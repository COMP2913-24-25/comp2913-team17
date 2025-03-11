"""Configures the Flask app."""

import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, join_room
from flask_apscheduler import APScheduler
from .models import db
from .init_db import populate_db

socketio = SocketIO()
scheduler = APScheduler()
mail = Mail()

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='static')

    # Load environment variables
    basedir = os.path.abspath(os.path.dirname(__file__))
    parentdir = os.path.dirname(basedir)
    load_dotenv(os.path.join(parentdir, '.env'))

    # Configure the secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Configure Stripe keys from the environment
    app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLISHABLE_KEY'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')

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
    app.config['AWS_REGION'] = os.environ.get('AWS_REGION')

    # Configure email settings for Flask-Mail
    app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USERNAME = os.environ.get('EMAIL_USER'),
        MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')
    )
    
    # Add BASE_URL for generating links in emails
    app.config['BASE_URL'] = os.environ.get('BASE_URL', '127.0.0.1:5000')
    
    # Initialize Mail
    mail.init_app(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.FileHandler("auction_system.log")  # File handler
        ]
    )

    # Initialise the WebSocket server
    socketio.init_app(app, cors_allowed_origins='*')

    # Initialise the scheduler
    scheduler.init_app(app)
    scheduler.api_enabled = True

    app.config.update(
        SCHEDULER_API_ENABLED=True,
    )

    # Check for ended auctions every minute
    @scheduler.task('interval', id='check_ended_auctions', seconds=60, misfire_grace_time=30)
    def check_ended_auctions_job():
        with app.app_context():
            from .page_item.routes import check_ended_auctions
            try:
                check_ended_auctions()
            except Exception as e:
                print(f'Error checking ended auctions: {str(e)}')

    scheduler.start()

    # Initialise the database
    db.init_app(app)

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
    from .page_authenticate_item import authenticate_item_page
    from .page_experts import expert_page
    from .page_managers import manager_page

    app.register_blueprint(home_page)
    app.register_blueprint(item_page, url_prefix='/item')
    app.register_blueprint(create_page, url_prefix='/create')
    app.register_blueprint(dashboard_page, url_prefix='/dashboard')
    app.register_blueprint(auth_page)
    app.register_blueprint(authenticate_item_page, url_prefix='/authenticate')
    app.register_blueprint(expert_page, url_prefix='/expert')
    app.register_blueprint(manager_page, url_prefix='/manager')

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return db.session.query(User).get(int(user_id))

    return app
