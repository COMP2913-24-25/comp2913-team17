"""Auction viewing routes."""

from app import socketio
from flask_socketio import join_room, leave_room
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import decimal
from . import item_page
from ..models import db, Item, Bid, User, Notification, AuthenticationRequest, logger


# SocketIO event handlers
@socketio.on('join')
def on_join(data):
    """User joins a specific auction."""
    if not current_user.is_authenticated:
        return
    room = data.get('item_url')
    if room:
        join_room(room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a specific auction."""
    room = data.get('item_url')
    if room:
        leave_room(room)


@item_page.route('/<url>')
def index(url):
    item = Item.query.filter_by(url=url).first_or_404()

    # Check authentication status
    authentication = AuthenticationRequest.query.filter_by(item_id=item.item_id).first()
    status = None
    if authentication:
        status = authentication.status
        expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None

    # Allow validated users access to the authentication page
    if not current_user.is_authenticated:
        is_allowed = False
    else:
        is_allowed = authentication and (
            current_user.role == 3
            or (expert and expert.expert_id == current_user.id and expert.status != 3)
            or authentication.requester_id == current_user.id
        )
    # Get all bids in descending order and suggested bid amount
    bids = item.bids[::-1]
    suggested_bid = item.highest_bid().bid_amount + decimal.Decimal('0.01') if item.highest_bid() else item.minimum_price + \
        decimal.Decimal('0.01')

    return render_template('item.html', item=item, authentication=status, is_allowed=is_allowed, suggested_bid=suggested_bid, bids=bids)

@item_page.route('/<url>/bid', methods=['POST'])
@login_required
def place_bid(url):
    try:
        item = Item.query.filter_by(url=url).first_or_404()
        
        # Check if auction is still open
        if datetime.now() > item.auction_end:
            return jsonify({'status': 'error', 'message': 'Auction has ended'}), 400
        
        data = request.get_json()
        bid_amount = decimal.Decimal(data.get('bid_amount', 0))
        
        # Check if bid is high enough
        highest_bid = item.highest_bid()
        if highest_bid and bid_amount <= highest_bid.bid_amount:
            return jsonify({'status': 'error', 'message': 'Bid must be higher than current bid'}), 400
        
        if not highest_bid and bid_amount < item.minimum_price:
            return jsonify({'status': 'error', 'message': 'Bid must be at least the minimum price'}), 400
        
        # Create new bid
        new_bid = Bid(
            item_id=item.item_id,
            bidder_id=current_user.id,
            bid_amount=bid_amount,
            bid_time=datetime.now()
        )
        db.session.add(new_bid)
        db.session.commit()
        
        # Notify previous highest bidder if exists
        if highest_bid and highest_bid.bidder_id != current_user.id:
            outbid_user = User.query.get(highest_bid.bidder_id)
            item.notify_outbid(outbid_user)
        
        # Emit real-time update to all clients in the auction room
        socketio.emit('bid_update', {
            'bid_amount': float(bid_amount),
            'bid_userid': current_user.id,
            'bid_username': current_user.username,
            'bid_time': datetime.now().strftime('%Y-%m-%d %H:%M')
        }, room=url)
        
        return jsonify({'status': 'success', 'message': 'Bid placed successfully'})
    
    except Exception as e:
        logger.error(f"Error in place_bid: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error placing bid: {str(e)}'}), 500

def check_ended_auctions():
    """Check for auctions that have ended but don't have a winner yet."""
    from ..models import Item
    finished_items = Item.query.filter(
        Item.auction_end <= datetime.now(),
        Item.winning_bid_id.is_(None)
    ).all()
    
    for item in finished_items:
        try:
            logger.info(f"Finalizing auction for item: {item.title}")
            item.finalise_auction()
        except Exception as e:
            logger.error(f"Error finalizing auction {item.item_id}: {e}")