"""Authentication related routes."""

import secrets
import requests
from flask import render_template, redirect, url_for, flash, request, current_app, session, abort
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse, urlencode
from app import socketio
from flask_socketio import join_room
from datetime import datetime
from . import auth_page
from .forms import LoginForm, RegisterForm, UpdateForm
from ..models import db, User
from ..limiter_utils import limiter

# SocketIO notification rooms
@socketio.on('join_user')
def on_join(data):
    """User joins a their personal notification room."""
    if not current_user.is_authenticated:
        return
    room = data.get('user_key')
    if current_user.secret_key != room:
        return
    elif room:
        join_room(f'user_{room}')


# Apply stricter rate limits to login route
@auth_page.route('/login', methods=['GET', 'POST'])
@limiter.limit("100 per minute", methods=["POST"], error_message="Too many login attempts. Please try again later.")
@limiter.limit("100 per minute", key_func=lambda: request.form.get('email', ''), methods=["POST"], error_message="Too many login attempts for this account. Please try again later.")
def login():
    """Log the user in."""
    next_page = request.args.get('next')

    # Check for malicious redirects
    if not next_page or urlparse(next_page).netloc != "":
        next_page = url_for('home_page.index')

    if current_user.is_authenticated:
        return redirect(next_page)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists
        if not user:
            flash('This user account is not exist. Please create a new account.', 'danger')
            return render_template('login.html', form=form)
        
        # Check if account is locked
        if user.is_account_locked():
            remaining_time = (user.locked_until - datetime.now()).total_seconds() / 60
            flash(f'Account is temporarily locked. Try again in {int(remaining_time)} minutes.', 'danger')
            return render_template('login.html', form=form)
        
        # Validate password
        if user.check_password(form.password.data):
            # Reset failed attempts on successful login
            user.reset_login_attempts()
            db.session.commit()
            
            login_user(user)
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home_page.index'))
        else:
            # Increment failed attempts on unsuccessful login
            user.increment_login_attempts()
            db.session.commit()
            
            # Calculate and display remaining attempts
            max_attempts = 5  # This should match the threshold in User.increment_login_attempts
            remaining_attempts = max_attempts - user.failed_login_attempts
            
            if remaining_attempts > 0:
                flash(f'Failed login. {remaining_attempts} {"attempt" if remaining_attempts == 1 else "attempts"} remaining before your account is locked.', 'danger')
            else:
                flash('Your account has been locked due to multiple failed login attempts. Try again in 15 minutes.', 'danger')
    
    return render_template('login.html', form=form)


# Apply rate limits to registration
@auth_page.route('/register', methods=['GET', 'POST'])
@limiter.limit("100 per hour", methods=["POST"], error_message="Too many registration attempts. Please try again later.")
@limiter.limit("100 per day", methods=["POST"])
def register():
    """Render the register page and handle registration requests."""
    if current_user.is_authenticated:
        return redirect(url_for('home_page.index'))

    # Pre-fill the email field if it was provided in the query string
    form = RegisterForm()
    if request.args.get('email'):
        form.email.data = request.args['email']

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if db.session.query(User).filter_by(email=email).first():
            flash('Email already taken')
        elif db.session.query(User).filter_by(username=username).first():
            flash('Username already taken')
        else:
            user = User(username=username, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('home_page.index'))
    return render_template('register.html', form=form)


# Apply rate limits to user update
@auth_page.route('/update_user', methods=['GET', 'POST'])
@limiter.limit("100 per hour", methods=["POST"], error_message="Too many update attempts. Please try again later.")
def update_user():
    """Render the update page and update user details."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page.login'))

    form = UpdateForm()

    # Pre-fill the form with the current user's information on GET requests.
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        new_username = form.username.data
        new_email = form.email.data
        new_password = form.password.data

        # Check if the email is taken by another user.
        existing_email = db.session.query(User).filter(User.email == new_email, User.id != current_user.id).first()
        if existing_email:
            flash('Email already taken')
        # Check if the username is taken by another user.
        elif db.session.query(User).filter(User.username == new_username, User.id != current_user.id).first():
            flash('Username already taken')
        else:
            # Update current_user's details.
            current_user.username = new_username
            current_user.email = new_email

            # Update password if a new one was provided.
            if new_password:
                current_user.set_password(new_password)

            db.session.commit()
            flash('Details been updated')
            return redirect(url_for('home_page.index'))

    return render_template('update_user.html', form=form)


@auth_page.route('/logout')
def logout():
    """Log the user out."""
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('home_page.index'))


# Apply rate limits to OAuth2 authorization
@auth_page.route('/authorize/<provider>')
@limiter.limit("10 per hour")
def oauth2_authorise(provider):
    """Redirect the user to the OAuth2 provider authorisation URL."""
    if not current_user.is_anonymous:
        return redirect(url_for('home_page.index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # Generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('auth_page.oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': " ".join(provider_data['scopes']),
        'state': session['oauth2_state'],
        'prompt': 'select_account'
    })

    # Redirect the user to the OAuth2 provider authorisation URL
    return redirect(provider_data['authorize_url'] + "?" + qs)


# Apply rate limits to OAuth2 callback
@auth_page.route('/callback/<provider>')
@limiter.limit("10 per hour")
def oauth2_callback(provider):
    """Handle the OAuth2 provider callback."""
    if not current_user.is_anonymous:
        return redirect(url_for('home_page.index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # If there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('auth_page.login'))

    # Enure that the state parameter matches the one in the auth request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # Ensure that the auth code is present
    if 'code' not in request.args:
        abort(401)

    # Exchange the auth code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for("auth_page.oauth2_callback", provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # Use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    # Find the user in the database or redirect them to the registration page
    user = db.session.query(User).filter_by(email=email).first()
    if user is None:
        flash('You must register before using Google login')
        return redirect(url_for('auth_page.register', email=email))

    # Log the user in
    login_user(user)
    return redirect(url_for('home_page.index'))
