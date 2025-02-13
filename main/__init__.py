from datetime import date, datetime, time, timedelta
import os
from flask import Flask, render_template
from .models import AuthenticationRequest, Bid, ExpertAssignment, ExpertAvailability, Item, ManagerConfig, Message, Notification, Payment, User, db

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sacrebleu'

    # This configuers the database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialises the database
    db.init_app(app)

    with app.app_context():
        # Creates tables if they don't exist
        db.create_all()
        # Populate dummy data if it doesn't already exist
        populate_db(app)

    # Import and registers the blueprints
    from .admin_page import admin_page 
    from .bidding_page import bidding_page
    from .home_page import home_page
    from .item_page import item_page
    from .user_page import user_page

    app.register_blueprint(admin_page, url_prefix='/admin')
    app.register_blueprint(bidding_page, url_prefix='/bidding')
    app.register_blueprint(home_page, url_prefix='/home')
    app.register_blueprint(item_page, url_prefix='/item')
    app.register_blueprint(user_page, url_prefix='/user')

    # Defines the main route
    @app.route('/')
    def main():
        return render_template('home.html')

    return app

def populate_db(app):
    with app.app_context():
        # Checks to see if user exists
        # If user exists, then dummy data has been loaded
        if User.query.first():
            print("Database already populated. Skipping dummy data load.")
            return

        now = datetime.now()

        # ---------------------------
        # Create Dummy Data
        # ---------------------------

        # Users
        user1 = User(username="alice", email="alice@example.com",
                     password_hash="hashed_pw1", role="general")
        user2 = User(username="bob", email="bob@example.com",
                     password_hash="hashed_pw2", role="general")
        user3 = User(username="charlie", email="charlie@example.com",
                     password_hash="hashed_pw3", role="expert")
        user4 = User(username="diana", email="diana@example.com",
                     password_hash="hashed_pw4", role="manager")
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()

        # Items
        item1 = Item(
            seller_id=user1.id,
            title="Vintage Clock",
            description="An antique clock from 1900",
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=7),
            minimum_price=100.00,
            authentication_status="not_requested"
        )
        item2 = Item(
            seller_id=user2.id,
            title="Art Painting",
            description="A modern art painting with vibrant colors",
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=10),
            minimum_price=200.00,
            authentication_status="not_requested"
        )
        db.session.add_all([item1, item2])
        db.session.commit()

        # Bids
        bid1 = Bid(
            item_id=item1.item_id,
            bidder_id=user2.id,
            bid_amount=120.00,
            bid_time=now + timedelta(days=1)
        )
        bid2 = Bid(
            item_id=item1.item_id,
            bidder_id=user3.id,
            bid_amount=130.00,
            bid_time=now + timedelta(days=2)
        )
        bid3 = Bid(
            item_id=item2.item_id,
            bidder_id=user1.id,
            bid_amount=210.00,
            bid_time=now + timedelta(days=3)
        )
        db.session.add_all([bid1, bid2, bid3])
        db.session.commit()

        # Payment (for bid1)
        payment1 = Payment(
            bid_id=bid1.bid_id,
            user_id=user2.id,
            card_details="encrypted_card_info",
            payment_status="completed",
            payment_time=now + timedelta(days=1, hours=2)
        )
        db.session.add(payment1)
        db.session.commit()

        # Authentication Request (for item2)
        auth_req = AuthenticationRequest(
            item_id=item2.item_id,
            requester_id=user2.id,
            request_date=now + timedelta(days=1),
            fee_percent=5.00,
            status="pending"
        )
        db.session.add(auth_req)
        db.session.commit()

        # Dummy Expert Assignment (for the authentication request)
        expert_assignment = ExpertAssignment(
            request_id=auth_req.request_id,
            expert_id=user3.id,
            assigned_date=now + timedelta(days=1, minutes=30),
            status="notified"
        )
        db.session.add(expert_assignment)
        db.session.commit()

        # Expert Availabilities (for user3)
        availability1 = ExpertAvailability(
            expert_id=user3.id,
            day=date.today(),
            start_time=time(9, 0),
            end_time=time(12, 0),
            status="available"
        )
        availability2 = ExpertAvailability(
            expert_id=user3.id,
            day=date.today(),
            start_time=time(13, 0),
            end_time=time(17, 0),
            status="available"
        )
        db.session.add_all([availability1, availability2])
        db.session.commit()

        # Messages (for the expert assignment)
        message1 = Message(
            assignment_id=expert_assignment.assignment_id,
            sender_id=user3.id,
            message_text="I have reviewed the request.",
            sent_at=now + timedelta(days=1, minutes=35)
        )
        message2 = Message(
            assignment_id=expert_assignment.assignment_id,
            sender_id=user2.id,
            message_text="Thanks for the update.",
            sent_at=now + timedelta(days=1, minutes=40)
        )
        db.session.add_all([message1, message2])
        db.session.commit()

        # Notification (for user2)
        notification1 = Notification(
            user_id=user2.id,
            message="Your bid has been accepted.",
            is_read=False,
            created_at=now + timedelta(days=2)
        )
        db.session.add(notification1)
        db.session.commit()

        # Manager Config
        manager_config = ManagerConfig(
            config_key="max_auction_duration",
            config_value="30",  # maximum auction duration in days
            description="Maximum auction duration in days"
        )
        db.session.add(manager_config)
        db.session.commit()

        print("Database populated with dummy data!")