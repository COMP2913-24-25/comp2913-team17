from flask import Flask, render_template

app = Flask(__name__)

# Import the routes
from .admin_page import admin_page 
from .bidding_page import bidding_page
from .home_page import home_page
from .item_page import item_page
from .user_page import user_page

# Register the blueprints
app.register_blueprint(admin_page, url_prefix='/admin')
app.register_blueprint(bidding_page, url_prefix='/bidding')
app.register_blueprint(home_page, url_prefix='/home')
app.register_blueprint(item_page, url_prefix='/item')
app.register_blueprint(user_page, url_prefix='/user')

# Define the main route
@app.route('/')
def main():
    return render_template('home.html')