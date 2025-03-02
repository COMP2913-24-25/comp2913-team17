"""Configures the Flask app."""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from .models import db
from .init_db import populate_db
from .socket_events import init_socketio, socketio

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static')

    # Load environment variables
    basedir = os.path.abspath(os.path.dirname(__file__))
    parentdir = os.path.dirname(basedir)
    load_dotenv(os.path.join(parentdir, '.env'))

    # Configure the secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise security features
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth_page.login'
    login_manager.login_message = 'Please log in to access this page'

    # Configure OAuth2 providers
    app.config['OAUTH2_PROVIDERS'] = {
        # Google OAuth 2.0 documentation:
        # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
        'google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'token_url': 'https://accounts.google.com/o/oauth2/token',
            'userinfo': {
                'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'email': lambda json: json["email"],
            },
            'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
        }
    }

    # Configure AWS S3
    app.config['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY')
    app.config['AWS_SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY')
    app.config['AWS_BUCKET'] = os.environ.get('AWS_BUCKET')

    # Configure email settings for Flask-Mail
    app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USERNAME = os.environ.get('EMAIL_USER'),
        MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    )
    
    mail = Mail(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.FileHandler("auction_system.log")  # File handler
        ]
    )

    # Initialise the database
    db.init_app(app)

    # Initialize SocketIO
    init_socketio(app)

    with app.app_context():
        # Creates tables if they don't exist
        db.create_all()
        # Populate dummy data if it doesn't already exist
        populate_db(app)

    # Import and registers the blueprints
    from .page_home import home_page
    from .page_item import item_page
    from .page_create import create_page
    from .page_dashboard import dashboard_page
    from .page_auth import auth_page

    app.register_blueprint(home_page)
    app.register_blueprint(item_page, url_prefix='/item')
    app.register_blueprint(create_page, url_prefix='/create')
    app.register_blueprint(dashboard_page, url_prefix='/dashboard')
    app.register_blueprint(auth_page)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return db.session.query(User).get(int(user_id))

    return app
