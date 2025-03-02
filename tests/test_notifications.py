import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from main import create_app
from main.models import db, User, Item, Bid, Notification

class TestNotificationsSystem(unittest.TestCase):
    @patch('main.socket_events.socketio')
    def setUp(self, mock_socketio):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Mock socketio for testing
        self.mock_socketio = mock_socketio
        
        # Create database tables
        db.create_all()
        
        # Create test users
        self.seller = User(username='seller', email='seller@test.com', role=1)
        self.seller.set_password('password123')
        
        self.bidder1 = User(username='bidder1', email='bidder1@test.com', role=1)
        self.bidder1.set_password('password123')
        
        self.bidder2 = User(username='bidder2', email='bidder2@test.com', role=1)
        self.bidder2.set_password('password123')
        
        db.session.add_all([self.seller, self.bidder1, self.bidder2])
        db.session.commit()
        
        # Create test item
        now = datetime.now()
        self.item = Item(
            seller_id=self.seller.id,
            title='Test Item',
            description='Test Description',
            minimum_price=100.00,
            upload_date=now,
            auction_start=now,
            auction_end=now + timedelta(days=1),
            authentication_status=1
        )
        db.session.add(self.item)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_notification_model_has_required_fields(self):
        """Test that Notification model has all required fields"""
        notification = Notification(
            user_id=self.bidder1.id,
            message="Test notification",
            item_url=self.item.url,
            item_title=self.item.title,
            notification_type=1
        )
        db.session.add(notification)
        db.session.commit()
        
        retrieved = Notification.query.get(notification.id)
        self.assertEqual(retrieved.user_id, self.bidder1.id)
        self.assertEqual(retrieved.message, "Test notification")
        self.assertEqual(retrieved.item_url, self.item.url)
        self.assertEqual(retrieved.item_title, self.item.title)
        self.assertEqual(retrieved.notification_type, 1)
        self.assertFalse(retrieved.is_read)
        self.assertIsNotNone(retrieved.created_at)
    
    def test_notification_type_field_exists(self):
        """Test notification type field exists and works correctly"""
        notification = Notification(
            user_id=self.bidder1.id,
            message="Test notification",
            notification_type=2  # Winner notification
        )
        db.session.add(notification)
        db.session.commit()
        
        retrieved = Notification.query.get(notification.id)
        self.assertEqual(retrieved.notification_type, 2)
    
    def test_outbid_notification_creation(self):
        """Test notification is created when a user is outbid"""
        # Add initial bid
        bid1 = Bid(
            item_id=self.item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00,
            bid_time=datetime.now()
        )
        db.session.add(bid1)
        db.session.commit()
        
        # Add higher bid
        bid2 = Bid(
            item_id=self.item.item_id,
            bidder_id=self.bidder2.id,
            bid_amount=160.00,
            bid_time=datetime.now()
        )
        db.session.add(bid2)
        
        # Notify the outbid user
        self.item.notify_outbid(self.bidder1)
        
        # Check notification was created
        notification = Notification.query.filter_by(
            user_id=self.bidder1.id,
            notification_type=1
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.item_url, self.item.url)
        self.assertEqual(notification.item_title, self.item.title)
        self.assertFalse(notification.is_read)
    
    def test_winner_notification_creation(self):
        """Test notification is created for auction winner"""
        # Add winning bid
        bid = Bid(
            item_id=self.item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00,
            bid_time=datetime.now()
        )
        db.session.add(bid)
        db.session.commit()
        
        # Set winning bid and notify
        self.item.winning_bid_id = bid.bid_id
        self.item.notify_winner()
        
        # Check notification was created
        notification = Notification.query.filter_by(
            user_id=self.bidder1.id,
            notification_type=2
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.item_url, self.item.url)
        self.assertEqual(notification.item_title, self.item.title)
        self.assertFalse(notification.is_read)
        self.assertIn("Congratulations", notification.message)
    
    def test_mark_notifications_as_read(self):
        """Test marking notifications as read"""
        # Create unread notification
        notification = Notification(
            user_id=self.bidder1.id,
            message="Test notification",
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        # Log in as bidder1
        with self.client as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.bidder1.id)
            
            # Make request to mark notifications as read
            response = client.post('/item/notifications/mark-read')
            
            # Check response and database
            self.assertEqual(response.status_code, 200)
            updated_notification = Notification.query.get(notification.id)
            self.assertTrue(updated_notification.is_read)
    
    def test_realtime_notification(self):
        """Test real-time notification is sent via SocketIO"""
        # Create a notification and trigger real-time notification
        self.item.notify_outbid(self.bidder1)
        
        # Check that socketio.emit was called
        self.mock_socketio.emit.assert_called_once()
        call_args = self.mock_socketio.emit.call_args[0]
        self.assertEqual(call_args[0], 'new_notification')
        self.assertIn('message', call_args[1])
        self.assertIn('item_url', call_args[1])
    
    def test_javascript_file_loading(self):
        """Test that notification JavaScript files are loaded"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'notifications.js', response.data)
        self.assertIn(b'realtime-notifications.js', response.data)
    
    def test_notifications_appear_in_dropdown(self):
        """Test that notifications appear in navbar dropdown"""
        # Create notification
        notification = Notification(
            user_id=self.bidder1.id,
            message="Test notification",
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        # Log in as bidder1
        with self.client as client:
            with client.session_transaction() as session:
                session['_user_id'] = str(self.bidder1.id)
            
            # Request home page with navbar
            response = client.get('/')
            
            # Check for notification elements in HTML
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Notifications', response.data)
            self.assertIn(b'dropdown-menu', response.data)
    
    def test_auction_finalization(self):
        """Test auction finalization process creates notifications"""
        # Add bid
        bid = Bid(
            item_id=self.item.item_id,
            bidder_id=self.bidder1.id,
            bid_amount=150.00,
            bid_time=datetime.now()
        )
        db.session.add(bid)
        db.session.commit()
        
        # Set auction end to past time
        self.item.auction_end = datetime.now() - timedelta(hours=1)
        db.session.commit()
        
        # Call finalization method
        self.item.finalise_auction()
        
        # Check that winner notification was created
        notification = Notification.query.filter_by(
            user_id=self.bidder1.id,
            notification_type=2
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(self.item.winning_bid_id, bid.bid_id)