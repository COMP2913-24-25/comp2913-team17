"""Auction viewing routes."""

from flask import render_template
from . import item_page
from ..models import Item

@item_page.route('/<url>')
def index(url):
    item = item = Item.query.filter_by(url=url).first_or_404()
    return render_template('item.html', item=item)
