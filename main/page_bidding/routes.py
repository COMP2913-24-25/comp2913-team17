from flask import render_template
from . import bidding_page

@bidding_page.route('/')
def index():
    return render_template('bidding.html')

# Add any additional routes here similar to the one above
