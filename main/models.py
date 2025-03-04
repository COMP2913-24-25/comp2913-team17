from calendar import c
from datetime import date, datetime
from turtle import back
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_mail import Message
from .tasks import send_winner_email

db = SQLAlchemy()

# ---------------------------
# Models
# ---------------------------

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Roles: 1 = General User, 2 = Expert, 3 = Manager
    role = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime,
                           default=datetime.now(),
                           onupdate=datetime.now())

    # Relationships to other tables:
    items = db.relationship('Item', 
                          backref='seller',
                          lazy=True,
                          foreign_keys='Item.seller_id')
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    authentication_requests = db.relationship('AuthenticationRequest', backref='requester', lazy=True)
    expert_assignments = db.relationship('ExpertAssignment', backref='expert', lazy=True)
    expert_availabilities = db.relationship('ExpertAvailability', backref='expert', lazy=True)
    messages_sent = db.relationship('Message', backref='sender', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Set the password for the user."""
        self.password_hash = generate_password_hash(password, method="pbkdf2")

    def check_password(self, password):
        """Check the password for the user."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

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

# Item Model
class Item(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(32), unique=True,
                    default=lambda: uuid4().hex, nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(256))
    upload_date = db.Column(db.DateTime, default=datetime.now())
    auction_start = db.Column(db.DateTime, nullable=False)
    auction_end = db.Column(db.DateTime, nullable=False)
    minimum_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    # Auction cannot be modified if a bid has been placed
    locked = db.Column(db.Boolean, default=False)

    winning_bid_id = db.Column(
        db.Integer, 
        db.ForeignKey('bids.bid_id', use_alter=True, name='fk_winning_bid'),
        nullable=True
    )
    # Define relationships
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
    
    def __repr__(self):
        return f"<Item {self.title} (ID: {self.item_id})>"

    # Add method to get highest bid
    def highest_bid(self):
        """Get the highest bid for this item"""
        return Bid.query.filter_by(item_id=self.item_id)\
                       .order_by(Bid.bid_amount.desc())\
                       .first()

    # Method for outbid notification
    def notify_outbid(self, outbid_user):
        """Create notification for outbid user"""
        notification = Notification(
            user_id=outbid_user.id,
            message=f"You have been outbid on {self.title}",
            is_read=False,
            created_at=datetime.now()
        )
        db.session.add(notification)
        db.session.commit()

    def notify_winner(self):
        """Create notification for auction winner"""
        winning_bid = self.highest_bid()
        if winning_bid:
            notification = Notification(
                user_id=winning_bid.bidder_id,
                message=f"Congratulations! You won the auction for {self.title}",
                is_read=False,
                created_at=datetime.now()
            )
            db.session.add(notification)
            db.session.commit()

    def notify_winner_email(self):
        """Queue async email notification to winner"""
        if self.winning_bid:
            # Using SQLAlchemy 2.0 pattern
            winner = db.session.get(User, self.winning_bid.bidder_id)
            if winner:
                try:
                    from .tasks import send_winner_email
                    send_winner_email.delay(
                        recipient=winner.email,
                        item_title=self.title,
                        bid_amount=self.winning_bid.bid_amount,
                        end_date=self.auction_end.strftime('%Y-%m-%d %H:%M')
                    )
                except Exception as e:
                    print(f"Error sending winner email: {str(e)}")

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

    # Relationship to payments (if any)
    payments = db.relationship('Payment', backref='bid', lazy=True)

    def __repr__(self):
        return f"<Bid {self.bid_id} on Item {self.item_id}>"

# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bids.bid_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # For now, store card details as a string,  will probably delete later, not a good idea to store
    card_details = db.Column(
        db.String(255),
        nullable=False
    )
    # Payment status: 1 = Pending, 2 = Completed, 3 = Failed
    payment_status = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
    payment_time = db.Column(db.DateTime, default=datetime.now())
    platform_fee_percent = db.Column(db.Numeric(4, 2), nullable=False)
    platform_fee_amount = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<Payment {self.payment_id} for Bid {self.bid_id}>"

# Authentication Request Model
class AuthenticationRequest(db.Model):
    __tablename__ = 'authentication_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(32), unique=True,
                    default=lambda: uuid4().hex, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.now())
    fee_percent = db.Column(db.Numeric(4, 2), nullable=False, default=5.00)
    # Request status: 1 = Pending, 2 = Approved, 3 = Declined
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
    # Assignment status: 1 = Notified, 2 = Completed, 3 = Reassigned
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

    def __repr__(self):
        return f"<Message {self.message_id} from User {self.sender_id}>"

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<Notification {self.notification_id} for User {self.user_id}>"

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

    @classmethod
    def get_fee_percentage(cls, is_authenticated=False):
        """Get the appropriate fee percentage based on item authentication status."""
        if is_authenticated:
            fee = cls.query.filter_by(config_key=cls.AUTHENTICATED_FEE_KEY).first()
            return float(fee.config_value if fee else 5.0)
        fee = cls.query.filter_by(config_key=cls.BASE_FEE_KEY).first()
        return float(fee.config_value if fee else 1.0)

    def __repr__(self):
        return f"<ManagerConfig {self.config_key}>"
