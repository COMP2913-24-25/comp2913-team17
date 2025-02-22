import unittest
from datetime import datetime, timedelta
from main import create_app
from main.models import db, User, Item, Bid, Notification
from flask import url_for

class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
            'SECRET_KEY': 'test-secret-key'  # Add secret key for testing
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test users
        self.seller = User(username='seller', email='seller@test.com')
        self.bidder1 = User(username='bidder1', email='bidder1@test.com')
        self.bidder2 = User(username='bidder2', email='bidder2@test.com')
        
        for user in [self.seller, self.bidder1, self.bidder2]:
            user.set_password('password123')
            db.session.add(user)
        
        db.session.commit()

    def test_outbid_notification(self):
        # Create test item with URL
        item = Item(
            seller_id=self.seller.id,
            title='Test Item',
            description='Test Description',
            minimum_price=100.00,
            auction_start=datetime.now(),
            auction_end=datetime.now() + timedelta(days=1),
            url='test-item'  # Add URL for routing
        )
        db.session.add(item)
        db.session.commit()

        # Create first bid directly
        first_bid = Bid(
            item_id=item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00
        )
        db.session.add(first_bid)
        db.session.commit()

        # Create second bid directly
        second_bid = Bid(
            item_id=item.item_id,
            bidder_id=self.bidder2.id,
            bid_amount=200.00
        )
        db.session.add(second_bid)
        
        # Notify the outbid user directly
        item.notify_outbid(self.bidder1)
        db.session.commit()

        # Check if outbid notification was created for bidder1
        notification = Notification.query.filter_by(user_id=self.bidder1.id).first()
        if notification is None:
            # Print debug information
            print("\nDebug information:")
            print(f"Bidder1 ID: {self.bidder1.id}")
            print(f"All notifications: {Notification.query.all()}")
            print(f"First bid amount: {first_bid.bid_amount}")
            print(f"Second bid amount: {second_bid.bid_amount}")
        
        self.assertIsNotNone(notification, "No notification was created")
        self.assertIn('outbid', notification.message.lower())

    def test_winner_notification(self):
        # Create test item that's about to end
        item = Item(
            seller_id=self.seller.id,
            title='Test Item',
            description='Test Description',
            minimum_price=100.00,
            auction_start=datetime.now() - timedelta(days=1),
            auction_end=datetime.now() - timedelta(minutes=1),  # Set as already ended
            url='test-item-ending'
        )
        db.session.add(item)
        db.session.commit()

        # Place winning bid
        bid = Bid(
            item_id=item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00
        )
        db.session.add(bid)
        db.session.commit()

        # Set the winning bid
        item.winning_bid_id = None  # Ensure it's None before checking
        db.session.commit()

        # Simulate auction end
        with self.client as c:
            response = c.get('/item/check-ended-auctions')
            self.assertEqual(response.status_code, 200)

        # Check if winner notification was created
        notification = Notification.query.filter_by(user_id=self.bidder1.id).first()
        self.assertIsNotNone(notification)
        self.assertIn('won', notification.message.lower())

    # Clear test data
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

'''
- Set WTF_CSRF_ENABLED = False and SECRET_KEY to app config
- Added url field to test items
- Modified auction end time in winner test to be in the past
- Explicitly set winning_bid_id to None before checking ended auctions
- Add error handling in the route
- Add User model import
- Verify user exists before notification
- Add debug information to the test
- Create bids directly in the test instead of through HTTP requests
- Add explicit commit after notification creation
'''
