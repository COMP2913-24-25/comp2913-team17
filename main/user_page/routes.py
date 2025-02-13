from flask import render_template
from . import user_page

@user_page.route('/')
def index():
    return render_template('user.html')

# Add any additional routes here similar to the one above
