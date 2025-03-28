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
        self.watched_items = MockWatchlist()

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

class MockWatchlist:
    """Mock watchlist class for testing watched_items functionality"""
    
    def __init__(self):
        self.items = []
        
    def all(self):
        """Return all items in watchlist"""
        return self.items
        
    def append(self, item):
        """Add an item to watchlist"""
        if item not in self.items:
            self.items.append(item)
        
    def remove(self, item):
        """Remove an item from watchlist"""
        if item in self.items:
            self.items.remove(item)
            
    def __contains__(self, item):
        """Check if item is in watchlist"""
        return item in self.items

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

# Item page helper functions
def place_bid(client, item_url, bid_amount):
    """Place a bid on an item"""
    return client.post(f'/item/{item_url}/bid', 
        data=json.dumps({'bid_amount': bid_amount}),
        content_type='application/json')

def watch_item(client, item_url):
    """Add an item to user's watchlist"""
    return client.post(f'/item/{item_url}/watch')

def unwatch_item(client, item_url):
    """Remove an item from user's watchlist"""
    return client.post(f'/item/{item_url}/unwatch')

def create_payment_intent(client, item_url):
    """Create a payment intent for an item"""
    return client.post(f'/item/{item_url}/create-payment-intent')

def mark_as_won(client, item_url):
    """Mark an item as won after payment"""
    return client.post(f'/item/{item_url}/mark-won')

def create_test_item_with_authentication(users, categories, authenticated=False, url=None):
    """Create a test item with authentication request"""
    now = datetime.datetime.now()
    item_url = url or uuid.uuid4().hex
    
    # Create the item
    item = Item(
        seller_id=users[0].id,
        category_id=categories[0].id,
        url=item_url,
        title=f"Authenticated Test Item",
        description="This is a test item with authentication",
        auction_start=now - datetime.timedelta(days=1),
        auction_end=now + datetime.timedelta(days=1),
        minimum_price=100.00,
        auction_completed=False
    )
    db.session.add(item)
    db.session.commit()
    
    # Add an authentication request
    auth_request = AuthenticationRequest(
        url=uuid.uuid4().hex,
        item_id=item.id,
        status=2 if authenticated else 1
    )
    db.session.add(auth_request)
    db.session.commit()
    
    return item, auth_request

def create_bid_sequence(item, users, start_amount=10.0, count=3, increment=5.0):
    """Create a sequence of bids on an item"""
    bids = []
    amount = start_amount
    now = datetime.datetime.now()
    
    for i in range(count):
        # Skip the seller
        user_index = (i % (len(users) - 1)) + 1 
        bid_time = now - datetime.timedelta(hours=(count-i))
        
        bid = Bid(
            bidder_id=users[user_index].id,
            bid_amount=amount,
            bid_time=bid_time,
            item_id=item.id
        )
        db.session.add(bid)
        bids.append(bid)
        amount += increment
    
    db.session.commit()
    return bids

def verify_auction_display(soup, item):
    """Verify that the auction display shows correct item information"""
    # Check title
    title = verify_element_exists(soup, 'h1', {'class': 'auction-page-title'})
    assert item.title.lower() in title.text.lower()
    
    # Check seller info
    seller_info = soup.find(string=lambda text: 'Posted by:' in text if text else False)
    assert seller_info is not None
    assert item.seller.username in seller_info
    
    # Check description
    description = soup.find(string=lambda text: item.description in text if text else False)
    assert description is not None
    
    # Check category
    category_badge = verify_element_exists(soup, 'span', {'class': 'badge bg-info'})
    assert item.category.name in category_badge.text
    
    return True

def verify_price_display(soup, item):
    """Verify that the price display shows correct information"""
    price_section = verify_element_exists(soup, 'div', {'id': 'price-section'})
    
    if item.bids:
        highest_bid = max([bid.bid_amount for bid in item.bids])
        assert f"£{highest_bid:.2f}" in price_section.text
        assert "Highest Bid" in price_section.text
    else:
        assert f"£{item.minimum_price:.2f}" in price_section.text
        assert "Starting Price" in price_section.text
    
    return True

def verify_countdown_display(soup, item):
    """Verify that the countdown display shows correct information"""
    now = datetime.datetime.now()
    
    if now < item.auction_end:
        # Auction is ongoing
        countdown = verify_element_exists(soup, 'span', {'class': 'countdown'})
        assert countdown is not None
        
        end_date_text = soup.find(string=lambda text: 'Auction ends:' in text if text else False)
        assert end_date_text is not None
    else:
        # Auction has ended
        ended_text = soup.find(string=lambda text: 'Auction Ended:' in text if text else False)
        assert ended_text is not None
    
    return True

# Manager expert availability helper functions
def verify_availability_table(soup, experts, day):
    """Verify that the availability table shows correct expert information"""
    table = soup.find('table', id='dailyTable')
    assert table is not None
    
    # Check that each expert is in the table
    for expert in experts:
        expert_cell = table.find('td', string=expert.username)
        assert expert_cell is not None
    
    return True

def verify_weekly_table(soup, experts, days):
    """Verify that the weekly table shows correct expert information"""
    table = soup.find('table', id='weeklyTable')
    assert table is not None
    
    # Check that each expert is in the table
    for expert in experts:
        expert_cell = table.find('td', string=expert.username)
        assert expert_cell is not None
    
    # Check that each day is in the header
    headers = table.find_all('th')
    for day in days:
        day_format = day.strftime('%a, %b %d')
        header_present = any(day_format in header.get_text() for header in headers)
        assert header_present
    
    return True

def create_test_expert_availability(app, expert_id, days=None, available=True):
    """Create test availability records for an expert"""
    with app.app_context():
        if days is None:
            # Default to today and tomorrow
            today = datetime.date.today()
            days = [today, today + datetime.timedelta(days=1)]
        
        records = []
        for day in days:
            # Create availability record for 8am to 8pm
            record = ExpertAvailability(
                expert_id=expert_id,
                day=day,
                start_time=datetime.time(8, 0),
                end_time=datetime.time(20, 0),
                status=available
            )
            db.session.add(record)
            records.append(record)
        
        db.session.commit()
        return records