from datetime import date, datetime, time, timedelta
from .models import (
    AuthenticationRequest, Bid, ExpertAssignment, ExpertAvailability,
    Item, ManagerConfig, Message, Notification, User, Category, Image,
    db
)

def populate_db(app):
    with app.app_context():
        # Check if user exists
        # If user exists, then dummy data has been loaded
        if User.query.first():
            print('Database already populated. Skipping dummy data load.')
            return

        now = datetime.now()

        # Regular Users
        user1 = User(username='alice', email='alice@example.com', role=1)
        user1.set_password('Alice@123')

        user2 = User(username='robert', email='robert@example.com', role=1)
        user2.set_password('Robert@123')

        user3 = User(username='john', email='john@example.com', role=1)
        user3.set_password('John@123')

        user4 = User(username='sarah', email='sarah@example.com', role=1)
        user4.set_password('Sarah@123')

        user5 = User(username='michael', email='michael@example.com', role=1)
        user5.set_password('Michael@123')

        # Experts (role=2)
        user6 = User(username='charlie', email='charlie@example.com', role=2)
        user6.set_password('Charlie@123')

        user7 = User(username='emma', email='emma@example.com', role=2)
        user7.set_password('Emma@123')

        user8 = User(username='oliver', email='oliver@example.com', role=2)
        user8.set_password('Oliver@123')

        # Managers (role=3)
        user9 = User(username='diana', email='diana@example.com', role=3)
        user9.set_password('Diana@123')

        user10 = User(username='frank', email='frank@example.com', role=3)
        user10.set_password('Frank@123')

        db.session.add_all([user1, user2, user3, user4, user5,
                            user6, user7, user8, user9, user10])
        db.session.commit()

        # Categories
        cat1 = Category(name='Antiques', description='Vintage and antique items')
        cat2 = Category(name='Art', description='Paintings, sculptures, and more')
        cat3 = Category(name='Electronics', description='Gadgets and tech devices')
        cat4 = Category(name='Fashion', description='Clothing, accessories, etc.')
        cat5 = Category(name='Furniture', description='Home and office furniture')
        cat6 = Category(name='Collectibles', description='Rare and collectible items')
        cat7 = Category(name='Books', description='Rare books and literature')
        cat8 = Category(name='Luxury Goods', description='High-end designer items and luxury products')
        cat9 = Category(name='Vehicles', description='Cars, motorcycles, boats, and other vehicles')
        cat10 = Category(name='Musical Instruments', description='Guitars, pianos, and other instruments')
        cat11 = Category(name='Sports Equipment', description='Athletic gear and sporting goods')
        cat12 = Category(name='Toys & Games', description='Collectible toys and vintage games')
        cat13 = Category(name='Miscellaneous', description='Items that don\'t fit other categories')
        db.session.add_all([cat1, cat2, cat3, cat4, cat5, cat6, cat7, cat8, cat9, cat10, cat11, cat12, cat13])
        db.session.commit()

        # Items
        item1 = Item(
            seller_id=user1.id,
            title='Vintage Clock',
            description='An antique clock from 1900',
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=4),
            minimum_price=100.00,
            category_id=cat1.id  # Assign to "Antiques"
        )

        image1 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250307_014410_clock.jpg',
            item=item1
        )

        item2 = Item(
            seller_id=user2.id,
            title='Art Painting',
            description='A modern art painting with vibrant colours',
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(minutes=1),
            minimum_price=200.00,
            category_id=cat2.id  # Assign to "Art"
        )

        image2 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250307_014233_art.jpg',
            item=item2
        )

        db.session.add_all([item1, item2, image1, image2])
        db.session.commit()

        # Bids - Managers and experts cannot bid
        bid1 = Bid(
            item_id=item1.item_id,
            bidder_id=user2.id,
            bid_amount=120.00,
            bid_time=now
        )
        bid2 = Bid(
            item_id=item2.item_id,
            bidder_id=user1.id,
            bid_amount=210.00,
            bid_time=now
        )
        db.session.add_all([bid1, bid2])
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
            expert_id=user6.id,
            assigned_date=now,
            status=1
        )
        db.session.add(expert_assignment)
        db.session.commit()
    
        # For Charlie (user6) – next 14 days:
        for i in range(14):
            day = date.today() + timedelta(days=i)
            # Weekday: available from 10:00 to 16:00; Weekend (Saturday=5, Sunday=6): unavailable in that slot.
            if day.weekday() in [5, 6]:  # Saturday or Sunday
                availability = ExpertAvailability(
                    expert_id=user6.id,
                    day=day,
                    start_time=time(10, 0),
                    end_time=time(16, 0),
                    status=False  # Unavailable on weekends in that slot
                )
            else:
                availability = ExpertAvailability(
                    expert_id=user6.id,
                    day=day,
                    start_time=time(10, 0),
                    end_time=time(16, 0),
                    status=True   # Available on weekdays
                )
            db.session.add(availability)

        # For Emma (user7) – next 7 days:
        for i in range(7):
            day = date.today() + timedelta(days=i)
            if i < 5:
                # Not available for the next 5 days during 10:00 to 15:00
                availability = ExpertAvailability(
                    expert_id=user7.id,
                    day=day,
                    start_time=time(10, 0),
                    end_time=time(15, 0),
                    status=False
                )
            else:
                # Available for the following 2 days during 10:00 to 15:00
                availability = ExpertAvailability(
                    expert_id=user7.id,
                    day=day,
                    start_time=time(10, 0),
                    end_time=time(15, 0),
                    status=True
                )
            db.session.add(availability)

        # For Oliver (user8) – completely unavailable for the next 7 days:
        for i in range(7):
            day = date.today() + timedelta(days=i)
            # Mark him as unavailable for the full day.
            availability = ExpertAvailability(
                expert_id=user8.id,
                day=day,
                start_time=time(8, 0),
                end_time=time(20, 00),
                status=False
            )
            db.session.add(availability)

        db.session.commit()

        # Messages (for the expert assignment)
        message1 = Message(
            authentication_request_id=auth_req.request_id,
            sender_id=user6.id,
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
