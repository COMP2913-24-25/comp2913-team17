"""Auction viewing routes."""

from app import socketio
from flask_socketio import join_room, leave_room
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import decimal
from . import item_page
from ..models import db, Item, Bid, User, AuthenticationRequest, logger, Notification


# SocketIO event handlers
@socketio.on('join_auction')
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
    item = Item.query.filter_by(url=url).first_or_404()

    # Check if auction is still active
    if datetime.now() >= item.auction_end:
        return jsonify({'error': 'This auction has ended.'}), 400

    # Error handling for placing bid
    try:
        # Get bid amount from form
        bid_amount = float(request.json.get('bid_amount'))
        print(bid_amount)

        # Get current highest bid
        current_highest = item.highest_bid()

        # Validate bid amount
        if not bid_amount:
            return jsonify({'error': 'Please enter a bid amount.'}), 400

        if not isinstance(bid_amount, (int, float)):
            return jsonify({'error': 'Bid amount must be a number.'}), 400

        if bid_amount < 0:
            return jsonify({'error': 'Bid amount must be a positive number.'}), 400

        if current_highest and bid_amount <= current_highest.bid_amount:
            return jsonify({'error': 'Your bid must be higher than the current bid.'}), 400

        if bid_amount < item.minimum_price:
            return jsonify({'error': 'Your bid must be at least the minimum price.'}), 400

        # Create new bid
        new_bid = Bid(
            item_id=item.item_id,
            bidder_id=current_user.id,
            bid_amount=bid_amount,
            bid_time=datetime.now()
        )
        db.session.add(new_bid)
        db.session.commit()

        # Notify all users in the auction room
        socketio.emit('bid_update', {
            'bid_userid': current_user.id,
            'bid_username': current_user.username,
            'bid_amount': bid_amount,
            'bid_time': new_bid.bid_time.strftime('%Y-%m-%d %H:%M')
        }, room=url)

        # Notify previous highest bidder that they were outbid
        try:
            if current_highest and current_highest.bidder_id != current_user.id:
                previous_bidder = User.query.get(current_highest.bidder_id)
                item.notify_outbid(previous_bidder)
        # Notification errors don't affect the bid placement
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")

        return jsonify({'status': 'success', 'message': 'Bid placed successfully'})

    except Exception as e:
        db.session.rollback()
        print(f"Error placing bid: {str(e)}")  # For debugging
        return jsonify({'error': 'Error placing bid. Please try again.'}), 500


def check_ended_auctions():
    """Check for auctions that have ended but don't have a winner yet."""
    finished_items = Item.query.filter(
        Item.auction_end <= datetime.now(),
        Item.winning_bid_id.is_(None)
    ).all()

    for item in finished_items:
        try:
            logger.info(f"Finalizing auction for item: {item.title}")
            item.finalise_auction()

            highest_bid = item.highest_bid()

            # Disconnects all users from the auction room
            if highest_bid:
                socketio.emit('auction_ended', {
                    'winner': True,
                    'winning_bidder_id': highest_bid.bidder.id,
                    'winning_bidder_username': highest_bid.bidder.username,
                    'winning_bid_amount': float(highest_bid.bid_amount)
                }, room=item.url)
            else:
                socketio.emit('auction_ended', {
                    'winner': False
                }, room=item.url)
        except Exception as e:
            logger.error(f"Error finalizing auction {item.item_id}: {e}")


@item_page.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    try:
        # Get notification IDs from the request
        notification_ids = request.json.get('ids', [])
        
        if not notification_ids:
            return jsonify({'status': 'success', 'message': 'No notifications to mark as read'})
        
        # Mark specified notifications as read
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user.id
        ).all()
        
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error marking specific notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500


@item_page.route('/<url>/watch', methods=['POST'])
@login_required
def watch_item(url):
    """Add an item to the user's watched items."""
    try:
        item = Item.query.filter_by(url=url).first_or_404()
        
        # Check if already watching
        if item in current_user.watched_items:
            return jsonify({'error': 'Already watching this auction'}), 400
            
        current_user.watched_items.append(item)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error watching item: {str(e)}")
        return jsonify({'error': 'Could not add to watched items'}), 500


@item_page.route('/<url>/unwatch', methods=['POST'])
@login_required
def unwatch_item(url):
    """Remove an item from the user's watched items."""
    try:
        item = Item.query.filter_by(url=url).first_or_404()
        
        # Check if actually watching
        if item not in current_user.watched_items:
            return jsonify({'error': 'Not watching this auction'}), 400
            
        current_user.watched_items.remove(item)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unwatching item: {str(e)}")
        return jsonify({'error': 'Could not remove from watched items'}), 500