"""Auction viewing routes."""

from flask import render_template
from . import item_page
from ..models import Item

@item_page.route('/<url>')
def index(url):
    item = item = Item.query.filter_by(url=url).first_or_404()
    return render_template('item.html', item=item)

from flask_socketio import emit
from flask import request, jsonify
from flask_login import login_required, current_user
from ..models import db, Bid, Item
from . import item_page
from main import socketio

@item_page.route('/bid', methods=['POST'])
@login_required
def place_bid():
    """Handles placing a new bid on an auction item."""
    data = request.get_json()
    item_id = data.get('item_id')
    bid_amount = data.get('bid_amount')

    if not item_id or not bid_amount:
        return jsonify({"error": "Invalid request"}), 400

    response, status = Bid.place_bid(item_id, current_user.id, bid_amount)
    
    if status == 200:
        # Emit event to update all clients
        socketio.emit('update_bid', {"item_id": item_id, "bid_amount": bid_amount}, broadcast=True)

    return jsonify(response), status

