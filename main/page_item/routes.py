from flask import render_template
from . import item_page

@item_page.route('/')
def index():
    return render_template('item.html')

# Add any additional routes here similar to the one above
