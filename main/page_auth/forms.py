"""Contains the form input fields for user login."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional


class LoginForm(FlaskForm):
    """Form for logging in."""
    email = StringField('Email', validators=[
                        DataRequired(), Email(), Length(max=50)])
    # Login doesn't require restrictions on password length or complexity
    # since it's being used on UpdateForm and RegisterForm
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=16)])
    email = StringField('Email', validators=[
                        DataRequired(),Email(),Length(max=50)])
    password = PasswordField('Password', validators=[
                             DataRequired(),
                             Length(min=8, max=24, message='Password must be between 8 and 24 characters.'),
                             Regexp(regex='^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]).+$', 
                                    message='Password must have at least one uppercase letter, one number, and one special character')])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(),
                                     EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')


class UpdateForm(FlaskForm):
    """Form for updating a new user."""
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=16)])
    email = StringField('Email', validators=[
                            DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[
                             Optional(),
                             Length(min=8, max=24, message='Password must be between 8 and 24 characters.'),
                             Regexp(regex='^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]).+$',
                                    message='Password must have at least one uppercase letter, one number, and one special character')])
    confirm_password = PasswordField('Confirm Password', validators=[
                                    Optional(),
                                     EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Update')
