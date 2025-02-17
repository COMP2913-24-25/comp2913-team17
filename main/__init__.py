import os
from flask import Flask, render_template
from .models import db
from .init_db import populate_db

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sacrebleu'

    # This configuers the database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialises the database
    db.init_app(app)

    with app.app_context():
        # Creates tables if they don't exist
        db.create_all()
        # Populate dummy data if it doesn't already exist
        populate_db(app)

    # Import and registers the blueprints
    from .admin_page import admin_page
    from .bidding_page import bidding_page
    from .home_page import home_page
    from .item_page import item_page
    from .user_page import user_page

    app.register_blueprint(admin_page, url_prefix='/admin')
    app.register_blueprint(bidding_page, url_prefix='/bidding')
    app.register_blueprint(home_page, url_prefix='/home')
    app.register_blueprint(item_page, url_prefix='/item')
    app.register_blueprint(user_page, url_prefix='/user')

    # Defines the main route
    @app.route('/')
    def main():
        return render_template('home.html')

    return app
