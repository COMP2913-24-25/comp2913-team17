import unittest
from flask import url_for
from datetime import datetime, timedelta
import os

from main import create_app, db
from main.models import User, Item, WatchedItem
from tests.uitls import register_user, login_user, logout_user, create_item  # Fixed typo in import


class TestWatchAuction(unittest.TestCase):
    def setUp(self):
        # Set environment variable to disable scheduler before creating app
        os.environ['TESTING'] = 'True'
        
        # Create app
        self.app = create_app()
        
        # Configure app for testing
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Explicitly disable the scheduler if your app has a direct attribute
        if hasattr(self.app, 'scheduler'):
            self.app.scheduler.shutdown(wait=False)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        
        # Create test user
        self.test_user = register_user(self.client, 'test@example.com', 'password123')
        login_user(self.client, 'test@example.com', 'password123')
        
        # Create another user for testing
        self.other_user = User(
            email='other@example.com',
            name='Other User',
            password='password123',
            confirmed=True
        )
        db.session.add(self.other_user)
        
        # Create test items
        self.item1 = create_item(
            title="Test Item 1",
            description="Description for test item 1",
            starting_price=10.00,
            auction_end=datetime.now() + timedelta(days=1),
            seller_id=self.other_user.id
        )
        
        self.item2 = create_item(
            title="Test Item 2",
            description="Description for test item 2",
            starting_price=20.00,
            auction_end=datetime.now() + timedelta(days=2),
            seller_id=self.other_user.id
        )
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        # Clear the testing environment variable
        os.environ.pop('TESTING', None)

    def test_watch_item(self):
        """Test watching an auction item"""
        response = self.client.post(f'/item/{self.item1.url}/watch')
        self.assertEqual(response.status_code, 200)
        
        # Check if watch was added to database
        watch = WatchedItem.query.filter_by(
            user_id=self.test_user.id,
            item_id=self.item1.item_id
        ).first()
        self.assertIsNotNone(watch)

    def test_unwatch_item(self):
        """Test unwatching an auction item"""
        # First watch an item
        watch = WatchedItem(user_id=self.test_user.id, item_id=self.item1.item_id)
        db.session.add(watch)
        db.session.commit()
        
        # Then unwatch it
        response = self.client.post(f'/item/{self.item1.url}/unwatch')
        self.assertEqual(response.status_code, 200)
        
        # Check if watch was removed from database
        watch = WatchedItem.query.filter_by(
            user_id=self.test_user.id,
            item_id=self.item1.item_id
        ).first()
        self.assertIsNone(watch)

    def test_view_item_watch_status(self):
        """Test that watch status is correctly displayed on item page"""
        # First watch an item
        watch = WatchedItem(user_id=self.test_user.id, item_id=self.item1.item_id)
        db.session.add(watch)
        db.session.commit()
        
        # View the item page
        response = self.client.get(f'/item/{self.item1.url}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unwatch', response.data)  # Should show unwatch button
        
        # View an unwatched item
        response = self.client.get(f'/item/{self.item2.url}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Watch', response.data)  # Should show watch button

    def test_dashboard_watched_items(self):
        """Test that watched items appear on user dashboard"""
        # Watch both items
        watch1 = WatchedItem(user_id=self.test_user.id, item_id=self.item1.item_id)
        watch2 = WatchedItem(user_id=self.test_user.id, item_id=self.item2.item_id)
        db.session.add(watch1)
        db.session.add(watch2)
        db.session.commit()
        
        # Check dashboard
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Item 1', response.data)
        self.assertIn(b'Test Item 2', response.data)
        self.assertIn(b'Watched Auctions', response.data)


if __name__ == '__main__':
    unittest.main()