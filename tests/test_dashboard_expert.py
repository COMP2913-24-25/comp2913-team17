"""Test expert dashboard functionality."""

import pytest
import json
from datetime import datetime, timedelta
from main.models import db, User, Item, Category, AuthenticationRequest, ExpertAssignment, ExpertCategory
from tests.test_utils import (
    MockUser, logged_in_user, login_as, mock_login_user, 
    common_setup_database, verify_page_title, verify_element_exists, 
    clear_all_tables
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for expert dashboard tests"""
    test_data = {}
    
    with app.app_context():
        # Get existing users created by common_setup_database
        regular_user = User.query.filter_by(username="regular_user").first()
        expert_user = User.query.filter_by(username="expert_user").first()
        manager_user = User.query.filter_by(username="manager_user").first()
        
        # Create additional test users
        test_expert1 = User(username="test_expert1", email="testexpert1@test.com", role=2)
        test_expert1.set_password("Password@123")
        db.session.add(test_expert1)
        
        test_expert2 = User(username="test_expert2", email="testexpert2@test.com", role=2)
        test_expert2.set_password("Password@123")
        db.session.add(test_expert2)
        
        # Get or create categories
        antiques_category = Category.query.filter_by(name="Antiques").first()
        collectibles_category = Category.query.filter_by(name="Collectibles").first()
        
        # Create expertise records for test_expert1
        expert_category1 = ExpertCategory(
            expert_id=test_expert1.id,
            category_id=antiques_category.id
        )
        db.session.add(expert_category1)
        
        # Create test items
        test_item1 = Item(
            seller_id=regular_user.id,
            category_id=antiques_category.id,
            title="Test Antique Item",
            description="This is a test antique item for expert authentication",
            auction_start=datetime.now() - timedelta(days=2),
            auction_end=datetime.now() + timedelta(days=3),
            minimum_price=100.00
        )
        db.session.add(test_item1)
        db.session.flush()
        
        test_item2 = Item(
            seller_id=regular_user.id,
            category_id=collectibles_category.id,
            title="Test Collectible Item",
            description="This is a test collectible item for expert authentication",
            auction_start=datetime.now() - timedelta(days=1),
            auction_end=datetime.now() + timedelta(days=4),
            minimum_price=50.00
        )
        db.session.add(test_item2)
        db.session.flush()
        
        # Create pending authentication requests
        auth_request1 = AuthenticationRequest(
            item_id=test_item1.item_id,
            requester_id=regular_user.id,
            status=1
        )
        db.session.add(auth_request1)
        db.session.flush()
        
        auth_request2 = AuthenticationRequest(
            item_id=test_item2.item_id,
            requester_id=regular_user.id,
            status=1
        )
        db.session.add(auth_request2)
        db.session.flush()
        
        # Assign test_expert1 to auth_request1
        expert_assignment1 = ExpertAssignment(
            request_id=auth_request1.request_id,
            expert_id=test_expert1.id,
            status=1
        )
        db.session.add(expert_assignment1)
        
        # Create a completed authentication request
        completed_item = Item(
            seller_id=regular_user.id,
            category_id=antiques_category.id,
            title="Completed Antique Item",
            description="This is a completed authentication item",
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
        
        completed_assignment = ExpertAssignment(
            request_id=completed_auth.request_id,
            expert_id=test_expert1.id,
            status=2
        )
        db.session.add(completed_assignment)
        
        # Create a declined authentication request
        declined_item = Item(
            seller_id=regular_user.id,
            category_id=collectibles_category.id,
            title="Declined Collectible Item",
            description="This is a declined authentication item",
            auction_start=datetime.now() - timedelta(days=6),
            auction_end=datetime.now() + timedelta(days=2),
            minimum_price=150.00
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
        
        declined_assignment = ExpertAssignment(
            request_id=declined_auth.request_id,
            expert_id=test_expert1.id,
            status=2
        )
        db.session.add(declined_assignment)
        
        db.session.commit()
        
        # Store IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'test_expert1_id': test_expert1.id,
            'test_expert2_id': test_expert2.id,
            'antiques_category_id': antiques_category.id,
            'collectibles_category_id': collectibles_category.id,
            'test_item1_id': test_item1.item_id,
            'test_item2_id': test_item2.item_id,
            'auth_request1_id': auth_request1.request_id,
            'auth_request1_url': auth_request1.url,
            'auth_request2_id': auth_request2.request_id,
            'auth_request2_url': auth_request2.url,
            'completed_auth_id': completed_auth.request_id,
            'completed_auth_url': completed_auth.url,
            'declined_auth_id': declined_auth.request_id,
            'declined_auth_url': declined_auth.url
        }
    
    yield test_data

# Access tests
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
    """Test that regular users can't see the expert dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the user dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Dashboard' in dashboard_title.text
    assert 'Expert Dashboard' not in dashboard_title.text

@login_as(role=3)
def test_dashboard_access_as_manager_user(client, setup_database, soup):
    """Test that managers can't see the expert dashboard directly"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the manager dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Management Dashboard' in dashboard_title.text
    assert 'Expert Dashboard' not in dashboard_title.text

@login_as(role=2)
def test_dashboard_access_as_expert(client, setup_database, soup):
    """Test that experts can access the expert dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the expert dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Expert Dashboard' in dashboard_title.text

# Expert Dashboard UI
@login_as(role=2)
def test_expert_dashboard_tabs(client, setup_database, soup):
    """Test that the expert dashboard has required tabs"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check for all tabs
    tabs = page.find_all('a', class_='nav-link')
    tab_ids = [tab.get('id') for tab in tabs]
    
    assert 'expertise-tab' in tab_ids
    assert 'pending-tab' in tab_ids
    assert 'completed-tab' in tab_ids

@login_as(role=2, user_id=4, username="test_expert1")
def test_expert_dashboard_expertise_tab(client, setup_database, soup):
    """Test the expertise tab"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify expertise tab
    expertise_tab = page.find('div', id='expertise')
    assert expertise_tab is not None
    
    # Check for current expertise section
    current_expertise = expertise_tab.find('div', id='current-expertise')
    assert current_expertise is not None
    
    # Check for expertise form
    expertise_form = expertise_tab.find('form', id='expertise-form')
    assert expertise_form is not None
    
    # Check for select/deselect all buttons
    select_all_button = expertise_form.find('button', id='select-all')
    deselect_all_button = expertise_form.find('button', id='deselect-all')
    assert select_all_button is not None
    assert deselect_all_button is not None
    
    # Check for save changes button
    save_button = expertise_form.find('button', id='save-expertise')
    assert save_button is not None
    
    # Check for category checkboxes - at least 2 categories (Antiques and Collectibles)
    checkboxes = expertise_form.find_all('input', {'type': 'checkbox', 'name': 'expertise'})
    assert len(checkboxes) >= 2
    
    # Check that Antiques is checked (since test_expert1 has expertise in Antiques)
    antiques_checkbox = expertise_form.find('input', {'type': 'checkbox', 'value': str(setup_database['antiques_category_id'])})
    assert antiques_checkbox is not None
    assert antiques_checkbox.get('checked') is not None

@login_as(role=2, user_id=4, username="test_expert1")
def test_expert_dashboard_pending_tab(client, setup_database, soup):
    """Test the pending tab"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify pending tab
    pending_tab = page.find('div', id='pending')
    assert pending_tab is not None
    
    # Check for auth table
    auth_table = pending_tab.find('table', class_='auth-table')
    assert auth_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in auth_table.find_all('th')]
    assert 'Item' in headers
    assert 'Category' in headers
    assert 'Seller' in headers
    assert 'Auction Period' in headers
    assert 'Status' in headers
    assert 'Action' in headers
    
    # Check for pending rows
    pending_rows = auth_table.find_all('tr')[1:]
    assert len(pending_rows) > 0
    
    # Check for the pending item title
    test_item1_in_rows = False
    for row in pending_rows:
        item_title = row.find('td', class_='item-title').text.strip()
        if "Test Antique Item" in item_title:
            test_item1_in_rows = True
            
            # Check for PENDING status
            status_cell = row.find('div', class_='authentication-status')
            assert 'PENDING' in status_cell.text
            
            # Check for Review button
            review_button = row.find('a', class_='btn-accent')
            assert 'Review' in review_button.text
            assert 'authenticate' in review_button['href']
            
            break
            
    assert test_item1_in_rows

@login_as(role=2, user_id=4, username="test_expert1")
def test_expert_dashboard_completed_tab(client, setup_database, soup):
    """Test the completed tab"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify completed tab
    completed_tab = page.find('div', id='completed')
    assert completed_tab is not None
    
    # Check for auth table
    auth_table = completed_tab.find('table', class_='auth-table')
    assert auth_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in auth_table.find_all('th')]
    assert 'Item' in headers
    assert 'Category' in headers
    assert 'Seller' in headers
    assert 'Auction Period' in headers
    assert 'Status' in headers
    assert 'Action' in headers
    
    # Check for completed rows
    completed_rows = auth_table.find_all('tr')[1:]
    assert len(completed_rows) > 0
    
    # Check for completed status badges
    completed_found = False
    declined_found = False
    for row in completed_rows:
        status_cell = row.find('div', class_='authentication-status')
        if 'AUTHENTICATED' in status_cell.text:
            completed_found = True
        elif 'DECLINED' in status_cell.text:
            declined_found = True
        
        # Check for View button
        view_button = row.find('a', class_='btn-outline-dark')
        assert 'View' in view_button.text
        assert 'authenticate' in view_button['href']
    
    assert completed_found
    assert declined_found

@login_as(role=2, user_id=5, username="test_expert2")
def test_expert_dashboard_empty_states(client, setup_database, soup):
    """Test the empty states"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check pending tab empty state
    pending_tab = page.find('div', id='pending')
    pending_empty_state = pending_tab.find('div', class_='empty-state')
    assert pending_empty_state is not None
    assert 'No pending authentication requests' in pending_empty_state.text
    
    # Check completed tab empty state
    completed_tab = page.find('div', id='completed')
    completed_empty_state = completed_tab.find('div', class_='empty-state')
    assert completed_empty_state is not None
    assert 'You haven\'t completed any authentications yet' in completed_empty_state.text

# API Tests
@login_as(role=2, user_id=4, username="test_expert1")
def test_update_expertise_api(client, setup_database):
    """Test the API for updating an expert's expertise"""
    user_id = setup_database['test_expert1_id']
    antiques_id = setup_database['antiques_category_id']
    collectibles_id = setup_database['collectibles_category_id']
    
    # Update expertise to include both Antiques and Collectibles
    response = client.put(
        f'/dashboard/api/expert/{user_id}',
        data=json.dumps({'expertise': [antiques_id, collectibles_id]}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'expertise updated' in data['message'].lower()
    assert 'expertise' in data
    assert len(data['expertise']) == 2
    assert antiques_id in data['expertise']
    assert collectibles_id in data['expertise']
    
    # Verify the change in the database
    with client.application.app_context():
        expert_categories = ExpertCategory.query.filter_by(expert_id=user_id).all()
        category_ids = [ec.category_id for ec in expert_categories]
        assert len(category_ids) == 2
        assert antiques_id in category_ids
        assert collectibles_id in category_ids

@login_as(role=2, user_id=5, username="test_expert2")
def test_update_expertise_remove_all(client, setup_database):
    """Test removing all expertise categories"""
    user_id = setup_database['test_expert2_id']
    
    # Update expertise to empty list
    response = client.put(
        f'/dashboard/api/expert/{user_id}',
        data=json.dumps({'expertise': []}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'expertise updated' in data['message'].lower()
    assert 'expertise' in data
    assert len(data['expertise']) == 0
    
    # Verify the change in database
    with client.application.app_context():
        expert_categories = ExpertCategory.query.filter_by(expert_id=user_id).all()
        assert len(expert_categories) == 0

@login_as(role=1)
def test_update_expertise_unauthorised(client, setup_database):
    """Test that regular users can't update expertise"""
    user_id = setup_database['test_expert1_id']
    antiques_id = setup_database['antiques_category_id']
    
    response = client.put(
        f'/dashboard/api/expert/{user_id}',
        data=json.dumps({'expertise': [antiques_id]}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'unauthorised' in data['error'].lower()

@login_as(role=2, user_id=4, username="test_expert1")
def test_update_other_expert_expertise_unauthorised(client, setup_database):
    """Test that experts can't update another expert's expertise"""
    # Try to update test_expert2's expertise
    user_id = setup_database['test_expert2_id']
    antiques_id = setup_database['antiques_category_id']
    
    response = client.put(
        f'/dashboard/api/expert/{user_id}',
        data=json.dumps({'expertise': [antiques_id]}),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'error' in data
    assert 'cannot modify' in data['error'].lower() or 'unauthorised' in data['error'].lower() 