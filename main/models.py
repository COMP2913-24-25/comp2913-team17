import logging
from calendar import c
from datetime import datetime, timedelta
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from .email_utils import send_notification_email
from .s3_utils import init_s3

db = SQLAlchemy()
logger = logging.getLogger(__name__)

# ---------------------------
# Models
# ---------------------------

# Table for watched items
user_watched_items = db.Table('user_watched_items',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('items.item_id'))
)

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    secret_key = db.Column(db.String(32), unique=True,
                    default=lambda: uuid4().hex, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Roles: 1 = General User, 2 = Expert, 3 = Manager
    role = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime,
                           default=datetime.now(),
                           onupdate=datetime.now())
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # NEW, Stripe Customer ID field for saving card details securely on Stripe
    stripe_customer_id = db.Column(db.String(255), nullable=True)

    # Relationships to other tables:
    items = db.relationship('Item', 
                          backref='seller',
                          lazy=True,
                          foreign_keys='Item.seller_id')
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    authentication_requests = db.relationship('AuthenticationRequest', backref='requester', lazy=True)
    expert_assignments = db.relationship('ExpertAssignment', backref='expert', lazy=True)
    expert_availabilities = db.relationship('ExpertAvailability', backref='expert', lazy=True)
    messages_sent = db.relationship('Message', backref='sender', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    watched_items = db.relationship('Item', secondary=user_watched_items, 
                                   backref=db.backref('watchers', lazy='dynamic'),
                                   lazy='dynamic')

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        # Set the password for the user
        self.password_hash = generate_password_hash(password, method="pbkdf2")

    def check_password(self, password):
        # Check the password for the user
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_account_locked(self):
        # Check if the account is currently locked
        return self.locked_until is not None and self.locked_until > datetime.now()
    
    def increment_login_attempts(self):
        # Increment failed login attempts and lock account if threshold reached
        self.failed_login_attempts += 1
        # Lock after 5 failed attempts
        if self.failed_login_attempts >= 5:
            # Lock for 15 minutes
            self.locked_until = datetime.now() + timedelta(minutes=15)
    
    def reset_login_attempts(self):
        # Reset the failed login attempts counter and unlock account
        self.failed_login_attempts = 0
        self.locked_until = None

    # Grab the user's winning items from the database
    def get_won_items(self):
        # Get items won by the winner
        return Item.query.join(Bid).filter(Item.winning_bid_id == Bid.bid_id).filter(Bid.bidder_id == self.id).all()

    # Schedule a task to automate checking and finalising auctions that have ended
    def schedule_auction_finalisation(self):
        # Check for finished auctions and set the winner
        finished_items = Item.query.filter(Item.auction_end <= datetime.now(),
                                           Item.winning_bid_id.is_(None)).all()
        for item in finished_items:
            item.finalise_auction()

    # Send a welcome notification to a new user
    def send_welcome_notification(self):
        notification = Notification(
            user_id=self.id,
            message=f"Welcome to Vintage Vault, {self.username}! Get started by browsing auctions or creating your own.",
            notification_type=0
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send welcome notification
        try:
            from app import socketio
            socketio.emit('new_notification', {
                'id': notification.id,
                'message': notification.message,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{self.secret_key}')
        except Exception as e:
            logger.error(f"Failed to send welcome notification: {e}")
            
        # Send welcome email
        try:
            send_notification_email(self, notification)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
        
        return notification

# Item Model
class Item(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # New field for category support
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    url = db.Column(db.String(32), unique=True,
                    default=lambda: uuid4().hex, nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now())
    auction_start = db.Column(db.DateTime, nullable=False)
    auction_end = db.Column(db.DateTime, nullable=False)
    minimum_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.01)
    locked = db.Column(db.Boolean, default=False)
    # Allow for items to end without a winner
    auction_completed = db.Column(db.Boolean, default=False)
    # Statuses: 1 = Open, 2 = Won, 3 = Paid
    status = db.Column(db.Integer, nullable=False, default=1)
    # ensures all images are deleted
    images = db.relationship('Image', back_populates='item', cascade='all, delete-orphan')
    # Store the fee per item
    base_fee = db.Column(db.Numeric(10, 2), nullable=False, default=1.00)
    auth_fee = db.Column(db.Numeric(10, 2), nullable=False, default=5.00)

    winning_bid_id = db.Column(
        db.Integer, 
        db.ForeignKey('bids.bid_id', use_alter=True, name='fk_winning_bid'),
        nullable=True
    )
    winning_bid = db.relationship(
        'Bid',
        foreign_keys=[winning_bid_id],
        uselist=False,
        post_update=True
    )
    bids = db.relationship(
        'Bid', 
        backref='item', 
        lazy=True, 
        foreign_keys='Bid.item_id',
        primaryjoin="Item.item_id==Bid.item_id"
    )
    authentication_requests = db.relationship('AuthenticationRequest', backref='item', lazy=True)

    def __init__(self, **kwargs):
        """Initialise the item and set the fees"""
        super().__init__(**kwargs)
        self.set_fees()

    def set_fees(self):
        """Set fees from the ManagerConfig if available"""
        from .models import ManagerConfig

        # Set unathenticated item fee
        base_config = ManagerConfig.query.filter_by(config_key=ManagerConfig.BASE_FEE_KEY).first()
        if base_config:
            self.base_fee = float(base_config.config_value)
        else:
            self.base_fee = 1.00
            
        # Set authenticated item fee
        auth_config = ManagerConfig.query.filter_by(config_key=ManagerConfig.AUTHENTICATED_FEE_KEY).first()
        if auth_config:
            self.auth_fee = float(auth_config.config_value)
        else:
            self.auth_fee = 5.00
    
    def __repr__(self):
        return f"<Item {self.title} (ID: {self.item_id})>"
    
    def highest_bid(self):
        if not self.bids:
            return None
        return max(self.bids, key=lambda bid: bid.bid_amount)
    
    def user_highest_bid(self, user_id):
        """Get the highest bid for a specific user on this item."""
        user_bids = [bid for bid in self.bids if bid.bidder_id == user_id]
        if not user_bids:
            return None
        return max(user_bids, key=lambda bid: bid.bid_amount)
    
    # Send notification to the outbid user
    def notify_outbid(self, user):
        notification = Notification(
            user_id=user.id,
            message=f"You have been outbid on '{self.title}'",
            item_url=self.url,
            item_title=self.title,
            notification_type=1
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        try:
            from main import socketio
            socketio.emit('new_notification', {
                'id': notification.id,
                'message': notification.message,
                'item_url': notification.item_url, 
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{user.secret_key}')
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            
        # Send email
        send_notification_email(user, notification)

    # Send notification to the winner
    def notify_winner(self):
        if not self.winning_bid:
            return
        
        winner = User.query.get(self.winning_bid.bidder_id)
        notification = Notification(
            user_id=winner.id,
            message=f"Congratulations! You won the auction for '{self.title}'",
            item_url=self.url,
            item_title=self.title,
            notification_type=2
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        try:
            from main import socketio
            socketio.emit('new_notification', {
                'id': notification.id,
                'message': notification.message,
                'item_url': notification.item_url,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{winner.secret_key}')
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
        
        # Send email
        send_notification_email(winner, notification)

    # Send notification to the losers
    def notify_losers(self):
        if not self.winning_bid:
            return
            
        # Get unique bidders excluding winner
        bidders = set()
        for bid in self.bids:
            if bid.bidder_id != self.winning_bid.bidder_id:
                bidders.add(bid.bidder_id)
        
        for bidder_id in bidders:
            bidder = User.query.get(bidder_id)
            notification = Notification(
                user_id=bidder.id,
                message=f"The auction for '{self.title}' has ended. Unfortunately, you didn't win.",
                item_url=self.url,
                item_title=self.title,
                notification_type=3
            )
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification
            try:
                from main import socketio
                socketio.emit('new_notification', {
                    'id': notification.id,
                    'message': notification.message,
                    'item_url': notification.item_url,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
                }, room=f'user_{bidder.secret_key}')
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")

    # Set the winning bid and notify users about the auction outcome
    def finalise_auction(self):
        highest = self.highest_bid()
        if highest:
            self.winning_bid_id = highest.bid_id
            self.status = 2  # Auction is won (but not yet paid)
            db.session.commit()
            # Notify winner and losers
            self.notify_winner()
            self.notify_losers()
        
        # Notify the seller if the auction has bid or not
        self.notify_seller()

    # Notify the seller
    def notify_seller(self):
        if self.winning_bid:
            message = f"Your auction for '{self.title}' has ended. The item was sold to {self.winning_bid.bidder.username} for £{self.winning_bid.bid_amount}."
            notification_type = 5
        else:
            message = f"Your auction for '{self.title}' has ended without any bids."
            notification_type = 6
        
        # Create and save the notification
        notification = Notification(
            user_id=self.seller_id,
            message=message,
            item_url=self.url,
            item_title=self.title,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        try:
            from main import socketio
            socketio.emit('new_notification', {
                'message': notification.message,
                'item_url': notification.item_url,
                'id': notification.id,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{self.seller.secret_key}')
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

        send_notification_email(self.seller, notification)

    def notify_payment(self):
        if not self.winning_bid:
            return

        try:
            seller = User.query.get(self.seller_id)
            if not seller:
                logger.error(f"Failed to find seller with ID {self.seller_id} for payment notification")
                return
                
            # Create notification
            notification = Notification(
                user_id=seller.id,
                message=f"Payment received! {self.winning_bid.bidder.username} has paid £{self.winning_bid.bid_amount} for '{self.title}'.",
                item_url=self.url,
                item_title=self.title,
                notification_type=7
            )
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification
            try:
                from app import socketio
                socketio.emit('new_notification', {
                    'id': notification.id,
                    'message': notification.message,
                    'item_url': notification.item_url,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
                }, room=f'user_{seller.secret_key}')
                logger.info(f"Sent payment notification to seller {seller.username} (ID: {seller.id})")
            except Exception as e:
                logger.error(f"Failed to send real-time payment notification to seller: {e}")
                
            # Send email notification
            try:
                send_notification_email(seller, notification)
                logger.info(f"Sent payment email to seller {seller.username} (ID: {seller.id})")
            except Exception as e:
                logger.error(f"Failed to send payment email to seller: {e}")
        except Exception as e:
            logger.error(f"Error in notify_payment for seller: {e}")
        
        # Notify the buyer
        self.notify_payment_buyer()

    def notify_payment_buyer(self):
        if not self.winning_bid:
            return
            
        buyer = User.query.get(self.winning_bid.bidder_id)
        notification = Notification(
            user_id=buyer.id,
            message=f"Payment successful! You have paid £{self.winning_bid.bid_amount} for '{self.title}'.",
            item_url=self.url,
            item_title=self.title,
            notification_type=8
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send real-time notification
        try:
            from app import socketio
            socketio.emit('new_notification', {
                'id': notification.id,
                'message': notification.message,
                'item_url': notification.item_url,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{buyer.secret_key}')
        except Exception as e:
            logger.error(f"Failed to send buyer payment notification: {e}")
            
        # Send email
        send_notification_email(buyer, notification)

    # Count the number of users watching an auction
    def watcher_count(self):
        return len(self.watchers.all())

class Image(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey(Item.item_id), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now())
    item = db.relationship('Item', back_populates='images')

# Bid Model
class Bid(db.Model):
    __tablename__ = 'bids'

    bid_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(
        db.Integer, 
        db.ForeignKey('items.item_id', ondelete='CASCADE'),
        nullable=False
    )
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bid_amount = db.Column(db.Numeric(10, 2), nullable=False)
    bid_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<Bid {self.bid_id} on Item {self.item_id}>"

# Authentication Request Model
class AuthenticationRequest(db.Model):
    __tablename__ = 'authentication_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(32), unique=True,
                    default=lambda: uuid4().hex, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.now())
    # Request status: 1 = Pending, 2 = Approved, 3 = Declined, 4 = Cancelled
    status = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    updated_at = db.Column(db.DateTime,
                           default=datetime.now(),
                           onupdate=datetime.now())

    # Relationship to expert assignments
    expert_assignments = db.relationship('ExpertAssignment', backref='authentication_request', lazy=True)

    # Relationship to messages
    messages = db.relationship('Message', backref='authentication_request', lazy=True)

    def __repr__(self):
        return f"<AuthenticationRequest {self.request_id} for Item {self.item_id}>"

# Expert Assignment Model
class ExpertAssignment(db.Model):
    __tablename__ = 'expert_assignments'

    assignment_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('authentication_requests.request_id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.now())
    # Assignment status: 1 = Notified, 2 = Completed, 3 = Reassigned, 4 = Cancelled
    status = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    def __repr__(self):
        return f"<ExpertAssignment {self.assignment_id} for Request {self.request_id}>"

# Expert Availability Model
class ExpertAvailability(db.Model):
    __tablename__ = 'expert_availability'

    availability_id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<ExpertAvailability {self.availability_id} for Expert {self.expert_id} on {self.day}>"

# Message Model
class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.Integer, primary_key=True)
    authentication_request_id = db.Column(db.Integer, db.ForeignKey('authentication_requests.request_id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now())

    # Relationship to message images
    images = db.relationship('MessageImage', backref='message', lazy='joined')

    # Helper method to get image URLs for this message
    def get_image_urls(self, expiry=3600):
        """Get all image URLs for this message"""
        return [image.get_url(expiry) for image in self.images]

    def __repr__(self):
        return f"<Message {self.message_id} from User {self.sender_id}>"

# Message Images
class MessageImage(db.Model):
    __tablename__ = 'message_images'

    image_id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.message_id'), nullable=False)
    # Message attachments are private so we store the key not the URL
    image_key = db.Column(db.String(256), nullable=False)

    # Get the URL for the image - only needed here because message attachments are private
    def get_url(self, expiry=3600):
        s3_client = init_s3()
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': current_app.config['AWS_BUCKET'], 'Key': self.image_key},
            ExpiresIn=expiry
        )

    def __repr__(self):
        return f"<MessageImage {self.image_id} for Message {self.message_id}>"

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    item_url = db.Column(db.String(32), nullable=True)
    item_title = db.Column(db.String(256), nullable=True)
    # Notification type: 0 = Default, 1 = Outbid, 2 = Winner, 3 = Loser, 4 = Authentication Update
    # 5 = Auction Ended (Sold), 6 = Auction Ended (Unsold)
    notification_type = db.Column(db.Integer, nullable=True, default=0)


    def __repr__(self):
        return f"<Notification {self.id} for user {self.user_id}>"

# Manager Config Model
class ManagerConfig(db.Model):
    __tablename__ = 'manager_config'

    # Stores the configuration key and value for example, 'base_platform_fee' = '5.0'
    config_key = db.Column(db.String, primary_key=True)
    config_value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Default configuration keys for fees
    BASE_FEE_KEY = 'base_platform_fee'
    AUTHENTICATED_FEE_KEY = 'authenticated_platform_fee'
    MAX_DURATION_KEY = 'max_auction_duration'

    def __repr__(self):
        return f"<ManagerConfig {self.config_key}>"

# Item Category Model
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    # One to many, so each item has one category, but each cat has many items
    items = db.relationship('Item', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

# Expert Category Model
class ExpertCategory(db.Model):
    __tablename__ = 'expert_categories'

    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Relationships to other tables
    expert = db.relationship('User', 
                           backref=db.backref('expert_categories', lazy=True),
                           foreign_keys=[expert_id])
    category = db.relationship('Category',
                             backref=db.backref('expert_categories', lazy=True),
                             foreign_keys=[category_id])

    def __repr__(self):
        return f"<ExpertCategory {self.id} for Expert {self.expert_id} in Category {self.category_id}>"