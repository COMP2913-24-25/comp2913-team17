"""Test auction creation functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from werkzeug.datastructures import FileStorage
from io import BytesIO
from main.models import User, Item, Category, AuthenticationRequest
from tests.test_utils import (
    MockUser, login_as, mock_login_user, setup_test_data, clean_test_data,
    common_setup_database, verify_page_title, verify_element_exists, 
    verify_form_exists, verify_form_field, clear_all_tables, db_transaction
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for create item tests"""
    test_data = {}
    
    with app.app_context():
        # Get users with different roles
        regular_user = User.query.filter_by(username="regular_user").first()
        expert_user = User.query.filter_by(username="expert_user").first()
        manager_user = User.query.filter_by(username="manager_user").first()
        
        # Store the IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'category_id': Category.query.first().id
        }
    
    yield test_data

def create_mock_image(filename="test_image.jpg", content_type="image/jpeg"):
    """Create a mock image file for testing file uploads"""
    return FileStorage(
        stream=BytesIO(b"mock image content"),
        filename=filename,
        content_type=content_type
    )

# Access tests
def test_create_page_access_as_regular_user(client, setup_database, soup):
    """Test that regular users can access the create page"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get('/create/')
    assert response.status_code == 200
    
    page = soup(response.data)
    verify_page_title(page, "Create Auction")
    
    # Check that the form exists
    form = verify_form_exists(page, form_id='create-auction-form')
    assert form is not None

def test_create_page_denied_for_expert(client, setup_database):
    """Test that experts cannot access the create page"""
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    response = client.get('/create/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that the response is unauthorised
    assert b'Only general users can create auctions' in response.data

def test_create_page_denied_for_manager(client, setup_database):
    """Test that managers cannot access the create page"""
    # Login as manager
    with client.session_transaction() as sess:
        with client.application.app_context():
            manager = User.query.filter_by(id=setup_database['manager_user_id']).first()
            sess['_user_id'] = str(manager.id)
    
    response = client.get('/create/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that the response is unauthorised
    assert b'Only general users can create auctions' in response.data

def test_create_page_requires_login(client):
    """Test that unauthenticated users are redirected to login"""
    # Clear any existing session
    with client.session_transaction() as sess:
        if '_user_id' in sess:
            del sess['_user_id']
    
    response = client.get('/create/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

# Form validation tests
def test_create_form_fields_present(client, setup_database, soup):
    """Test that all required fields are present in the form"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get('/create/')
    assert response.status_code == 200
    
    page = soup(response.data)
    form = page.find('form', id='create-auction-form')
    
    # Check for fields
    assert form.find('input', {'id': 'enter-title'}) is not None
    assert form.find('select', {'id': 'category_id'}) is not None
    assert form.find('textarea', {'id': 'enter-description'}) is not None
    assert form.find('input', {'id': 'enter-end-time'}) is not None
    assert form.find('input', {'id': 'enter-price'}) is not None
    assert form.find('input', {'id': 'upload-images'}) is not None
    assert form.find('input', {'id': 'authenticate-item'}) is not None
    assert form.find('input', {'id': 'submit-auction'}) is not None

def test_form_validation_missing_required_fields(client, setup_database, soup):
    """Test form validation catches missing required fields"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Submit form with missing fields
    response = client.post('/create/', data={
        'title': '',
        'category_id': '',
        'description': '',
        'auction_end': '',
        'minimum_price': '10.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    page = soup(response.data)
    
    # Check for error messages
    assert page.find(string=lambda text: 'required' in text.lower() if text else False) is not None

def test_form_validation_title_too_short(client, setup_database, soup):
    """Test form validation for title that's too short"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Submit form with short title
    response = client.post('/create/', data={
        'title': 'Short',
        'category_id': setup_database['category_id'],
        'description': 'This is a valid description for testing purposes.',
        'auction_end': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '10.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Title must be' in response.data

def test_form_validation_description_too_short(client, setup_database, soup):
    """Test form validation for description that's too short"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Submit form with short description
    response = client.post('/create/', data={
        'title': 'This is a valid title for testing purposes',
        'category_id': setup_database['category_id'],
        'description': 'Short',
        'auction_end': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '10.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Description must be at least' in response.data

def test_form_validation_auction_end_in_past(client, setup_database, soup):
    """Test form validation for auction end date in the past"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Submit form with past end date
    response = client.post('/create/', data={
        'title': 'This is a valid title for testing purposes',
        'category_id': setup_database['category_id'],
        'description': 'This is a valid description for testing purposes.',
        'auction_end': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '10.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Auction end must occur after' in response.data

def test_form_validation_auction_duration_too_short(client, setup_database, soup):
    """Test form validation for auction duration that's too short"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Submit form with short duration (less than 1 hour)
    response = client.post('/create/', data={
        'title': 'This is a valid title for testing purposes',
        'category_id': setup_database['category_id'],
        'description': 'This is a valid description for testing purposes.',
        'auction_end': (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '10.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Auction duration must be at least an hour' in response.data

# File upload and auction creation tests
@patch('main.page_create.routes.upload_s3')
def test_create_auction_success(mock_upload_s3, client, setup_database):
    """Test successful auction creation"""
    mock_upload_s3.return_value = "https://example.com/test_image.jpg"
    
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Count items before creation
    with client.application.app_context():
        item_count_before = Item.query.count()
    
    # Create mock image
    mock_image = create_mock_image()
    
    # Submit valid form with image
    response = client.post('/create/', data={
        'title': 'This is a valid title for testing purposes',
        'category_id': setup_database['category_id'],
        'description': 'This is a valid description for testing purposes.',
        'auction_end': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '10.00',
        'images': [mock_image],
        'authenticate_item': False
    }, follow_redirects=True, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'Auction created successfully' in response.data
    
    # Verify item was created
    with client.application.app_context():
        assert Item.query.count() == item_count_before + 1
        # Get the latest item
        latest_item = Item.query.order_by(Item.item_id.desc()).first()
        assert latest_item.title == 'This is a valid title for testing purposes'
        assert latest_item.seller_id == setup_database['regular_user_id']
        
        # Verify image was added
        assert len(latest_item.images) > 0

@patch('main.page_create.routes.upload_s3')
def test_create_auction_with_authentication(mock_upload_s3, client, setup_database):
    """Test auction creation with authentication request"""
    mock_upload_s3.return_value = "https://example.com/test_image.jpg"
    
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Count auth requests before creation
    with client.application.app_context():
        auth_count_before = AuthenticationRequest.query.count()
    
    # Create mock image
    mock_image = create_mock_image()
    
    # Submit valid form with authentication request
    response = client.post('/create/', data={
        'title': 'Authentication test item',
        'category_id': setup_database['category_id'],
        'description': 'This is a test item that needs authentication.',
        'auction_end': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': '20.00',
        'images': [mock_image],
        'authenticate_item': True
    }, follow_redirects=True, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert b'Auction created successfully' in response.data
    
    # Verify auth request was created
    with client.application.app_context():
        assert AuthenticationRequest.query.count() == auth_count_before + 1
        # Get the latest item and auth request
        latest_item = Item.query.filter_by(title='Authentication test item').first()
        auth_request = AuthenticationRequest.query.filter_by(item_id=latest_item.item_id).first()
        
        assert auth_request is not None
        assert auth_request.requester_id == setup_database['regular_user_id']
        assert auth_request.status == 1

def test_fees_displayed_correctly(client, setup_database, soup):
    """Test that platform fees are correctly displayed"""
    # Login as regular user
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get('/create/')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check for fee display
    fee_text = page.find(string=lambda text: 'platform fee' in text.lower() if text else False)
    assert fee_text is not None
    
    # Check for authentication fee meta element
    auth_fee_meta = page.find('meta', {'name': 'auth-fee'})
    assert auth_fee_meta is not None
    assert auth_fee_meta.get('content') is not None 