"""Configures the Flask app."""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_apscheduler import APScheduler
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from .models import db
from .init_db import populate_db
from .limiter_utils import configure_limiter
from .extensions import csrf
from .db_utils import reset_database

socketio = SocketIO()
scheduler = None
mail = Mail()

def create_app(testing=False, database_path='database.db'):
    """Creates and configures the Flask app."""
    global scheduler

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
    app.config['STRIPE_WEBHOOK_SECRET'] = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # Configure the database based on environment
    if os.environ.get('DATABASE_URL'):
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

        # Set NullPool for PostgreSQL to avoid threading issues with Gunicorn
        from sqlalchemy.pool import NullPool
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': NullPool,
            'connect_args': {}
        }
    elif not testing:
        # Local SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    else:
        # Testing SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, database_path)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Set the SQLAlchemy engine options per environment
    if os.environ.get('RENDER') != 'true':
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                # Seconds to wait if db is locked
                'timeout': 30
            },
            'pool_recycle': 120,
            'pool_pre_ping': True
        }
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 120,
        'pool_pre_ping': True
    }

    # Initialise security features
    csrf.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth_page.login'
    login_manager.login_message = 'Please log in to access this page'

    # Set session life to 1 hour of inactivity
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

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
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get('EMAIL_USER'),
        MAIL_PASSWORD=os.environ.get('EMAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.environ.get('EMAIL_USER')
    )

    # Add BASE_URL for generating links in emails
    app.config['BASE_URL'] = os.environ.get('BASE_URL', '127.0.0.1:5000/')
    
    # Initialise Mail
    mail.init_app(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # Set max logfile size to 5MB and keep up to 3 backups
            RotatingFileHandler(
                "auction_system.log", 
                maxBytes=1024 * 1024 * 5,
                backupCount=3
            )
        ]
    )

    # Initialise the WebSocket server
    socketio.init_app(app, cors_allowed_origins='*')

    # Initialise the scheduler
    if not testing and scheduler is None:
        if os.environ.get('RENDER') != 'true' or os.environ.get('RENDER_SERVICE_TYPE') == 'web':
            scheduler = APScheduler()
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
        if os.environ.get('RENDER') == 'true':
            # If running on Render, reset the database completely
            reset_database(app, db)
        else:
            # Empty the database if required
            if os.environ.get('EMPTY_DB'):
                db.drop_all()
                db.create_all()
            # Otherwise, populate dummy data if it doesn't already exist
            else:
                db.create_all()
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
    from .page_addons import addons_page

    app.register_blueprint(home_page)
    app.register_blueprint(item_page, url_prefix='/item')
    app.register_blueprint(create_page, url_prefix='/create')
    app.register_blueprint(dashboard_page, url_prefix='/dashboard')
    app.register_blueprint(auth_page)
    app.register_blueprint(authenticate_item_page, url_prefix='/authenticate')
    app.register_blueprint(expert_page, url_prefix='/expert')
    app.register_blueprint(manager_page, url_prefix='/manager')
    app.register_blueprint(addons_page)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return db.session.get(User, int(user_id))
    
    # Checks if the password has been changed and forces a logout if so
    @app.before_request
    def check_password_version():
        from flask_login import current_user, logout_user
        from flask import session, redirect, url_for, flash

        session.permanent = True

        if current_user.is_authenticated:
            password_version = session.get('password_version')
            if password_version is None:
                # Set initial version
                session['password_version'] = current_user.password_version
            elif password_version != current_user.password_version:
                # Password changed, force logout
                logout_user()
                flash('Your password has been changed. Please log in again.', 'info')
                return redirect(url_for('auth_page.login'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Initialise rate limiter
    configure_limiter(app)

    # Send pending notifications on startup
    with app.app_context():
        from .page_item.routes import check_ended_auctions
        try:
            check_ended_auctions()
        except Exception as e:
            print(f'Error checking ended auctions on startup: {str(e)}')

    return app
