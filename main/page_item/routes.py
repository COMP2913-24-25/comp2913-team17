"""Auction viewing routes."""
import stripe
from app import socketio
from flask_socketio import join_room, leave_room
from flask import flash, redirect, render_template, request, jsonify, url_for, current_app
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

    # Check authentication status and authentication info
    authentication = AuthenticationRequest.query.filter_by(item_id=item.item_id).first()
    status = None
    expert = None
    if authentication:
        status = authentication.status
        expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None

    if not current_user.is_authenticated:
        is_allowed = False
    else:
        is_allowed = authentication and (
            current_user.role == 3
            or (expert and expert.expert_id == current_user.id and expert.status != 3)
            or authentication.requester_id == current_user.id
        )
    bids = item.bids[::-1]
    suggested_bid = (item.highest_bid().bid_amount + decimal.Decimal('0.01')
                     if item.highest_bid() else item.minimum_price + decimal.Decimal('0.01'))
    
    is_auction_over = datetime.now() >= item.auction_end
    is_winner = False
    if current_user.is_authenticated and item.highest_bid() and item.highest_bid().bidder_id == current_user.id:
        is_winner = True
    # show_payment is true when auction is over, user is the winner, and the item is not yet paid (status != 3)
    show_payment = is_auction_over and is_winner and (item.status != 3)

    return render_template('item.html', item=item, authentication=status, is_allowed=is_allowed,
                           suggested_bid=suggested_bid, bids=bids, show_payment=show_payment, 
                           is_auction_over=is_auction_over)

@item_page.route('/<url>/bid', methods=['POST'])
@login_required
def place_bid(url):
    item = Item.query.filter_by(url=url).first_or_404()
    
    # Prevent the seller from bidding on their own auction.
    if current_user.id == item.seller_id:
        return jsonify({'error': 'You cannot bid on your own auction.'}), 403

    if datetime.now() >= item.auction_end:
        return jsonify({'error': 'This auction has ended.'}), 400

    try:
        bid_amount = float(request.json.get('bid_amount'))
        print(bid_amount)
        current_highest = item.highest_bid()

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

        new_bid = Bid(
            item_id=item.item_id,
            bidder_id=current_user.id,
            bid_amount=bid_amount,
            bid_time=datetime.now()
        )
        db.session.add(new_bid)
        db.session.commit()

        socketio.emit('bid_update', {
            'bid_userid': current_user.id,
            'bid_username': current_user.username,
            'bid_amount': bid_amount,
            'bid_time': new_bid.bid_time.strftime('%Y-%m-%d %H:%M')
        }, room=url)

        try:
            if current_highest and current_highest.bidder_id != current_user.id:
                previous_bidder = User.query.get(current_highest.bidder_id)
                item.notify_outbid(previous_bidder)
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")

        return jsonify({'status': 'success', 'message': 'Bid placed successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error placing bid: {str(e)}")
        return jsonify({'error': 'Error placing bid. Please try again.'}), 500


def check_ended_auctions():
    """Check for auctions that have ended but don't have a winner yet."""
    finished_items = Item.query.filter(
        Item.auction_end <= datetime.now(),
        Item.winning_bid_id.is_(None)
    ).all()
    for item in finished_items:
        try:
            logger.info(f"Finalising auction for item: {item.title}")
            # finalise_auction() should update item.status to 2 (won)
            item.finalise_auction()
            highest_bid = item.highest_bid()
            if highest_bid:
                socketio.emit('auction_ended', {
                    'winner': True,
                    'winning_bidder_id': highest_bid.bidder.id,
                    'winning_bidder_username': highest_bid.bidder.username,
                    'winning_bid_amount': float(highest_bid.bid_amount)
                }, room=item.url)
            else:
                socketio.emit('auction_ended', {'winner': False}, room=item.url)
        except Exception as e:
            logger.error(f"Error finalising auction {item.item_id}: {e}")

@item_page.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    try:
        notification_ids = request.json.get('ids', [])
        if not notification_ids:
            return jsonify({'status': 'success', 'message': 'No notifications to mark as read'})
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
    try:
        item = Item.query.filter_by(url=url).first_or_404()
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
    try:
        item = Item.query.filter_by(url=url).first_or_404()
        if item not in current_user.watched_items:
            return jsonify({'error': 'Not watching this auction'}), 400
        current_user.watched_items.remove(item)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unwatching item: {str(e)}")
        return jsonify({'error': 'Could not remove from watched items'}), 500

@item_page.route('/<url>/payment', methods=['GET'])
@login_required
def payment_page(url):
    item = Item.query.filter_by(url=url).first_or_404()
    is_auction_over = datetime.now() >= item.auction_end
    is_winner = current_user.is_authenticated and item.highest_bid() and item.highest_bid().bidder_id == current_user.id
    if not is_auction_over or not is_winner:
        flash("You are not authorised to access the payment page.", "danger")
        return redirect(url_for('item_page.index', url=url))
    return render_template('payment.html', item=item, stripe_publishable_key=current_app.config.get('STRIPE_PUBLISHABLE_KEY'))

@item_page.route('/<url>/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent(url):
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    item = Item.query.filter_by(url=url).first_or_404()
    amount = int(((item.highest_bid().bid_amount if item.highest_bid() else item.minimum_price) * 100))
    
    # Ensure the current user has an associated Stripe Customer
    if not current_user.stripe_customer_id:
        create_stripe_customer(current_user)
    
    try:
        # Create a PaymentIntent that:
        # • Enables automatic payment methods,
        # • Saves card details for future off-session payments by setting up payment_method_options,
        # • Attaches the PaymentIntent to the existing customer.
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='gbp',
            description=f"Payment for auction item {item.title}",
            automatic_payment_methods={'enabled': True},
            payment_method_options={
                'card': {
                    'setup_future_usage': 'off_session'
                }
            },
            setup_future_usage='off_session',
            customer=current_user.stripe_customer_id,
            metadata={"item_id": str(item.item_id)}
        )

        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@item_page.route('/<url>/mark-won', methods=['POST'])
@login_required
def mark_won(url):
    item = Item.query.filter_by(url=url).first_or_404()
    if datetime.now() < item.auction_end:
        return jsonify({'error': 'Auction is still active'}), 400
    if not item.highest_bid() or item.highest_bid().bidder_id != current_user.id:
        return jsonify({'error': 'You are not the winning bidder'}), 403
    item.locked = True
    item.status = 3  # Mark as paid
    db.session.commit()
    return jsonify({'status': 'success'})

# New route: after successful payment, redirect with a flash message.
@item_page.route('/<url>/redirect-after-payment')
@login_required
def redirect_after_payment(url):
    flash("Payment successful!", "success")
    return redirect(url_for('item_page.index', url=url))

def create_stripe_customer(user):
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    customer = stripe.Customer.create(
        email=user.email,
        name=user.username
    )
    user.stripe_customer_id = customer.id
    db.session.commit()
    return customer

@item_page.route('/<url>/set-default-payment-method', methods=['POST'])
@login_required
def set_default_payment_method(url):
    data = request.get_json()
    payment_method_id = data.get('payment_method_id')
    if not payment_method_id:
        return jsonify({'error': 'No payment method ID provided.'}), 400
    try:
        stripe.Customer.modify(
            current_user.stripe_customer_id,
            invoice_settings={'default_payment_method': payment_method_id}
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@item_page.route('/<url>/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session(url):
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    item = Item.query.filter_by(url=url).first_or_404()
    
    # Ensure the customer has an associated Stripe Customer
    if not current_user.stripe_customer_id:
        create_stripe_customer(current_user)
    
    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': item.title,
                    },
                    'unit_amount': int(((item.highest_bid().bid_amount if item.highest_bid() else item.minimum_price) * 100)),
                },
                'quantity': 1,
            }],
            success_url=url_for('item_page.redirect_after_payment', url=item.url, _external=True, _scheme='http'),
            cancel_url=url_for('item_page.index', url=item.url, _external=True, _scheme='http'),
            payment_intent_data={
                'setup_future_usage': 'off_session'
            },
            saved_payment_method_options={
                'payment_method_save': 'enabled'
            }
        )

        return jsonify({'checkoutUrl': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from ..extensions import csrf  # or "from main.extensions import csrf" depending on your structure

@item_page.route('/stripe-webhook', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    current_app.logger.info(f"Webhook payload: {payload}")
    current_app.logger.info(f"Stripe-Signature header: {sig_header}")

    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        current_app.logger.error("Invalid payload")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error("Invalid signature")
        return "Invalid signature", 400

    # Process event if verification passed...
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        item_id = session.get('metadata', {}).get('item_id')
        if item_id:
            item = Item.query.filter_by(item_id=item_id).first()
            if item:
                item.locked = True
                item.status = 3  # Mark as paid
                db.session.commit()
                current_app.logger.info(f"Item {item.title} marked as paid via webhook.")
    return "", 200
