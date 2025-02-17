from flask import render_template
from . import dashboard_page

@dashboard_page.route('/')
def index():
    return render_template('dashboard.html')

# Add any additional routes here similar to the one above
