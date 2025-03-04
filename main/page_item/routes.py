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
        expert = authentication.expert_assignments[0] if authentication.expert_assignments else None

    # Allow validated users access to the authentication page
    if not current_user.is_authenticated:
        is_allowed = False
    else:
        is_allowed = authentication and (
            current_user.role == 3
            or expert and expert.expert_id == current_user.id
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

    # Add error handling for placing bid
    try:
        # Get bid amount from form
        bid_amount = float(request.json.get('bid_amount'))

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
            bid_amount=bid_amount
        )
        db.session.add(new_bid)

        # Notify previous highest bidder that they were outbid
        if current_highest and current_highest.bidder_id != current_user.id:
            previous_bidder = User.query.get(current_highest.bidder_id)
            if previous_bidder:  # Make sure we found the user
                item.notify_outbid(previous_bidder)

        db.session.commit()

        # Notify all users in the auction room
        socketio.emit('bid_update', {
            'item_url': url,
            'bid_userid': current_user.id,
            'bid_username': current_user.username,
            'bid_amount': bid_amount,
            'bid_time': new_bid.bid_time.strftime('%Y-%m-%d %H:%M')
        }, room=url)

        return jsonify({'success': 'Your bid has been placed successfully!'})

    except Exception as e:
        db.session.rollback()
        print(f"Error placing bid: {str(e)}")  # For debugging
        return jsonify({'error': 'Error placing bid. Please try again.'}), 500


@item_page.route('/check-ended-auctions')
def check_ended_auctions():
    """Check for ended auctions and notify winners"""
    try:
        ended_items = Item.query.filter(
            Item.auction_end <= datetime.now(),
            Item.winning_bid_id.is_(None)  # Only process items without winners set
        ).all()

        logger.info(f"Found {len(ended_items)} ended auctions to process")

        for item in ended_items:
            highest_bid = item.highest_bid()
            if highest_bid:
                # Set winning bid
                item.winning_bid_id = highest_bid.bid_id
                
                # Send notifications - To implement
                # item.notify_winner()  # In-app notification
                # item.notify_winner_email()  # Email notification

                db.session.commit()

                # Disconnects all users from the auction room
                socketio.emit('auction_ended', {
                    'item_url': item.url,
                    'winner': True,
                    'winning_bidder_id': highest_bid.bidder.id,
                    'winning_bidder_username': highest_bid.bidder.username,
                    'winning_bid_amount': float(highest_bid.bid_amount)
                }, room=item.url)
            else:
                socketio.emit('auction_ended', {
                    'item_url': item.url,
                    'winner': False
                }, room=item.url)
                
        return {'message': 'Ended auctions processed'}, 200
    except Exception as e:
        logger.error(f"Error processing ended auctions: {str(e)}")
        return {'error': 'Failed to process ended auctions'}, 500


@item_page.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Mark all notifications as read for current user"""
    try:
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()

        for notification in notifications:
            notification.is_read = True

        db.session.commit()
        return {'status': 'success'}, 200
    except Exception as e:
        print(f"Error marking notifications read: {str(e)}")
        return {'error': 'Failed to mark notifications as read'}, 500
