"""Test utilities for common test functions."""

import flask_login
from functools import wraps
from contextlib import contextmanager
import datetime
import json
from main.models import db, User, Category, Item, Image, Bid, Notification, Message, MessageImage, AuthenticationRequest, ExpertAssignment, ExpertAvailability
import uuid
import pytest

def clear_all_tables(db_session):
    """Clear all tables in the correct order to avoid foreign key issues"""
    tables_in_order = [
        MessageImage, Message, AuthenticationRequest, ExpertAssignment, ExpertAvailability,
        Bid, Image, Item, Category, User, Notification
    ]
    
    for table in tables_in_order:
        db_session.query(table).delete()
    
    db_session.commit()

@contextmanager
def db_transaction():
    """Context manager for database transactions that rolls back on exception"""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

class MockUser:
    """Mock user class for testing Flask-Login functionality"""

    def __init__(self, id=None, username=None, is_authenticated=True, role=1):
        self.id = id
        self.username = username
        self.email = f"{username}@test.com" if username else "user@test.com"
        self.is_authenticated = is_authenticated
        self.role = role
        self.is_active = True
        self.is_anonymous = False
        self.failed_login_attempts = 0
        self.locked_until = None
        self.secret_key = "mock_secret_key"

    def get_id(self):
        """Return user ID as string"""
        return str(self.id)
        
    def check_password(self, password):
        """Mock password check that returns True for 'Password@123', False otherwise"""
        return password == "Password@123"
        
    def reset_login_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
        
    def increment_login_attempts(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        
    def is_account_locked(self):
        """Check if account is locked"""
        return False

@contextmanager
def logged_in_user(client, user, remember=False):
    """Context manager for testing as a logged-in user"""
    # Store original function
    original_get_user = flask_login.utils._get_user

    try:
        # Replace with our mock function
        flask_login.utils._get_user = lambda: user
        yield
    finally:
        # Restore original function
        flask_login.utils._get_user = original_get_user

def login_as(role, user_id=1, username="testuser"):
    """Decorator to run a test function with a specific user role logged in"""
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(client, *args, **kwargs):
            # Create mock user
            mock_user = MockUser(id=user_id, username=username, is_authenticated=True, role=role)

            # Store original function
            original_get_user = flask_login.utils._get_user

            try:
                # Replace with our mock function
                flask_login.utils._get_user = lambda: mock_user

                # Run the test
                return test_func(client, *args, **kwargs)
            finally:
                # Restore original function
                flask_login.utils._get_user = original_get_user

        return wrapper
    return decorator

def mock_login_user(monkeypatch, user):
    """Mock the flask_login.current_user functionality"""
    monkeypatch.setattr('flask_login.utils._get_user', lambda: user)

class JsonResponseWrapper:
    """Wrapper for Flask test response with JSON data"""

    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.data = response.data
        
        if response.headers.get('Content-Type', '').startswith('application/json'):
            self.json = json.loads(response.data)
        else:
            self.json = None

class JsonClient:
    """Wrapper for the Flask test client that handles JSON data"""
    
    def __init__(self, client):
        self.client = client
    
    def get(self, url, **kwargs):
        """Make a GET request with Accept: application/json header"""
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Accept', 'application/json')
        response = self.client.get(url, **kwargs)
        return JsonResponseWrapper(response)
    
    def post(self, url, data=None, **kwargs):
        """Make a POST request with JSON data"""
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')
        
        if data is not None and not isinstance(data, str):
            data = json.dumps(data)
        
        response = self.client.post(url, data=data, **kwargs)
        return JsonResponseWrapper(response)

# Authentication helper functions
def login_user(client, email="user@test.com", password="Password@123"):
    """Log in a user via the login form"""
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def register_user(client, username="testuser", email="newuser@test.com", password="Password123!", confirm_password="Password123!"):
    """Register a new user via the registration form"""
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm_password
    }, follow_redirects=True)

def logout_user(client):
    """Log out the current user"""
    return client.get('/logout', follow_redirects=True)

def update_username(client, new_username, current_password="Password@123"):
    """Update user's username"""
    return client.post('/update_user', data={
        'new_username': new_username,
        'current_password': current_password,
        'submit': 'Update Username'
    }, follow_redirects=True)

def update_email(client, new_email, current_password="Password@123"):
    """Update user's email"""
    return client.post('/update_user', data={
        'new_email': new_email,
        'current_password': current_password,
        'submit': 'Update Email'
    }, follow_redirects=True)

def update_password(client, current_password="Password@123", new_password="NewPassword123!", confirm_password="NewPassword123!"):
    """Update user's password"""
    return client.post('/update_user', data={
        'current_password': current_password,
        'new_password': new_password,
        'confirm_password': confirm_password,
        'submit': 'Update Password'
    }, follow_redirects=True)

def create_test_categories():
    """Create test categories for testing"""
    categories = [
        Category(name="Antiques", description="Vintage and antique items"),
        Category(name="Collectibles", description="Rare and collectible items"),
        Category(name="Luxury Goods", description="High-end designer items and luxury products"),
        Category(name="Miscellaneous", description="Items that don't fit other categories")
    ]
    
    for category in categories:
        db.session.add(category)
    db.session.commit()
    
    return categories

def create_test_users():
    """Create test users with different roles"""
    users = [
        User(username="regular_user", email="user@test.com", role=1),
        User(username="expert_user", email="expert@test.com", role=2),
        User(username="manager_user", email="manager@test.com", role=3)
    ]
    
    for user in users:
        user.set_password("Password@123")
        db.session.add(user)
    db.session.commit()
    
    return users

def create_test_items(users, categories, count=5):
    """Create test auction items"""
    items = []
    now = datetime.datetime.now()
    
    for i in range(count):
        # Alternate between ongoing and ended auctions
        is_ended = i % 2 == 0
        auction_end = now - datetime.timedelta(days=1) if is_ended else now + datetime.timedelta(days=i+1)
        
        # Assign to different users and categories
        user_index = i % len(users)
        category_index = i % len(categories)
        
        item = Item(
            seller_id=users[user_index].id,
            category_id=categories[category_index].id,
            url=uuid.uuid4().hex,
            title=f"Test Item {i+1}",
            description=f"This is a test item description for item {i+1}",
            auction_start=now - datetime.timedelta(days=3),
            auction_end=auction_end,
            minimum_price=10.00 + (i * 5),
            auction_completed=is_ended
        )
        
        # Add an image to some items
        if i % 2 == 0:
            image = Image(
                url=f"https://example.com/image{i}.jpg"
            )
            item.images.append(image)
        
        # For some items, add bids
        if i % 3 == 0:
            bid = Bid(
                bidder_id=users[(i+1) % len(users)].id,
                bid_amount=20.00 + (i * 8)
            )
            item.bids.append(bid)
        
        db.session.add(item)
        items.append(item)
    
    db.session.commit()
    return items

def setup_test_data(app):
    """Set up all test data for the database"""
    with app.app_context():
        # Clear existing data without dropping tables
        clear_all_tables(db.session)
        
        users = create_test_users()
        categories = create_test_categories()
        items = create_test_items(users, categories)
        
        return {
            'users': users,
            'categories': categories,
            'items': items
        }

def clean_test_data(app):
    """Clean up test data after tests"""
    with app.app_context():
        # Clear the data but don't drop tables
        clear_all_tables(db.session)

def ensure_test_user_exists(app, email="user@test.com", username="regular_user"):
    """Ensure that a specific test user exists in the database"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, role=1)
            user.set_password("Password@123")
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.add(user)
            db.session.commit()
        return user

def reset_database_for_test(app):
    """Create a clean database state for tests that need an empty database"""
    with app.app_context():
        # Clear all data
        clear_all_tables(db.session)
        
        # Add a single default category
        category = Category(name="Test Category", description="Test Description")
        db.session.add(category)
        db.session.commit()
        
        return category

@pytest.fixture(scope="module")
def common_setup_database(app):
    """Common database setup fixture that can be reused across test files"""
    with app.app_context():
        # Clear existing data without dropping tables
        clear_all_tables(db.session)
        
        # Create test users
        users = [
            User(username="regular_user", email="user@test.com", role=1),
            User(username="expert_user", email="expert@test.com", role=2),
            User(username="manager_user", email="manager@test.com", role=3)
        ]
        
        for user in users:
            user.set_password("Password@123")
            db.session.add(user)
        
        # Create test categories
        categories = [
            Category(name="Antiques", description="Vintage and antique items"),
            Category(name="Collectibles", description="Rare and collectible items")
        ]
        
        for category in categories:
            db.session.add(category)
            
        db.session.commit()
    
    yield
    
    # Clean up after all tests
    with app.app_context():
        clear_all_tables(db.session)

def verify_page_title(soup, expected_text):
    """Verify that a page title contains the expected text"""
    assert expected_text in soup.title.string

def verify_form_exists(soup, form_name=None, form_id=None, form_method=None):
    """Verify that a form with given attributes exists on the page"""
    form_attrs = {}
    if form_name:
        form_attrs['name'] = form_name
    if form_id:
        form_attrs['id'] = form_id
    if form_method:
        form_attrs['method'] = form_method
    
    form = soup.find('form', attrs=form_attrs)
    assert form is not None
    return form

def verify_form_field(form, field_name=None, field_id=None, field_type=None):
    """Verify that a form field with given attributes exists in the form"""
    field_attrs = {}
    if field_name:
        field_attrs['name'] = field_name
    if field_id:
        field_attrs['id'] = field_id
    if field_type:
        field_attrs['type'] = field_type
    
    field = form.find('input', attrs=field_attrs)
    assert field is not None
    return field

def verify_element_exists(soup, element_type, attrs=None, string=None):
    """Verify that an element or string exists on the page"""
    element = soup.find(element_type, attrs=attrs, string=string)
    assert element is not None
    return element

def verify_flash_message(soup, message_class, expected_text):
    """Verify that a flash message with the given class and text exists on the page"""
    flash_message = soup.find('div', class_=message_class)
    assert flash_message is not None
    assert expected_text in flash_message.text
    return flash_message
