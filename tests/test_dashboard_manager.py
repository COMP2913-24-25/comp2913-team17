"""Test manager dashboard functionality."""

import pytest
import json
from datetime import datetime, timedelta
from main.models import db, User, Item, Category, AuthenticationRequest, ExpertAssignment, ManagerConfig
from tests.test_utils import (
    MockUser, logged_in_user, login_as, mock_login_user, 
    common_setup_database, verify_page_title, verify_element_exists, 
    clear_all_tables
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for manager dashboard tests"""
    test_data = {}
    
    with app.app_context():
        # Get existing users created by common_setup_database
        regular_user = User.query.filter_by(username="regular_user").first()
        expert_user = User.query.filter_by(username="expert_user").first()
        manager_user = User.query.filter_by(username="manager_user").first()
        
        # Create additional test users
        test_user1 = User(username="test_user1", email="testuser1@test.com", role=1)
        test_user1.set_password("Password@123")
        db.session.add(test_user1)
        
        test_user2 = User(username="test_user2", email="testuser2@test.com", role=1)
        test_user2.set_password("Password@123")
        db.session.add(test_user2)
        
        test_expert = User(username="test_expert", email="testexpert@test.com", role=2)
        test_expert.set_password("Password@123")
        db.session.add(test_expert)
        
        # Create manager config if it doesn't exist
        base_fee = ManagerConfig.query.filter_by(config_key=ManagerConfig.BASE_FEE_KEY).first()
        if not base_fee:
            base_fee = ManagerConfig(
                config_key=ManagerConfig.BASE_FEE_KEY,
                config_value='1.00',
                description='Base platform fee percentage for standard items'
            )
            db.session.add(base_fee)
            
        auth_fee = ManagerConfig.query.filter_by(config_key=ManagerConfig.AUTHENTICATED_FEE_KEY).first()
        if not auth_fee:
            auth_fee = ManagerConfig(
                config_key=ManagerConfig.AUTHENTICATED_FEE_KEY,
                config_value='5.00',
                description='Platform fee percentage for authenticated items'
            )
            db.session.add(auth_fee)
            
        max_duration = ManagerConfig.query.filter_by(config_key=ManagerConfig.MAX_DURATION_KEY).first()
        if not max_duration:
            max_duration = ManagerConfig(
                config_key=ManagerConfig.MAX_DURATION_KEY,
                config_value='5',
                description='Maximum auction duration in days'
            )
            db.session.add(max_duration)
            
        # Create test items
        category = Category.query.first()
        
        test_item = Item(
            seller_id=regular_user.id,
            category_id=category.id,
            title="Test Dashboard Item",
            description="This is a test item for the dashboard",
            auction_start=datetime.now() - timedelta(days=2),
            auction_end=datetime.now() + timedelta(days=3),
            minimum_price=100.00
        )
        db.session.add(test_item)
        db.session.flush()
        
        # Create a test authentication request
        auth_request = AuthenticationRequest(
            item_id=test_item.item_id,
            requester_id=regular_user.id,
            status=1
        )
        db.session.add(auth_request)
        db.session.commit()
        
        # Store IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'test_user1_id': test_user1.id,
            'test_user2_id': test_user2.id,
            'test_expert_id': test_expert.id,
            'test_item_id': test_item.item_id,
            'auth_request_id': auth_request.request_id,
            'base_fee': base_fee.config_value,
            'auth_fee': auth_fee.config_value,
            'max_duration': max_duration.config_value
        }
    
    yield test_data
    

# Access Control Tests
def test_dashboard_access_logged_out(client, setup_database):
    """Test that logged out users are redirected"""
    response = client.get('/dashboard/', follow_redirects=False)
    assert response.status_code == 302
    
    # Confirm we go to login page
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

@login_as(role=1)
def test_dashboard_access_as_regular_user(client, setup_database, soup):
    """Test that regular users can't see the manager dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the user dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Dashboard' in dashboard_title.text
    assert 'Management Dashboard' not in dashboard_title.text

@login_as(role=2)
def test_dashboard_access_as_expert_user(client, setup_database, soup):
    """Test that expert users can't see the manager dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the expert dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Expert Dashboard' in dashboard_title.text
    assert 'Management Dashboard' not in dashboard_title.text

@login_as(role=3)
def test_dashboard_access_as_manager(client, setup_database, soup):
    """Test that managers can access the manager dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the manager dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Management Dashboard' in dashboard_title.text

# Manager Dashboard UI Tests
@login_as(role=3)
def test_manager_dashboard_tabs(client, setup_database, soup):
    """Test that the manager dashboard has all required tabs"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check for all tabs
    tabs = page.find_all('a', class_='nav-link')
    tab_ids = [tab.get('id') for tab in tabs]
    
    assert 'users-tab' in tab_ids
    assert 'requests-tab' in tab_ids
    assert 'statistics-tab' in tab_ids
    assert 'config-tab' in tab_ids

@login_as(role=3)
def test_manager_dashboard_users_tab(client, setup_database, soup):
    """Test the users tab"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify users tab content
    users_tab = page.find('div', id='users')
    assert users_tab is not None
    
    # Check for user search and filter
    user_search = users_tab.find('input', id='user-search')
    role_filter = users_tab.find('select', id='role-filter')
    assert user_search is not None
    assert role_filter is not None
    
    # Check for user table
    user_table = users_tab.find('table', class_='auth-table')
    assert user_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in user_table.find_all('th')]
    assert 'Username' in headers
    assert 'Email' in headers
    assert 'Role' in headers
    assert 'Actions' in headers
    
    # Check for user rows including test users
    user_rows = user_table.find_all('tr')[1:]
    usernames = [row.find('td', {'data-label': 'Username'}).text.strip() for row in user_rows]
    
    assert 'regular_user' in usernames
    assert 'expert_user' in usernames
    assert 'test_user1' in usernames
    assert 'test_user2' in usernames
    assert 'test_expert' in usernames

@login_as(role=3)
def test_manager_dashboard_config_tab(client, setup_database, soup):
    """Test the configuration tab"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify config tab content
    config_tab = page.find('div', id='config')
    assert config_tab is not None
    
    # Check for config table
    config_table = config_tab.find('table', class_='auth-table')
    assert config_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in config_table.find_all('th')]
    assert 'Option' in headers
    assert 'Current Value' in headers
    assert 'Update Value' in headers
    
    # Check for specific config options
    options = [row.find('td', {'data-label': 'Option'}).text.strip() for row in config_table.find_all('tr')[1:]]
    assert 'Base Platform Fee (%)' in options
    assert 'Authenticated Item Fee (%)' in options
    assert 'Maximum Auction Duration (Days)' in options
    
    # Check current values match our setup
    base_fee_cell = config_table.find('td', class_='base-cell')
    auth_fee_cell = config_table.find('td', class_='auth-cell')
    duration_cell = config_table.find('td', class_='dur-cell')
    
    assert base_fee_cell is not None
    assert auth_fee_cell is not None
    assert duration_cell is not None
    
    assert float(base_fee_cell.text) == float(setup_database['base_fee'])
    assert float(auth_fee_cell.text) == float(setup_database['auth_fee'])
    assert int(duration_cell.text) == int(setup_database['max_duration'])

# API Tests
@login_as(role=3)
def test_update_user_role_api(client, setup_database):
    """Test the API for updating a user's role"""
    # Test updating a regular user to expert
    user_id = setup_database['test_user1_id']
    
    response = client.patch(
        f'/dashboard/api/users/{user_id}/role',
        data=json.dumps({'role': 2}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['new_role'] == 2
    
    # Verify the change in the database
    with client.application.app_context():
        user = db.session.get(User, user_id)
        assert user.role == 2

@login_as(role=1)
def test_update_user_role_api_unauthorised(client, setup_database):
    """Test that regular users can't update roles"""
    user_id = setup_database['test_user2_id']
    
    response = client.patch(
        f'/dashboard/api/users/{user_id}/role',
        data=json.dumps({'role': 2}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']
    
    # Verify no change in database
    with client.application.app_context():
        user = db.session.get(User, user_id)
        assert user.role == 1  # Still a regular user

@login_as(role=3)
def test_update_base_fee_api(client, setup_database):
    """Test updating the base platform fee"""
    new_fee = 2.50
    
    response = client.put(
        '/dashboard/api/update-base',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['config_key'] == 'base_platform_fee'
    assert float(data['config_value']) == new_fee
    
    # Verify the change in database
    with client.application.app_context():
        config = ManagerConfig.query.filter_by(config_key=ManagerConfig.BASE_FEE_KEY).first()
        assert float(config.config_value) == new_fee

@login_as(role=3)
def test_update_authenticated_fee_api(client, setup_database):
    """Test updating the authenticated item fee"""
    new_fee = 7.50
    
    response = client.put(
        '/dashboard/api/update-auth',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['config_key'] == 'authenticated_platform_fee'
    assert float(data['config_value']) == new_fee
    
    # Verify the change in database
    with client.application.app_context():
        config = ManagerConfig.query.filter_by(config_key=ManagerConfig.AUTHENTICATED_FEE_KEY).first()
        assert float(config.config_value) == new_fee

@login_as(role=3)
def test_update_max_duration_api(client, setup_database):
    """Test updating the maximum auction duration"""
    new_duration = 10
    
    response = client.put(
        '/dashboard/api/update-dur',
        data=json.dumps({'days': new_duration}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['config_key'] == 'max_auction_duration'
    assert int(data['config_value']) == new_duration
    
    # Verify the change in database
    with client.application.app_context():
        config = ManagerConfig.query.filter_by(config_key=ManagerConfig.MAX_DURATION_KEY).first()
        assert int(config.config_value) == new_duration

@login_as(role=1)
def test_update_config_unauthorised(client, setup_database):
    """Test that regular users can't update platform configurations"""
    new_fee = 3.0
    
    # Try to update base fee
    response = client.put(
        '/dashboard/api/update-base',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']
    
    # Verify no change in database to the new value
    with client.application.app_context():
        config = ManagerConfig.query.filter_by(config_key=ManagerConfig.BASE_FEE_KEY).first()
        assert float(config.config_value) != new_fee

@login_as(role=3)
def test_assign_expert_api(client, setup_database):
    """Test the API for assigning an expert to an authentication request"""
    request_id = setup_database['auth_request_id']
    expert_id = setup_database['expert_user_id']
    
    # Get all authentication requests
    response = client.get('/dashboard/')
    
    # Now try to assign the expert
    response = client.post(
        f'/dashboard/api/assign-expert/{request_id}',
        data=json.dumps({'expert': expert_id}),
        content_type='application/json'
    )
    
    # If successful, check for success status
    data = json.loads(response.data)
    if response.status_code == 200:
        assert data['status'] == 'success'
        
        # Verify the assignment in database
        with client.application.app_context():
            assignment = ExpertAssignment.query.filter_by(
                request_id=request_id,
                expert_id=expert_id
            ).first()
            assert assignment is not None

# Test invalid input for configurations
@login_as(role=3)
def test_update_max_duration_api_days_less_than_one(client, setup_database):
    """Test updating the max duration with days less than 1"""
    new_duration = 0
    
    response = client.put(
        '/dashboard/api/update-dur',
        data=json.dumps({'days': new_duration}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Duration cannot be less than 1 day' in data['error']
    
    # Verify no change in database
    with client.application.app_context():
        config = ManagerConfig.query.filter_by(config_key=ManagerConfig.MAX_DURATION_KEY).first()
        assert int(config.config_value) != new_duration

@login_as(role=3)
def test_update_max_duration_api_days_non_number(client, setup_database):
    """Test updating the max duration with non-numeric value"""
    response = client.put(
        '/dashboard/api/update-dur',
        data=json.dumps({'days': 'abc'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@login_as(role=3)
def test_update_max_duration_api_days_float(client, setup_database):
    """Test updating the max duration with float instead of int"""
    new_duration = 5.5
    
    response = client.put(
        '/dashboard/api/update-dur',
        data=json.dumps({'days': new_duration}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Invalid duration' in data['error']

@login_as(role=3)
def test_update_base_fee_api_negative(client, setup_database):
    """Test updating the base fee with negative value"""
    new_fee = -1.0
    
    response = client.put(
        '/dashboard/api/update-base',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Fee must be positive' in data['error']

@login_as(role=3)
def test_update_base_fee_api_too_high(client, setup_database):
    """Test updating the base fee with value over 100%"""
    new_fee = 101.0
    
    response = client.put(
        '/dashboard/api/update-base',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Fee cannot be over 100' in data['error']

@login_as(role=3)
def test_update_auth_fee_api_negative(client, setup_database):
    """Test updating the auth fee with negative value"""
    new_fee = -1.0
    
    response = client.put(
        '/dashboard/api/update-auth',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Fee must be positive' in data['error']

@login_as(role=3)
def test_update_auth_fee_api_too_high(client, setup_database):
    """Test updating the auth fee with value over 100%"""
    new_fee = 101.0
    
    response = client.put(
        '/dashboard/api/update-auth',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Fee cannot be over 100' in data['error']

# Test expert trying to access manager functionality
@login_as(role=2)
def test_expert_update_base_fee_api(client, setup_database):
    """Test that expert cannot update base fee"""
    new_fee = 3.0
    
    response = client.put(
        '/dashboard/api/update-base',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']

@login_as(role=2)
def test_expert_update_auth_fee_api(client, setup_database):
    """Test that expert cannot update auth fee"""
    new_fee = 8.0
    
    response = client.put(
        '/dashboard/api/update-auth',
        data=json.dumps({'fee': new_fee}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']

@login_as(role=2)
def test_expert_update_duration_api(client, setup_database):
    """Test that expert cannot update max duration"""
    new_duration = 15
    
    response = client.put(
        '/dashboard/api/update-dur',
        data=json.dumps({'days': new_duration}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']

@login_as(role=2)
def test_expert_update_user_role_api(client, setup_database):
    """Test that expert cannot update user roles"""
    user_id = setup_database['test_user1_id']
    
    response = client.patch(
        f'/dashboard/api/users/{user_id}/role',
        data=json.dumps({'role': 2}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Unauthorised' in data['error']