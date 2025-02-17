"""Contains the form input fields for user login."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    """Form for logging in."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField('Username', validators=[
                           DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[
        DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(),
                             Length(min=8, max=24, message='Password must be between 8 and 24 characters.')])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(),
                                     EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')
