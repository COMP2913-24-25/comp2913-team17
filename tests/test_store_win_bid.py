import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import boto3
from main.models import db, Item, User, Bid, Notification
from main import create_app

class TestAuctionWinner(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test users with all required fields
        self.seller = User(
            username='seller',
            email='seller@test.com',
            role=1,
            created_at=datetime.now()
        )
        self.seller.set_password('password123')

        self.bidder1 = User(
            username='bidder1',
            email='bidder1@test.com',
            role=1,
            created_at=datetime.now()
        )
        self.bidder1.set_password('password123')

        self.bidder2 = User(
            username='bidder2',
            email='bidder2@test.com',
            role=1,
            created_at=datetime.now()
        )
        self.bidder2.set_password('password123')

        db.session.add_all([self.seller, self.bidder1, self.bidder2])
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_winning_bid_storage(self):
        """Test if winning bid is correctly stored"""
        now = datetime.now()
        
        # Create a test item
        item = Item(
            seller_id=self.seller.id,
            title='Test Item',
            description='Test Description',
            minimum_price=100.00,
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=1),
            authentication_status=1
        )
        db.session.add(item)
        db.session.commit()

        # Create test bid
        bid1 = Bid(
            item_id=item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00,
            bid_time=now
        )
        db.session.add(bid1)
        db.session.commit()

        # Refresh item from database
        db.session.refresh(item)
        
        # Assert the winning bid
        self.assertEqual(item.highest_bid().bid_id, bid1.bid_id)