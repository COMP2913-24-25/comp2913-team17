from datetime import date, datetime, time, timedelta
from .models import (
    AuthenticationRequest, Bid, ExpertAssignment, ExpertAvailability,
    Item, ManagerConfig, Message, Notification, Payment, User, Category, db
)

def populate_db(app):
    with app.app_context():
        # Check if user exists
        # If user exists, then dummy data has been loaded
        if User.query.first():
            print('Database already populated. Skipping dummy data load.')
            return

        now = datetime.now()

        # Users
        user1 = User(username='alice', email='alice@example.com', role=1)
        user1.set_password('alice123')

        user2 = User(username='robert', email='robert@example.com', role=1)
        user2.set_password('robert123')

        user3 = User(username='charlie', email='charlie@example.com', role=2)
        user3.set_password('charlie123')

        user4 = User(username='diana', email='diana@example.com', role=3)
        user4.set_password('diana123')

        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()

        # Categories (create and commit categories first)
        cat1 = Category(name='Antiques', description='Vintage and antique items')
        cat2 = Category(name='Art', description='Paintings, sculptures, and more')
        cat3 = Category(name='Electronics', description='Gadgets and tech devices')
        cat4 = Category(name='Fashion', description='Clothing, accessories, etc.')
        cat5 = Category(name='Furniture', description='Home and office furniture')
        cat6 = Category(name='Collectibles', description='Rare and collectible items')
        cat7 = Category(name='Books', description='Rare books and literature')
        db.session.add_all([cat1, cat2, cat3, cat4, cat5, cat6, cat7])
        db.session.commit()

        # Items (assign categories at creation time)
        item1 = Item(
            seller_id=user1.id,
            title='Vintage Clock',
            description='An antique clock from 1900',
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=3),
            minimum_price=100.00,
            category_id=cat1.id  # Assign to "Antiques"
        )
        item2 = Item(
            seller_id=user2.id,
            title='Art Painting',
            description='A modern art painting with vibrant colours',
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=5),
            minimum_price=200.00,
            category_id=cat2.id  # Assign to "Art"
        )
        db.session.add_all([item1, item2])
        db.session.commit()

        # Bids
        bid1 = Bid(
            item_id=item1.item_id,
            bidder_id=user2.id,
            bid_amount=120.00,
            bid_time=now
        )
        bid2 = Bid(
            item_id=item1.item_id,
            bidder_id=user3.id,
            bid_amount=130.00,
            bid_time=now
        )
        bid3 = Bid(
            item_id=item2.item_id,
            bidder_id=user1.id,
            bid_amount=210.00,
            bid_time=now
        )
        db.session.add_all([bid1, bid2, bid3])
        db.session.commit()

        # Authentication Request (for item2)
        auth_req = AuthenticationRequest(
            item_id=item2.item_id,
            requester_id=user2.id,
            request_date=now,
            fee_percent=5.00,
            status=1
        )
        db.session.add(auth_req)
        db.session.commit()

        # Expert Assignment (for the authentication request)
        expert_assignment = ExpertAssignment(
            request_id=auth_req.request_id,
            expert_id=user3.id,
            assigned_date=now,
            status=1
        )
        db.session.add(expert_assignment)
        db.session.commit()

        # Expert Availabilities (for user3)
        availability1 = ExpertAvailability(
            expert_id=user3.id,
            day=date.today(),
            start_time=time(9, 0),
            end_time=time(12, 0),
            status=False
        )
        availability2 = ExpertAvailability(
            expert_id=user3.id,
            day=date.today(),
            start_time=time(13, 0),
            end_time=time(17, 0),
            status=True
        )
        db.session.add_all([availability1, availability2])
        db.session.commit()

        # Messages (for the expert assignment)
        message1 = Message(
            authentication_request_id=auth_req.request_id,
            sender_id=user3.id,
            message_text='Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
            sent_at=now + timedelta(hours=1)
        )
        message2 = Message(
            authentication_request_id=auth_req.request_id,
            sender_id=user2.id,
            message_text='I\'ll provide the necessary information shortly.',
            sent_at=now + timedelta(hours=2)
        )
        db.session.add_all([message1, message2])
        db.session.commit()

        # Notification (for user2)
        notification1 = Notification(
            user_id=user2.id,
            message='Your bid has been accepted.',
            is_read=False,
            created_at=now + timedelta(days=2)
        )
        db.session.add(notification1)
        db.session.commit()

        # Manager Config
        configs = [
            ManagerConfig(
                config_key='base_platform_fee',
                config_value='1.00',
                description='Base platform fee percentage for standard items'
            ),
            ManagerConfig(
                config_key='authenticated_platform_fee',
                config_value='5.00',
                description='Platform fee percentage for authenticated items'
            ),
            ManagerConfig(
                config_key='max_auction_duration',
                config_value='5',
                description='Maximum auction duration in days'
            )
        ]
        db.session.add_all(configs)
        db.session.commit()

        print('Database populated with dummy data!')
