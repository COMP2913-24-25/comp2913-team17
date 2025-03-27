from datetime import date, datetime, time, timedelta
from decimal import Decimal
import random
from .models import (
    AuthenticationRequest, Bid, ExpertAssignment, ExpertAvailability, ExpertCategory,
    Item, ManagerConfig, Message, MessageImage, Notification, User, Category, Image,
    MessageImage, db
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

        # Additional Regular Users
        user11 = User(username='linda', email='linda@example.com', role=1)
        user11.set_password('Linda@123')

        user12 = User(username='peter', email='peter@example.com', role=1)
        user12.set_password('Peter@123')

        user13 = User(username='kevin', email='kevin@example.com', role=1)
        user13.set_password('Kevin@123')

        user14 = User(username='susan', email='susan@example.com', role=1)
        user14.set_password('Susan@123')

        # Additional Experts (role=2)
        user15 = User(username='cristiano', email='cristiano@example.com', role=2)
        user15.set_password('Cristiano@123')

        user16 = User(username='sandeep', email='sandeep@example.com', role=2)
        user16.set_password('sandeep@123')

        user17 = User(username='jamal', email='jamal@example.com', role=2)
        user17.set_password('jamal@123')

        user18 = User(username='yusuf', email='cheeseman@example.com', role=2)
        user18.set_password('Cheeseman@123')

        # Add them to the session along with the previous users:
        db.session.add_all([user11, user12, user13, user14, user15, user16, user17, user18])
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
            upload_date=now - timedelta(days=1),
            auction_start=now - timedelta(days=1),
            auction_end=now + timedelta(days=3),
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
            upload_date=now - timedelta(days=2),
            auction_start=now - timedelta(days=2),
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
            upload_date=now - timedelta(days=3),
            auction_start=now - timedelta(days=3),
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
            minimum_price=90000.00,
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
            bid_amount=94000.00,
            bid_time=now
        )
        bid2 = Bid(
            item_id=auction11.item_id,
            bidder_id=user1.id,
            bid_amount=92000.00,
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

            # Set the initial bid time to 5 hours ago.
            last_bid_time = now - timedelta(hours=5)

            for _ in range(additional_bids):
                possible_bidders = [u for u in regular_users if u.id != auction.seller_id]
                bidder = random.choice(possible_bidders)
                # Increase the current bid by a random 5% to 15%
                increment = current_bid * Decimal(str(random.uniform(0.05, 0.15)))
                new_bid_amount = current_bid + increment
                # Add a random number of minutes (between 1 and 60) to the last bid time,
                # ensuring that each bid has a later timestamp than the previous one.
                delta_minutes = random.randint(1, 60)
                new_bid_time = last_bid_time + timedelta(minutes=delta_minutes)
                
                new_bid = Bid(
                    item_id=auction.item_id,
                    bidder_id=bidder.id,
                    bid_amount=new_bid_amount,
                    bid_time=new_bid_time
                )
                db.session.add(new_bid)
                db.session.commit()
    
                # Update the last_bid_time and current_bid for the next iteration.
                last_bid_time = new_bid_time
                current_bid = new_bid_amount

        # Authentication Requests for auctions (except certain titles)
        excluded_titles = ['Luxury Rolex', 'Rare Comic Book', 'Ferrari', 'Moby Dick: A First Edition', 'Modern Sculpture', 'Electric Guitar', 'Designer Jacket', 'Vintage Vase', 'iPhone']
        for auction in items:
            if auction.title not in excluded_titles:
                auth_req = AuthenticationRequest(
                    item_id=auction.item_id,
                    requester_id=auction.seller_id,
                    request_date=now,
                    fee_percent=5.00
                )
                db.session.add(auth_req)
        db.session.commit()

        # ---------------------------
        # Mark Specific Auctions as Authenticated and Create Expert Assignments
        # We want to mark the following auctions as authenticated:
        # - Art Painting (auction2)
        # - Modern Sculpture (auction4)
        # - Moby Dick: A First Edition (auction9)
        # - Ferrari (auction11)
        # ---------------------------
        # For Art Painting:
        auth_req_art = AuthenticationRequest.query.filter_by(item_id=auction2.item_id).first()
        if auth_req_art:
            auth_req_art.status = 2  # Authenticated
            db.session.commit()
            if auth_req_art.expert_assignments:
                auth_req_art.expert_assignments[0].status = 2
            else:
                expert_assignment_art = ExpertAssignment(
                    request_id=auth_req_art.request_id,
                    expert_id=user6.id,  # Assign Charlie for example
                    assigned_date=now,
                    status=2
                )
                db.session.add(expert_assignment_art)
            db.session.commit()

            # Add seller message with image for Art Painting
            message_expert_art1 = Message(
                authentication_request_id=auth_req_art.request_id,
                sender_id=user6.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=1, minutes=30)
            )
            message_seller_art = Message(
                authentication_request_id=auth_req_art.request_id,
                sender_id=auction2.seller_id,
                message_text="Here are more details about my artwork. Please see the attached image for reference.",
                sent_at=now - timedelta(hours=1)
            )
            db.session.add_all([message_expert_art1, message_seller_art])
            db.session.commit()

            message_image_art = MessageImage(
                message_id=message_seller_art.message_id,
                image_key="message_attachments/20250321_130844_ARTJPG.jpg"  # S3 key for the Art image
            )
            db.session.add(message_image_art)
            db.session.commit()

            # Add expert response for Art Painting
            message_expert_art = Message(
                authentication_request_id=auth_req_art.request_id,
                sender_id=user6.id,
                message_text="Thank you for the information. Your artwork is now authenticated.",
                sent_at=now - timedelta(minutes=15)
            )
            db.session.add(message_expert_art)
            db.session.commit()

        # For Modern Sculpture:
        auth_req_sculpt = AuthenticationRequest(
            item_id=auction4.item_id,
            requester_id=auction4.seller_id,
            request_date=now,
            fee_percent=5.00,
            status=2  # Authenticated
        )
        db.session.add(auth_req_sculpt)
        db.session.commit()
        expert_assignment_sculpt = ExpertAssignment(
            request_id=auth_req_sculpt.request_id,
            expert_id=user7.id,   # Assign Emma for sculpture
            assigned_date=now,
            status=2
        )
        db.session.add(expert_assignment_sculpt)
        db.session.commit()

        # Add seller message with image for Modern Sculpture
        message_expert_sculpt1 = Message(
                authentication_request_id=auth_req_sculpt.request_id,
                sender_id=user7.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=1, minutes=30)
        )
        message_seller_sculpt = Message(
            authentication_request_id=auth_req_sculpt.request_id,
            sender_id=auction4.seller_id,
            message_text="Please find attached a detailed view of my sculpture.",
            sent_at=now - timedelta(hours=1)
        )
        db.session.add_all([message_expert_sculpt1, message_seller_sculpt])

        db.session.commit()

        message_image_sculpt = MessageImage(
            message_id=message_seller_sculpt.message_id,
            image_key="message_attachments/20250321_130846_SCULPTURE.jpg"  # S3 key for the Sculpture image
        )
        db.session.add(message_image_sculpt)
        db.session.commit()

        # Add expert response for Modern Sculpture
        message_expert_sculpt = Message(
            authentication_request_id=auth_req_sculpt.request_id,
            sender_id=user7.id,
            message_text="Thank you for the details. Your sculpture is authenticated.",
            sent_at=now - timedelta(minutes=15)
        )
        db.session.add(message_expert_sculpt)
        db.session.commit()

        # For Moby Dick: A First Edition
        auth_req_moby = AuthenticationRequest(
            item_id=auction9.item_id,
            requester_id=auction9.seller_id,
            request_date=now,
            fee_percent=5.00,
            status=2  # Authenticated
        )
        db.session.add(auth_req_moby)
        db.session.commit()
        expert_assignment_moby = ExpertAssignment(
            request_id=auth_req_moby.request_id,
            expert_id=user8.id,   # Assign Oliver for Moby Dick
            assigned_date=now,
            status=2
        )
        db.session.add(expert_assignment_moby)
        db.session.commit()

        message_expert_moby1 = Message(
                authentication_request_id=auth_req_moby.request_id,
                sender_id=user8.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=1, minutes=30)
        )
        # Add seller message with image for Moby Dick
        message_seller_moby = Message(
            authentication_request_id=auth_req_moby.request_id,
            sender_id=auction9.seller_id,
            message_text="Please see the attached close-up of my rare first edition.",
            sent_at=now - timedelta(hours=1)
        )
        db.session.add_all([message_expert_moby1, message_seller_moby])
        db.session.commit()

        message_image_moby = MessageImage(
            message_id=message_seller_moby.message_id,
            image_key="message_attachments/20250321_130846_MOBYDICK.jpg"  # S3 key for the Moby Dick image
        )
        db.session.add(message_image_moby)
        db.session.commit()

        # Add expert response for Moby Dick
        message_expert_moby = Message(
            authentication_request_id=auth_req_moby.request_id,
            sender_id=user8.id,
            message_text="Thank you for providing the image and details. Your item is authenticated.",
            sent_at=now - timedelta(minutes=15)
        )
        db.session.add(message_expert_moby)
        db.session.commit()

        # For Ferrari:
        auth_req_ferrari = AuthenticationRequest(
            item_id=auction11.item_id,
            requester_id=auction11.seller_id,
            request_date=now,
            fee_percent=5.00,
            status=2  # Authenticated
        )
        db.session.add(auth_req_ferrari)
        db.session.commit()
        expert_assignment_ferrari = ExpertAssignment(
            request_id=auth_req_ferrari.request_id,
            expert_id=user6.id,   # Assign Charlie for Ferrari
            assigned_date=now,
            status=2
        )
        db.session.add(expert_assignment_ferrari)
        db.session.commit()

        message_expert_ferrari1 = Message(
                authentication_request_id=auth_req_ferrari.request_id,
                sender_id=user6.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=1, minutes=30)
        )
        # Add seller message with image for Ferrari
        message_seller_ferrari = Message(
            authentication_request_id=auth_req_ferrari.request_id,
            sender_id=auction11.seller_id,
            message_text="Attached is a detailed image of my car's interior and exterior.",
            sent_at=now - timedelta(hours=1)
        )
        db.session.add_all([message_expert_ferrari1, message_seller_ferrari])
        db.session.commit()

        message_image_ferrari = MessageImage(
            message_id=message_seller_ferrari.message_id,
            image_key="message_attachments/20250321_130845_FERARIJPG.jpg"  # S3 key for the Ferrari image
        )
        db.session.add(message_image_ferrari)
        db.session.commit()

        # Add expert response for Ferrari
        message_expert_ferrari = Message(
            authentication_request_id=auth_req_ferrari.request_id,
            sender_id=user6.id,
            message_text="Thank you for the information. Your Ferrari has been authenticated.",
            sent_at=now - timedelta(minutes=15)
        )
        db.session.add(message_expert_ferrari)
        db.session.commit()

        # For Comic Book: mark authentication as denied
        auth_req_book = AuthenticationRequest(
            item_id=auction8.item_id,
            requester_id=auction8.seller_id,
            request_date=now,
            fee_percent=5.00,
            status=3  # 3 = Declined/Denied
        )
        db.session.add(auth_req_book)
        db.session.commit()

        expert_assignment_book = ExpertAssignment(
            request_id=auth_req_book.request_id,
            expert_id=user6.id,   # Assign Charlie
            assigned_date=now,
            status=2  # Mark assignment as completed/responded
        )
        db.session.add(expert_assignment_book)
        db.session.commit()

        message_expert_comic = Message(
                authentication_request_id=auth_req_book.request_id,
                sender_id=user6.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=2, minutes=30)
        )

        db.session.add(message_expert_comic)
        db.session.commit()

        # Add seller message with image for Comic Book
        message_seller_comic = Message(
            authentication_request_id=auth_req_book.request_id,
            sender_id=auction8.seller_id,
            message_text="Please see the attached image of my comic book.",
            sent_at=now - timedelta(hours=2)
        )
        db.session.add(message_seller_comic)
        db.session.commit()

        message_image_comic = MessageImage(
            message_id=message_seller_comic.message_id,
            image_key="message_attachments/20250322_132008_Dover.jpg"  # Replace with your S3 key for the comic image
        )
        db.session.add(message_image_comic)
        db.session.commit()

        # Add expert response for Comic Book
        message_expert_comic = Message(
            authentication_request_id=auth_req_book.request_id,
            sender_id=user6.id,
            message_text="The image you provided looks lovely. "
            "However, it is not the expected comic book. Authentication denied.",
            sent_at=now - timedelta(hours=1, minutes=30)
        )
        db.session.add(message_expert_comic)
        db.session.commit()

        # For Comic Book: mark authentication as denied
        auth_req_rolex = AuthenticationRequest(
            item_id=auction10.item_id,
            requester_id=auction10.seller_id,
            request_date=now,
            fee_percent=5.00,
            status=1 
        )
        db.session.add(auth_req_rolex)
        db.session.commit()

        expert_assignment_rolex = ExpertAssignment(
            request_id=auth_req_rolex.request_id,
            expert_id=user6.id,   # Assign Charlie
            assigned_date=now,
            status=1 
        )
        db.session.add(expert_assignment_rolex)
        db.session.commit()

        message_expert_rolex = Message(
                authentication_request_id=auth_req_rolex.request_id,
                sender_id=user6.id,
                message_text="Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.",
                sent_at=now - timedelta(hours=2, minutes=30)
        )

        db.session.add(message_expert_rolex)
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

        # Create availability for the new experts
        new_experts = [user15, user16, user17, user18]
        for expert in new_experts:
            for i in range(7):  # For the next 7 days
                day = date.today() + timedelta(days=i)
                availability = ExpertAvailability(
                    expert_id=expert.id,
                    day=day,
                    start_time=time(8, 0),
                    end_time=time(20, 0),
                    status=True
                )
                db.session.add(availability)
        db.session.commit()

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
                winner = db.session.get(User, highest.bidder_id)
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
                        other_user = db.session.get(User, bid.bidder_id)
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

        # Assign 5 random expertise categories to each expert
        all_categories = Category.query.all()
        experts = User.query.filter(User.role == 2).all()

        for expert in experts:
            # Get 5 unique categories randomly (if there are at least 5)
            if len(all_categories) >= 5:
                random_expertise = random.sample(all_categories, 5)
            else:
                random_expertise = all_categories
            for category in random_expertise:
                expert_category = ExpertCategory(expert_id=expert.id, category_id=category.id)
                db.session.add(expert_category)

        db.session.commit()


        print('Database populated with dummy data!')
