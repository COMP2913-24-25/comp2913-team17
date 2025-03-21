from datetime import date, datetime, time, timedelta
from decimal import Decimal
import random
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

        # Auctions
        items = []
        images = []

        auction1 = Item(
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
            item=auction1
        )

        items.append(auction1)
        images.append(image1)

        auction2 = Item(
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
            item=auction2
        )

        items.append(auction2)
        images.append(image2)

        # Auction 3: Vintage Vase
        auction3 = Item(
            seller_id=user3.id,
            title='Vintage Vase',
            description='A beautiful vintage vase from the early 1900s.',
            upload_date=now - timedelta(days=2),
            auction_start=now - timedelta(days=2),
            auction_end=now + timedelta(days=2),
            minimum_price=150.00,
            category_id=cat1.id
        )
        image3 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024256_Vase1.jpg',
            item=auction3
        )
        image4 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024256_Vase2.jpg',
            item=auction3
        )
        image5 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024257_Vase3.jpg',
            item=auction3
        )
        items.append(auction3)
        images.extend([image3, image4, image5])

        # Auction 4: Modern Sculpture (ended)
        auction4 = Item(
            seller_id=user4.id,
            title='Modern Sculpture',
            description='A unique modern sculpture.',
            upload_date=now - timedelta(days=3),
            auction_start=now - timedelta(days=3),
            auction_end=now - timedelta(hours=1),
            minimum_price=3000.00,
            category_id=cat2.id
        )
        image6 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024250_Sculpture1.jpg',
            item=auction4
        )
        image7 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024252_Sculpture2.jpg',
            item=auction4
        )
        image8 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024252_Sculpture2.jpg',
            item=auction4
        )
        items.append(auction4)
        images.extend([image6, image7, image8])

        # Auction 5: Smartphone
        auction5 = Item(
            seller_id=user5.id,
            title='iPhone',
            description='A classic smartphone model with advanced features (for the time of it\'s release).',
            upload_date=now - timedelta(days=1),
            auction_start=now - timedelta(days=1),
            auction_end=now + timedelta(days=1),
            minimum_price=500.00,
            category_id=cat3.id
        )
        image9 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024242_iPhone1.jpg',
            item=auction5
        )
        image10 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024244_iPhone2.jpg',
            item=auction5
        )
        items.append(auction5)
        images.extend([image9, image10])

        # Auction 6: Designer Jacket
        auction6 = Item(
            seller_id=user1.id,
            title='Designer Jacket',
            description='A stylish designer jacket in excellent condition.',
            upload_date=now - timedelta(days=4),
            auction_start=now - timedelta(days=4),
            auction_end=now + timedelta(hours=6),
            minimum_price=250.00,
            category_id=cat4.id
        )
        image11 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024246_Jacket1.jpg',
            item=auction6
        )
        image12 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024247_Jacket2.jpg',
            item=auction6
        )
        items.append(auction6)
        images.extend([image11, image12])

        # Auction 7: Antique Desk
        auction7 = Item(
            seller_id=user2.id,
            title='Antique Desk',
            description='A well-crafted antique desk perfect for any study.',
            upload_date=now - timedelta(days=5),
            auction_start=now - timedelta(days=5),
            auction_end=now + timedelta(days=3),
            minimum_price=800.00,
            category_id=cat5.id
        )
        image13 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024236_Desk1.jpg',
            item=auction7
        )
        image14 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024236_Desk2.jpg',
            item=auction7
        )
        items.append(auction7)
        images.extend([image13, image14])

        # Auction 8: Rare Comic Book
        auction8 = Item(
            seller_id=user3.id,
            title='Rare Comic Book',
            description='A rare comic book from the golden age.',
            upload_date=now - timedelta(days=6),
            auction_start=now - timedelta(days=6),
            auction_end=now + timedelta(hours=12),
            minimum_price=75.00,
            category_id=cat6.id
        )
        image15 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024233_Comic1.jpg',
            item=auction8
        )
        image16 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024235_Comic2.jpg',
            item=auction8
        )
        items.append(auction8)
        images.extend([image15, image16])

        # Auction 9: First Edition Book (ended)
        auction9 = Item(
            seller_id=user4.id,
            title='Moby Dick: A First Edition',
            description="A rare first edition book, a collector's dream.",
            upload_date=now - timedelta(days=7),
            auction_start=now - timedelta(days=7),
            auction_end=now - timedelta(hours=2),
            minimum_price=120.00,
            category_id=cat7.id
        )
        image17 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024232_Book1.jpeg',
            item=auction9
        )
        items.append(auction9)
        images.append(image17)

        # Auction 10: Luxury Watch
        auction10 = Item(
            seller_id=user5.id,
            title='Luxury Rolex',
            description='A high-end luxury watch with impeccable design.',
            upload_date=now - timedelta(days=1),
            auction_start=now - timedelta(days=1),
            auction_end=now + timedelta(days=2),
            minimum_price=1500.00,
            category_id=cat8.id
        )
        image18 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024248_Rolex.jpg',
            item=auction10
        )
        items.append(auction10)
        images.append(image18)

        # Auction 11: Sports Car (ended)
        auction11 = Item(
            seller_id=user1.id,
            title='Ferrari',
            description='A vintage sports car in pristine condition.',
            upload_date=now - timedelta(days=10),
            auction_start=now - timedelta(days=10),
            auction_end=now - timedelta(days=1),
            minimum_price=50000000.00,
            category_id=cat9.id
        )
        image19 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024238_Ferrari2.jpg',
            item=auction11
        )
        image20 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024237_Ferrari1.jpg',
            item=auction11
        )
        items.append(auction11)
        images.extend([image19, image20])

        # Auction 12: Electric Guitar
        auction12 = Item(
            seller_id=user2.id,
            title='Electric Guitar',
            description='A quality electric guitar for music enthusiasts.',
            upload_date=now - timedelta(days=3),
            auction_start=now - timedelta(days=3),
            auction_end=now + timedelta(hours=5),
            minimum_price=600.00,
            category_id=cat10.id
        )
        image21 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024239_Guitar1.jpg',
            item=auction12
        )
        image22 = Image(
            url='https://sc23jk3-auctionbucket.s3.amazonaws.com/auction_items/20250321_024240_Guitar2.jpg',
            item=auction12
        )
        items.append(auction12)
        images.extend([image21, image22])

        db.session.add_all(items + images)
        db.session.commit()

        # Bids - Managers and experts cannot bid
        bid1 = Bid(
            item_id=auction11.item_id,
            bidder_id=user2.id,
            bid_amount=51000000.00,
            bid_time=now
        )
        bid2 = Bid(
            item_id=auction11.item_id,
            bidder_id=user1.id,
            bid_amount=51700000.00,
            bid_time=now
        )
        db.session.add_all([bid1, bid2])
        db.session.commit()

         # -------------------------
        # Add Additional Fake Bids for Auctions (except Antique Desk and Electric Guitar)
        # -------------------------
        regular_users = [user1, user2, user3, user4, user5]
        for auction in items:
            if auction.title in ['Antique Desk', 'Electric Guitar', 'Ferrari']:
                continue

            # Determine total number of bids desired (between 1 and 3)
            if auction.highest_bid():
                total_bids = random.randint(1, 3)
                additional_bids = total_bids - 1  # one bid already exists
            else:
                total_bids = random.randint(1, 3)
                additional_bids = total_bids

            # Set the starting bid amount: highest bid if exists; otherwise, the minimum price.
            current_bid = auction.highest_bid().bid_amount if auction.highest_bid() else auction.minimum_price

            for _ in range(additional_bids):
                possible_bidders = [u for u in regular_users if u.id != auction.seller_id]
                bidder = random.choice(possible_bidders)
                # Increase the current bid by a random 5% to 15%
                increment = current_bid * Decimal(str(random.uniform(0.05, 0.15)))
                new_bid_amount = current_bid + increment
                new_bid = Bid(
                    item_id=auction.item_id,
                    bidder_id=bidder.id,
                    bid_amount=new_bid_amount,
                    bid_time=now + timedelta(minutes=random.randint(1, 60))
                )
                db.session.add(new_bid)
                db.session.commit()
                current_bid = new_bid_amount

        # Authentication Requests for auctions (except certain titles)
        excluded_titles = ['Electric Guitar', 'Designer Jacket', 'Rare Comic Book', 'iPhone']
        regular_users = [user1, user2, user3, user4, user5]
        for auction in items:
            if auction.title not in excluded_titles:
                # Choose a requester (a regular user) who is not the seller
                possible_requesters = [u for u in regular_users if u.id != auction.seller_id]
                if possible_requesters:
                    requester = random.choice(possible_requesters)
                    auth_req = AuthenticationRequest(
                        item_id=auction.item_id,
                        requester_id=requester.id,
                        request_date=now,
                        fee_percent=5.00,
                        status=1  # Pending
                    )
                    db.session.add(auth_req)
        db.session.commit()


        # Authentication Request (for item2)
        auth_req = AuthenticationRequest(
            item_id=auction2.item_id,
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

        # For every auction, generate fake notifications for the bids
        for auction in items:
            # Only proceed if there are any bids
            if auction.bids:
                highest = auction.highest_bid()
                # Notify the highest bidder that their bid is accepted
                winner = User.query.get(highest.bidder_id)
                winner_notification = Notification(
                    user_id=winner.id,
                    message=f"Congratulations! Your bid on '{auction.title}' has been accepted.",
                    is_read=False,
                    created_at=now,
                    item_url=auction.url,
                    item_title=auction.title,
                    notification_type=0  # standard notification
                )
                db.session.add(winner_notification)
                
                # Notify all other bidders that they have been outbid
                for bid in auction.bids:
                    if bid.bidder_id != highest.bidder_id:
                        other_user = User.query.get(bid.bidder_id)
                        outbid_notification = Notification(
                            user_id=other_user.id,
                            message=f"You have been outbid on '{auction.title}'.",
                            is_read=False,
                            created_at=now,
                            item_url=auction.url,
                            item_title=auction.title,
                            notification_type=1  # outbid notification
                        )
                        db.session.add(outbid_notification)
                db.session.commit()


        print('Database populated with dummy data!')
