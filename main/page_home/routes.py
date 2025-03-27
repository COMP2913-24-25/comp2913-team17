from flask import render_template, jsonify
from . import home_page
from ..models import Item, Category

@home_page.route('/')
def index():
    items = Item.query.order_by(Item.auction_completed.asc(), Item.auction_end.asc()).all()
    categories = Category.query.order_by(Category.name).all()
    category_names = [category.name.upper() for category in categories if category.name != 'Miscellaneous'] + ['TREASURES']

    return render_template('home.html', items=items, categories=categories, category_names=category_names)

@home_page.route('/api/search')
def search_items():
    # This route isnt neccesary for client-side search but it's included in case we implement server-side search
    items = Item.query.order_by(Item.auction_end.asc()).all()
    return jsonify([{
        'item_id': item.item_id,
        'title': item.title,
        'url': item.url
    } for item in items])