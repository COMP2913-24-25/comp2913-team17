"""Authentication related routes."""

import secrets
import requests
from flask import render_template, redirect, url_for, flash, request, current_app, session, abort
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse, urlencode
from main import socketio
from flask_socketio import join_room
from datetime import datetime
from . import auth_page
from .forms import LoginForm, RegisterForm, UpdateUsernameForm, UpdateEmailForm, UpdatePasswordForm
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
            flash('This user account does not exist. Please create a new account.', 'warning')
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

            # Log in and store current password version in session
            login_user(user)
            session['password_version'] = user.password_version
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home_page.index'))
        else:
            # Increment failed attempts on unsuccessful login
            user.increment_login_attempts()
            db.session.commit()

            # Calculate and display remaining attempts
            max_attempts = 5
            remaining_attempts = max_attempts - user.failed_login_attempts

            if remaining_attempts > 0:
                flash(
                    f'Failed login. {remaining_attempts} {"attempt" if remaining_attempts == 1 else "attempts"} remaining before your account is locked.', 'danger')
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
    if request.method == 'GET' and request.args.get('email'):
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

            # Initialise welcome notificaition to a new user
            user.send_welcome_notification()

            login_user(user)
            return redirect(url_for('home_page.index'))
    return render_template('register.html', form=form)

@auth_page.route('/update-user', methods=['GET', 'POST'])
@limiter.limit("100 per hour", methods=["POST"], error_message="Too many update attempts. Please try again later.")
def update_user():
    """Render the update page and update user details."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth_page.login'))

    update_username_form = UpdateUsernameForm()
    update_email_form = UpdateEmailForm()
    update_password_form = UpdatePasswordForm()

    # Mask current email before rendering the template
    email = current_user.email
    mask_start, domain = email.split('@')
    if len(mask_start) > 2:
        masked_email = mask_start[0] + '*' * (len(mask_start) - 2) + mask_start[-1] + '@' + domain
    else:
        masked_email = '*' * (len(mask_start)) + '@' + domain

    # Check which form was submitted by checking the submit button
    if request.method == 'POST':
        form_name = request.form.get('submit', '')

        # Handle Username Update
        if 'Update Username' in form_name and update_username_form.validate_on_submit():
            current_password = update_username_form.current_password.data
            new_username = update_username_form.new_username.data

            # Check 1 - Wrong password
            if not current_user.check_password(current_password):
                flash("Incorrect current password", "danger")
            # Check 2 - Username is the same as current username
            elif new_username == current_user.username:
                flash('New username must be different to the current username', 'danger')
            # Check 3 - Username already taken
            elif db.session.query(User).filter(User.username == new_username, User.id != current_user.id).first():
                flash('Username already taken', 'danger')
            else:
                current_user.username = new_username
                db.session.commit()
                flash('Username updated successfully', 'success')
                return redirect(url_for('auth_page.update_user'))

        # Handle Email Update
        elif 'Update Email' in form_name:
            if update_email_form.validate_on_submit():
                current_password = update_email_form.current_password.data
                new_email = update_email_form.new_email.data

                # Check 1 - Wrong password
                if not current_user.check_password(current_password):
                    flash("Incorrect current password", "danger")
                # Check 2 - Email is the same as current email
                elif new_email == current_user.email:
                    flash('New email must be different to current email', 'danger')
                # Check 3 - Email already taken
                elif db.session.query(User).filter(User.email == new_email, User.id != current_user.id).first():
                    flash('Email already taken', 'danger')
                else:
                    # Update the email
                    current_user.email = new_email
                    db.session.commit()
                    flash('Email updated successfully', 'success')
                    return redirect(url_for('auth_page.update_user'))

        # Handle Password Update
        elif 'Update Password' in form_name:
            if update_password_form.validate_on_submit():
                current_password = update_password_form.current_password.data
                new_password = update_password_form.new_password.data
                confirm_password = update_password_form.confirm_password.data

                # Check 1 - Wrong password
                if not current_user.check_password(current_password):
                    flash("Incorrect current password", "danger")
                # Check 2 - New password is the same as current password
                elif current_user.check_password(new_password):
                    flash('New password must be different to your current password', 'danger')
                # Check 3 - Passwords don't match
                elif new_password != confirm_password:
                    flash('Passwords do not match', 'danger')
                else:
                    # Update the password
                    current_user.set_password(new_password)
                    db.session.commit()

                    logout_user()
                    flash('Password updated successfully. Please log in with your updated password.', 'info')

                    return redirect(url_for('auth_page.login'))

    return render_template(
        'update_user.html',
        update_username_form=update_username_form,
        update_email_form=update_email_form,
        update_password_form=update_password_form,
        masked_email=masked_email)

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

    # Check if account is locked
    if user.is_account_locked():
        form = LoginForm()
        remaining_time = (user.locked_until - datetime.now()).total_seconds() / 60
        flash(f'Account is temporarily locked. Try again in {int(remaining_time)} minutes.', 'danger')
        return render_template('login.html', form=form)

    # Log the user in and reset their login attempts
    user.reset_login_attempts()
    db.session.commit()
    login_user(user)
    session['password_version'] = user.password_version
    return redirect(url_for('home_page.index'))
