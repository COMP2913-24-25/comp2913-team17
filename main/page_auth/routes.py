"""Authentication related routes."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from . import auth_page
from .forms import LoginForm, RegisterForm
from ..models import db, User

@auth_page.route('/login', methods=['GET', 'POST'])
def login():
    """Render the login page and handle login requests."""
    next_page = request.args.get('next')

    # Check for malicious redirects
    if not next_page or urlparse(next_page).netloc != "":
        next_page = url_for('home_page.index')

    if current_user.is_authenticated:
        return redirect(next_page)

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.query(User).filter_by(email=email).first()

        if user is None:
            flash('Invalid email address')
        elif not user.check_password(password):
            flash('Invalid password')
        else:
            login_user(user)
            return redirect(next_page)
    return render_template('login.html', form=form)


@auth_page.route('/register', methods=['GET', 'POST'])
def register():
    """Render the register page and handle registration requests."""
    if current_user.is_authenticated:
        return redirect(url_for('home_page.index'))

    form = RegisterForm()
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


@auth_page.route('/logout')
def logout():
    """Log the user out."""
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('home_page.index'))
