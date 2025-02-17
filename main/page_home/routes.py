from flask import render_template
from . import home_page

@home_page.route('/')
def index():
    return render_template('home.html')

# Add any additional routes here similar to the one above
