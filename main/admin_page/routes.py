from flask import render_template
from . import admin_page

@admin_page.route('/')
def index():
    return render_template('admin.html')

# Add any additional routes here similar to the one above
