from datetime import datetime, date, time
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------------------------
# Models
# ---------------------------

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # e.g., 'general', 'expert', 'manager'
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime,
                           default=datetime.now(),
                           onupdate=datetime.now())
    
    # Relationships to other tables:
    items = db.relationship('Item', backref='seller', lazy=True)
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    authentication_requests = db.relationship('AuthenticationRequest', backref='requester', lazy=True)
    expert_assignments = db.relationship('ExpertAssignment', backref='expert', lazy=True)
    expert_availabilities = db.relationship('ExpertAvailability', backref='expert', lazy=True)
    messages_sent = db.relationship('Message', backref='sender', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"

# Item Model
class Item(db.Model):
    __tablename__ = 'items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now())
    auction_start = db.Column(db.DateTime, nullable=False)
    auction_end = db.Column(db.DateTime, nullable=False)
    minimum_price = db.Column(db.Numeric(10, 2), nullable=False)
    locked = db.Column(db.Boolean, default=False) # if someone has bid set to true
    authentication_status = db.Column(
        db.String(20),
        nullable=False,
        default='not_requested'  # other values: 'pending', 'approved', 'declined'
    )
    
    # Relationships:
    bids = db.relationship('Bid', backref='item', lazy=True)
    authentication_requests = db.relationship('AuthenticationRequest', backref='item', lazy=True)
    
    def __repr__(self):
        return f"<Item {self.title} (ID: {self.item_id})>"

# Bid Model
class Bid(db.Model):
    __tablename__ = 'bids'
    
    bid_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bid_amount = db.Column(db.Numeric(10, 2), nullable=False)
    bid_time = db.Column(db.DateTime, default=datetime.now())
    
    # Relationship to payments (if any)
    payments = db.relationship('Payment', backref='bid', lazy=True)
    
    def __repr__(self):
        return f"<Bid {self.bid_id} on Item {self.item_id}>"

# Payment Model
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bids.bid_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_details = db.Column(
        db.String(255),
        nullable=False
    )  # change, will probably delete later, not a good idea to store
    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'  # e.g., 'pending', 'completed', 'failed'
    )
    payment_time = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
        return f"<Payment {self.payment_id} for Bid {self.bid_id}>"

# Authentication Request Model
class AuthenticationRequest(db.Model):
    __tablename__ = 'authentication_requests'
    
    request_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.now())
    fee_percent = db.Column(db.Numeric(4, 2), nullable=False, default=5.00)
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'  # e.g., 'pending', 'approved', 'declined'
    )
    updated_at = db.Column(db.DateTime,
                           default=datetime.now(),
                           onupdate=datetime.now())
    
    # Relationship to expert assignments
    expert_assignments = db.relationship('ExpertAssignment', backref='authentication_request', lazy=True)
    
    def __repr__(self):
        return f"<AuthenticationRequest {self.request_id} for Item {self.item_id}>"

# Expert Assignment Model
class ExpertAssignment(db.Model):
    __tablename__ = 'expert_assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('authentication_requests.request_id'), nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(
        db.String(20),
        nullable=False,
        default='notified'  # e.g., 'notified', 'in_review', 'awaiting_info', 'completed'
    )
    
    # Relationship to messages
    messages = db.relationship('Message', backref='expert_assignment', lazy=True)
    
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
    status = db.Column(
        db.String(20),
        nullable=False,
        default='available'  # e.g., 'available', 'unavailable'
    )
    
    def __repr__(self):
        return f"<ExpertAvailability {self.availability_id} for Expert {self.expert_id} on {self.day}>"

# Message Model
class Message(db.Model):
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('expert_assignments.assignment_id'), nullable=False)
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
    
    config_key = db.Column(db.String, primary_key=True)
    config_value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f"<ManagerConfig {self.config_key}>"
