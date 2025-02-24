"""Auction viewing routes."""

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from . import item_page
from ..models import db, Item, Bid, User, Notification, AuthenticationRequest

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
            current_user.role == 3 or
            expert and expert.expert_id == current_user.id or
            authentication.requester_id == current_user.id
        )

    return render_template('item.html', item=item, authentication=status, is_allowed=is_allowed)

@item_page.route('/<url>/bid', methods=['POST'])
@login_required
def place_bid(url):
    item = Item.query.filter_by(url=url).first_or_404()
    
    # Check if auction is still active
    if datetime.now() >= item.auction_end:
        flash('This auction has ended.', 'error')
        return redirect(url_for('item_page.index', url=url))

    # Add error handling for placing bid
    try:
        # Get bid amount from form
        bid_amount = float(request.form.get('bid_amount'))
        
        # Get current highest bid
        current_highest = item.highest_bid()
        
        # Validate bid amount
        if current_highest and bid_amount <= current_highest.bid_amount:
            flash('Your bid must be higher than the current bid.', 'error')
            return redirect(url_for('item_page.index', url=url))
        
        if bid_amount < item.minimum_price:
            flash('Your bid must be at least the minimum price.', 'error')
            return redirect(url_for('item_page.index', url=url))

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
        flash('Your bid has been placed successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error placing bid. Please try again.', 'error')
        print(f"Error placing bid: {str(e)}")  # For debugging
        
    return redirect(url_for('item_page.index', url=url))

@item_page.route('/check-ended-auctions')
def check_ended_auctions():
    """Check for ended auctions and notify winners"""
    try:
        ended_items = Item.query.filter(
            Item.auction_end <= datetime.now(),
            Item.winning_bid_id.is_(None)  # Only process items without winners set
        ).all()
        
        for item in ended_items:
            highest_bid = item.highest_bid()
            if highest_bid:
                # Set winning bid
                item.winning_bid_id = highest_bid.bid_id
                # Send notifications
                item.notify_winner()  # In-app notification
                item.notify_winner_email()  # Email notification
                db.session.commit()
        
        return {'message': 'Ended auctions processed'}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error processing ended auctions: {str(e)}")
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
