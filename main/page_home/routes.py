from flask import render_template
from . import home_page
from ..models import Item

@home_page.route('/')
def index():
    items = Item.query.order_by(Item.auction_end.asc()).all()
    return render_template('home.html', items=items)
