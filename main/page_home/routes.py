from flask import render_template, jsonify
from . import home_page
from ..models import Item

@home_page.route('/')
def index():
    items = Item.query.order_by(Item.auction_end.asc()).all()
    return render_template('home.html', items=items)

@home_page.route('/api/search')
def search_items():
    # This route isn't strictly needed for client-side search
    # But it's included in case you want to implement server-side search in the future
    items = Item.query.order_by(Item.auction_end.asc()).all()
    return jsonify([{
        'item_id': item.item_id,
        'title': item.title,
        'url': item.url
    } for item in items])