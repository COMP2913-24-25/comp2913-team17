"""Configures the Flask app."""

import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .models import db
from .init_db import populate_db

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
