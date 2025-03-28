"""Test authenticate item functionality."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO
from main.models import db, User, Item, Category, AuthenticationRequest, ExpertAssignment, Message, Notification
from tests.test_utils import (
    MockUser, logged_in_user, login_as, mock_login_user, setup_test_data, clean_test_data,
    common_setup_database, verify_page_title, verify_element_exists, 
    clear_all_tables, db_transaction, reset_database_for_test
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for authentication item tests"""
    test_data = {}
    
    with app.app_context():
        regular_user = User.query.filter_by(username="regular_user").first()
        expert_user = User.query.filter_by(username="expert_user").first()
        manager_user = User.query.filter_by(username="manager_user").first()
        
        # Create a test item
        test_item = Item(
            seller_id=regular_user.id,
            category_id=Category.query.first().id,
            title="Test Authentication Item",
            description="This is a test item for authentication",
            auction_start=datetime.now() - timedelta(days=5),
            auction_end=datetime.now() + timedelta(days=5),
            minimum_price=100.00
        )
        db.session.add(test_item)
        db.session.flush()
        
        # Create a pending test authentication request
        auth_request = AuthenticationRequest(
            item_id=test_item.item_id,
            requester_id=regular_user.id,
            status=1
        )
        db.session.add(auth_request)
        db.session.flush()
        
        # Assign the expert to the authentication request
        expert_assignment = ExpertAssignment(
            request_id=auth_request.request_id,
            expert_id=expert_user.id,
            status=1
        )
        db.session.add(expert_assignment)
        
        # Create a message in the authentication request
        message = Message(
            authentication_request_id=auth_request.request_id,
            sender_id=regular_user.id,
            message_text="Hello, I would like to authenticate this item."
        )
        db.session.add(message)
        
        # Create another test item with a completed authentication
        completed_item = Item(
            seller_id=regular_user.id,
            category_id=Category.query.first().id,
            title="Completed Authentication Item",
            description="This is a test item with completed authentication",
            auction_start=datetime.now() - timedelta(days=5),
            auction_end=datetime.now() + timedelta(days=5),
            minimum_price=200.00
        )
        db.session.add(completed_item)
        db.session.flush()
        
        completed_auth = AuthenticationRequest(
            item_id=completed_item.item_id,
            requester_id=regular_user.id,
            status=2
        )
        db.session.add(completed_auth)
        db.session.flush()
        
        # Assign the expert to the completed authentication request
        completed_assignment = ExpertAssignment(
            request_id=completed_auth.request_id,
            expert_id=expert_user.id,
            status=2
        )
        db.session.add(completed_assignment)
        
        # Create a declined authentication request
        declined_item = Item(
            seller_id=regular_user.id,
            category_id=Category.query.first().id,
            title="Declined Authentication Item",
            description="This is a test item with declined authentication",
            auction_start=datetime.now() - timedelta(days=5),
            auction_end=datetime.now() + timedelta(days=5),
            minimum_price=300.00
        )
        db.session.add(declined_item)
        db.session.flush()
        
        declined_auth = AuthenticationRequest(
            item_id=declined_item.item_id,
            requester_id=regular_user.id,
            status=3
        )
        db.session.add(declined_auth)
        db.session.flush()
        
        # Assign the expert to the declined authentication request
        declined_assignment = ExpertAssignment(
            request_id=declined_auth.request_id,
            expert_id=expert_user.id,
            status=2
        )
        db.session.add(declined_assignment)
        
        db.session.commit()
        
        # Store IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'test_item_id': test_item.item_id,
            'auth_request_id': auth_request.request_id,
            'auth_request_url': auth_request.url,
            'completed_auth_url': completed_auth.url,
            'declined_auth_url': declined_auth.url
        }
    
    yield test_data

def create_mock_image():
    """Create a mock image file for testing file uploads"""
    return FileStorage(
        stream=BytesIO(b"mock image content"),
        filename="test_image.jpg",
        content_type="image/jpeg"
    )

# Tests for authentication page access
def test_auth_page_access_as_creator(client, setup_database, soup):
    """Test accessing authentication page as the requester"""
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get(f"/authenticate/{setup_database['auth_request_url']}")
    assert response.status_code == 200
    
    page = soup(response.data)
    verify_page_title(page, "Authenticate: Test Authentication Item")
    
    # Check that the authentication status is shown
    status_badge = page.find('span', class_='badge')
    assert "Authentication Pending" in status_badge.text
    
    # Check that the message form is present
    message_form = page.find('form', id='message-form')
    assert message_form is not None
    
    # Check that expert options are not present
    expert_options = page.find('div', class_='expert-menu')
    assert expert_options is None

def test_auth_page_access_as_expert(client, setup_database, soup):
    """Test accessing authentication page as the assigned expert"""
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    response = client.get(f"/authenticate/{setup_database['auth_request_url']}")
    assert response.status_code == 200
    
    page = soup(response.data)
    verify_page_title(page, "Authenticate: Test Authentication Item")
    
    # Check that the expert options are present
    expert_options = page.find('div', class_='expert-menu')
    assert expert_options is not None
    
    # Verify the expert buttons
    authenticate_btn = expert_options.find('button', id='authenticate-item')
    decline_btn = expert_options.find('button', id='decline-item')
    reassign_btn = expert_options.find('button', id='reassign-item')
    
    assert authenticate_btn is not None
    assert decline_btn is not None
    assert reassign_btn is not None

def test_auth_page_access_as_manager(client, setup_database, soup):
    """Test accessing authentication page as a manager"""
    with client.session_transaction() as sess:
        with client.application.app_context():
            manager = User.query.filter_by(id=setup_database['manager_user_id']).first()
            sess['_user_id'] = str(manager.id)
    
    response = client.get(f"/authenticate/{setup_database['auth_request_url']}")
    assert response.status_code == 200
    
    page = soup(response.data)
    verify_page_title(page, "Authenticate: Test Authentication Item")
    
    # Check that the messages are shown but manager can't send messages
    messages_div = page.find('div', class_='messages')
    assert messages_div is not None
    
    # Manager should not see message form or expert options
    message_form = page.find('form', id='message-form')
    expert_options = page.find('div', class_='expert-menu')
    
    assert message_form is None
    assert expert_options is None

def test_auth_page_access_denied(client, setup_database, soup):
    """Test that unauthorised users can't access the authentication page"""
    # Create a different regular user
    with client.application.app_context():
        other_user = User(
            username="other_user",
            email="other@test.com",
            role=1
        )
        other_user.set_password("Password@123")
        db.session.add(other_user)
        db.session.commit()
        
        # Login as this other user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(other_user.id)
    
    # Try without following redirects
    response = client.get(f"/authenticate/{setup_database['auth_request_url']}")
    
    # Response should be a redirect
    assert response.status_code == 302
    response = client.get(f"/authenticate/{setup_database['auth_request_url']}", follow_redirects=True)
    page = soup(response.data)
    
    # Should redirect to home with error message
    verify_page_title(page, "Vintage Vault")
    alert = page.find('div', class_='alert-danger')
    assert alert is not None
    assert "not authorised" in alert.text.lower()
    
    # Clean up
    with client.application.app_context():
        db.session.delete(other_user)
        db.session.commit()

# Tests for different authentication statuses
def test_completed_authentication_display(client, setup_database, soup):
    """Test that completed authentication is displayed correctly"""
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get(f"/authenticate/{setup_database['completed_auth_url']}")
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check that the authentication status is shown
    status_badge = page.find('span', class_='badge', string=lambda string: string and "Authenticated" in string)
    assert status_badge is not None
    
    # No message form should be present for completed auth
    message_form = page.find('form', id='message-form')
    assert message_form is None

def test_declined_authentication_display(client, setup_database, soup):
    """Test that declined authentication is displayed correctly"""
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    response = client.get(f"/authenticate/{setup_database['declined_auth_url']}")
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check that the authentication status is shown
    status_badge = page.find('span', class_='badge', string=lambda string: string and "Authentication Declined" in string)
    assert status_badge is not None
    
    # No message form should be present for declined auth
    message_form = page.find('form', id='message-form')
    assert message_form is None

# Tests for messaging functionality
@patch('main.page_authenticate_item.routes.upload_s3')
@patch('main.page_authenticate_item.routes.socketio')
def test_send_message_as_creator(mock_socketio, mock_upload_s3, client, setup_database):
    """Test sending a message as the creator"""
    mock_upload_s3.return_value = "test_image_key"
    mock_socketio.emit = MagicMock()
    
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Create data for message POST request
    message_data = {
        'content': 'This is a test message from the creator'
    }
    
    # Send message
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/message", 
        data=message_data,
        follow_redirects=True
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    assert 'Your message has been sent.' in response_data['success']
    
    # Verify message was saved in database
    with client.application.app_context():
        message = Message.query.filter_by(
            authentication_request_id=setup_database['auth_request_id'],
            message_text='This is a test message from the creator'
        ).first()
        
        assert message is not None
        assert message.sender_id == setup_database['regular_user_id']

@patch('main.page_authenticate_item.routes.upload_s3')
@patch('main.page_authenticate_item.routes.socketio')
def test_send_message_as_expert(mock_socketio, mock_upload_s3, client, setup_database):
    """Test sending a message as the expert"""
    mock_upload_s3.return_value = "test_image_key"
    mock_socketio.emit = MagicMock()
    
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    # Create data for message POST request
    message_data = {
        'content': 'This is a test message from the expert'
    }
    
    # Send message
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/message", 
        data=message_data,
        follow_redirects=True
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    assert 'Your message has been sent.' in response_data['success']
    
    # Verify message was saved in database
    with client.application.app_context():
        message = Message.query.filter_by(
            authentication_request_id=setup_database['auth_request_id'],
            message_text='This is a test message from the expert'
        ).first()
        
        assert message is not None
        assert message.sender_id == setup_database['expert_user_id']

@patch('main.page_authenticate_item.routes.upload_s3')
@patch('main.page_authenticate_item.routes.socketio')
def test_send_message_with_image(mock_socketio, mock_upload_s3, client, setup_database):
    """Test sending a message with an image attachment"""
    mock_upload_s3.return_value = "test_image_key"
    mock_socketio.emit = MagicMock()
    
    # Login as creator
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Create mock image file
    mock_image = create_mock_image()
    
    # Create data for message POST request with image file
    data = {}
    data['content'] = 'This is a test message with an image'
    
    # Send message with file
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/message", 
        data=data,
        buffered=True,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    assert 'Your message has been sent.' in response_data['success']
    
    # Verify message was saved in database
    with client.application.app_context():
        message = Message.query.filter_by(
            authentication_request_id=setup_database['auth_request_id'],
            message_text='This is a test message with an image'
        ).first()
        
        assert message is not None

def test_send_message_to_completed_auth(client, setup_database):
    """Test that messages can't be sent to completed authentication requests"""
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Create data for message POST request
    message_data = {
        'content': 'This should not be accepted'
    }
    
    # Send message to completed auth
    response = client.post(
        f"/authenticate/{setup_database['completed_auth_url']}/api/message", 
        data=message_data,
        follow_redirects=True
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert 'Authentication request is not pending.' in response_data['error']

# Tests for expert actions
@patch('main.page_authenticate_item.routes.socketio')
def test_expert_accept_authentication(mock_socketio, client, setup_database):
    """Test expert accepting an authentication request"""
    mock_socketio.emit = MagicMock()
    
    # Reset authentication status to pending
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        auth_request.status = 1
        
        # Reset expert assignment
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assignment.status = 1
        
        db.session.commit()
    
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/accept", 
        follow_redirects=True
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    assert 'Authentication request accepted.' in response_data['success']
    
    # Verify authentication status was updated
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        assert auth_request.status == 2
        
        # Verify expert assignment was updated
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assert assignment.status == 2
        
        # Verify notification was created
        notification = Notification.query.filter_by(
            user_id=setup_database['regular_user_id'],
            notification_type=4
        ).order_by(Notification.created_at.desc()).first()
        
        assert notification is not None
        assert "authenticated" in notification.message.lower()

@patch('main.page_authenticate_item.routes.socketio')
@patch('main.page_authenticate_item.routes.send_notification_email')
def test_expert_decline_authentication(mock_email, mock_socketio, client, setup_database):
    """Test expert declining an authentication request"""
    mock_socketio.emit = MagicMock()
    mock_email.return_value = None
    
    # Reset authentication status to pending
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        auth_request.status = 1
        
        # Reset expert assignment
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assignment.status = 1  # Notified
        
        # Clear any existing notifications
        notifications = Notification.query.filter_by(
            user_id=setup_database['regular_user_id'],
            notification_type=4
        ).all()
        for notif in notifications:
            db.session.delete(notif)
            
        db.session.commit()
    
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/decline", 
        follow_redirects=True
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    assert 'Authentication request rejected.' in response_data['success']
    
    # Verify authentication status was updated
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        assert auth_request.status == 3
        
        # Verify expert assignment was updated
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assert assignment.status == 2
        
        # Check that the notification was created
        notification = Notification.query.filter_by(
            user_id=setup_database['regular_user_id'],
            notification_type=4
        ).order_by(Notification.created_at.desc()).first()
        
        assert notification is not None

def test_expert_reassign_authentication(client, setup_database):
    """Test expert reassigning an authentication request"""
    # Reset authentication status to pending
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        auth_request.status = 1
        
        # Reset expert assignment
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assignment.status = 1
        
        db.session.commit()
    
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/reassign", 
        follow_redirects=True
    )
    
    # Check if response is successful
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'success' in response_data
    
    # Verify authentication status remains pending
    with client.application.app_context():
        auth_request = AuthenticationRequest.query.filter_by(request_id=setup_database['auth_request_id']).first()
        assert auth_request.status == 1
        
        # Verify expert assignment was updated to reassigned
        assignment = ExpertAssignment.query.filter_by(request_id=auth_request.request_id).first()
        assert assignment.status == 3

# Test unauthorised actions
def test_creator_cannot_authenticate(client, setup_database):
    """Test that a requester cannot authenticate their own item"""
    # Login as requester
    with client.session_transaction() as sess:
        with client.application.app_context():
            user = User.query.filter_by(id=setup_database['regular_user_id']).first()
            sess['_user_id'] = str(user.id)
    
    # Try to authenticate as requester
    response = client.post(
        f"/authenticate/{setup_database['auth_request_url']}/api/accept", 
        follow_redirects=True
    )
    
    # Check that the response is unauthorised
    assert response.status_code in [401, 403]
    response_data = json.loads(response.data)
    assert 'error' in response_data

def test_expert_cannot_authenticate_completed(client, setup_database):
    """Test that an expert cannot re-authenticate a completed request"""
    # Login as expert
    with client.session_transaction() as sess:
        with client.application.app_context():
            expert = User.query.filter_by(id=setup_database['expert_user_id']).first()
            sess['_user_id'] = str(expert.id)
    
    # Try to re-authenticate a completed request
    response = client.post(
        f"/authenticate/{setup_database['completed_auth_url']}/api/accept", 
        follow_redirects=True
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert 'Authentication request is not pending.' in response_data['error'] 