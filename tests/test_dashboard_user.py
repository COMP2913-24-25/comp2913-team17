"""Test user dashboard functionality."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from main.models import db, User, Item, Category, Bid, AuthenticationRequest, Image
from tests.test_utils import (
    MockUser, logged_in_user, login_as, mock_login_user, 
    common_setup_database, verify_page_title, verify_element_exists, 
    clear_all_tables
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for user dashboard tests"""
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
        
        # Get or create categories
        antiques_category = Category.query.filter_by(name="Antiques").first()
        collectibles_category = Category.query.filter_by(name="Collectibles").first()
        
        # Item 1: Active auction created by test_user1
        active_item = Item(
            seller_id=test_user1.id,
            category_id=antiques_category.id,
            title="Active Test Item",
            description="This is an active auction item created by test_user1",
            auction_start=datetime.now() - timedelta(days=2),
            auction_end=datetime.now() + timedelta(days=5),
            minimum_price=50.00
        )
        db.session.add(active_item)
        db.session.flush()
        
        # Add an image to item 1
        active_image = Image(
            item_id=active_item.item_id,
            url="https://example.com/image1.jpg"
        )
        db.session.add(active_image)
        
        # Item 2: Authenticated auction created by test_user1
        auth_item = Item(
            seller_id=test_user1.id,
            category_id=collectibles_category.id,
            title="Authenticated Test Item",
            description="This is an authenticated auction item created by test_user1",
            auction_start=datetime.now() - timedelta(days=3),
            auction_end=datetime.now() + timedelta(days=4),
            minimum_price=100.00
        )
        db.session.add(auth_item)
        db.session.flush()
        
        # Create approved authentication request for auth_item
        auth_request = AuthenticationRequest(
            item_id=auth_item.item_id,
            requester_id=test_user1.id,
            status=2
        )
        db.session.add(auth_request)
        
        # Item 3: Item created by regular_user that test_user1 is bidding on
        bidding_item = Item(
            seller_id=regular_user.id,
            category_id=antiques_category.id,
            title="Bidding Test Item",
            description="This is an item test_user1 is bidding on",
            auction_start=datetime.now() - timedelta(days=1),
            auction_end=datetime.now() + timedelta(days=6),
            minimum_price=75.00
        )
        db.session.add(bidding_item)
        db.session.flush()
        
        # Create a bid from test_user1 on bidding_item
        bid1 = Bid(
            item_id=bidding_item.item_id,
            bidder_id=test_user1.id,
            bid_amount=80.00
        )
        db.session.add(bid1)
        
        # Create a higher bid from test_user2 on bidding_item
        bid2 = Bid(
            item_id=bidding_item.item_id,
            bidder_id=test_user2.id,
            bid_amount=85.00
        )
        db.session.add(bid2)
        
        # Item 4: Item created by regular_user that test_user1 won (auction ended, highest bidder)
        won_item = Item(
            seller_id=regular_user.id,
            category_id=collectibles_category.id,
            title="Won Test Item",
            description="This is an item test_user1 has won",
            auction_start=datetime.now() - timedelta(days=10),
            auction_end=datetime.now() - timedelta(days=1),
            minimum_price=120.00,
            auction_completed=True,
            status=2
        )
        db.session.add(won_item)
        db.session.flush()
        
        # Create a winning bid from test_user1 on won_item
        winning_bid = Bid(
            item_id=won_item.item_id,
            bidder_id=test_user1.id,
            bid_amount=130.00
        )
        db.session.add(winning_bid)
        db.session.flush()
        
        # Set winning bid for won_item
        won_item.winning_bid_id = winning_bid.bid_id
        
        # Item 5: Item created by regular_user that test_user1 paid for
        paid_item = Item(
            seller_id=regular_user.id,
            category_id=antiques_category.id,
            title="Paid Test Item",
            description="This is an item test_user1 has paid for",
            auction_start=datetime.now() - timedelta(days=15),
            auction_end=datetime.now() - timedelta(days=5),
            minimum_price=200.00,
            auction_completed=True,
            status=3
        )
        db.session.add(paid_item)
        db.session.flush()
        
        # Create a winning bid from test_user1 on paid_item
        paid_winning_bid = Bid(
            item_id=paid_item.item_id,
            bidder_id=test_user1.id,
            bid_amount=210.00
        )
        db.session.add(paid_winning_bid)
        db.session.flush()
        
        # Set winning bid for paid_item
        paid_item.winning_bid_id = paid_winning_bid.bid_id
        
        # Item 6: Item created by regular_user that test_user1 is watching
        watched_item = Item(
            seller_id=regular_user.id,
            category_id=collectibles_category.id,
            title="Watched Test Item",
            description="This is an item test_user1 is watching",
            auction_start=datetime.now() - timedelta(days=2),
            auction_end=datetime.now() + timedelta(days=7),
            minimum_price=150.00
        )
        db.session.add(watched_item)
        db.session.flush()
        
        # Add watched_item to test_user1's watchlist
        db.session.execute(
            text("INSERT INTO user_watched_items (user_id, item_id) VALUES (:user_id, :item_id)"),
            {"user_id": test_user1.id, "item_id": watched_item.item_id}
        )
        
        db.session.commit()
        
        # Store the IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'test_user1_id': test_user1.id,
            'test_user2_id': test_user2.id,
            'antiques_category_id': antiques_category.id,
            'collectibles_category_id': collectibles_category.id,
            'active_item_id': active_item.item_id,
            'active_item_url': active_item.url,
            'auth_item_id': auth_item.item_id,
            'auth_item_url': auth_item.url,
            'bidding_item_id': bidding_item.item_id,
            'bidding_item_url': bidding_item.url,
            'won_item_id': won_item.item_id,
            'won_item_url': won_item.url,
            'paid_item_id': paid_item.item_id,
            'paid_item_url': paid_item.url,
            'watched_item_id': watched_item.item_id,
            'watched_item_url': watched_item.url
        }
    
    yield test_data

# Access Control Tests
def test_dashboard_access_logged_out(client, setup_database):
    """Test that logged out users are redirected when trying to access the dashboard"""
    response = client.get('/dashboard/', follow_redirects=False)
    assert response.status_code == 302
    
    # Follow redirect to confirm we go to login page
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

@login_as(role=2)
def test_dashboard_access_as_expert_user(client, setup_database, soup):
    """Test that experts can't see the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the expert dashboard, not user dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Expert Dashboard' in dashboard_title.text
    
    # Check that we don't see user dashboard tabs
    user_tabs = page.find('ul', id='userDashboardTabs')
    assert user_tabs is None

@login_as(role=3)
def test_dashboard_access_as_manager_user(client, setup_database, soup):
    """Test that managers can't see the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the manager dashboard, not user dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Management Dashboard' in dashboard_title.text
    
    # Check that we don't see user dashboard tabs
    user_tabs = page.find('ul', id='userDashboardTabs')
    assert user_tabs is None

@login_as(role=1)
def test_dashboard_access_as_regular_user(client, setup_database, soup):
    """Test that regular users can access the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we see the user dashboard
    page = soup(response.data)
    dashboard_title = page.find('h1', class_='dashboard-title')
    assert dashboard_title is not None
    assert 'Dashboard' in dashboard_title.text

# User Dashboard UI Tests
@login_as(role=1)
def test_user_dashboard_tabs(client, setup_database, soup):
    """Test that the user dashboard has all required tabs"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check for all tabs
    tabs = page.find_all('a', class_='nav-link')
    tab_ids = [tab.get('id') for tab in tabs]
    
    assert 'selling-tab' in tab_ids
    assert 'bidding-tab' in tab_ids
    assert 'watchlist-tab' in tab_ids

@login_as(role=1, user_id=4, username="test_user1")
def test_user_dashboard_selling_tab(client, setup_database, soup):
    """Test the selling tab content in the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify selling tab content
    selling_tab = page.find('div', id='selling')
    assert selling_tab is not None
    
    # Check for auctions table
    auctions_table = selling_tab.find('table', class_='auth-table')
    assert auctions_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in auctions_table.find_all('th')]
    assert 'Item' in headers
    assert 'Authentication' in headers
    assert 'Current Price' in headers
    assert 'Bids' in headers
    assert 'Time Remaining' in headers
    assert 'Watchers' in headers
    
    # Check for auction rows
    auction_rows = auctions_table.find_all('tr')[1:]
    assert len(auction_rows) > 0
    
    # Check for the active item title
    items_found = []
    for row in auction_rows:
        item_title = row.find('td', class_='item-title').text.strip()
        items_found.append(item_title)
        if "Active Test Item" in item_title:
            # Check for authentication status
            auth_status = row.find('td', {'data-label': 'Authentication'}).text.strip()
            assert 'NOT REQUESTED' in auth_status
    
    # Check that both items are found
    assert "Active Test Item" in items_found
    assert "Authenticated Test Item" in items_found

@login_as(role=1, user_id=4, username="test_user1")
def test_user_dashboard_bidding_tab(client, setup_database, soup):
    """Test the bidding tab content in the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify bidding tab exists
    bidding_tab = page.find('div', id='bidding')
    assert bidding_tab is not None
    
    # Verify bidding sub-tabs exist
    sub_tabs = bidding_tab.find_all('a', class_='nav-link')
    sub_tab_ids = [tab.get('id') for tab in sub_tabs]
    
    assert 'live-auctions-tab' in sub_tab_ids
    assert 'won-tab' in sub_tab_ids
    assert 'paid-tab' in sub_tab_ids
    
    # Check live bidding tab content
    live_bidding_tab = page.find('div', id='live-bidding')
    assert live_bidding_tab is not None
    
    # Check for bidding table
    bidding_table = live_bidding_tab.find('table', class_='auth-table')
    assert bidding_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in bidding_table.find_all('th')]
    assert 'Item' in headers
    assert 'Current Price' in headers
    assert 'Your Bid' in headers
    assert 'Status' in headers
    
    # Check for bidding item row
    bidding_rows = bidding_table.find_all('tr')[1:]
    assert len(bidding_rows) > 0
    
    bidding_item_found = False
    for row in bidding_rows:
        item_title = row.find('td', class_='item-title').text.strip()
        if "Bidding Test Item" in item_title:
            bidding_item_found = True
            
            # Check for bid status (should be losing since test_user2 has a higher bid)
            status_cell = row.find('div', class_='authentication-status')
            assert 'Losing' in status_cell.text
            
            # Check your bid amount
            your_bid_cell = row.find('td', {'data-label': 'Your Bid'}).text.strip()
            assert '£80.00' in your_bid_cell
    
    assert bidding_item_found

@login_as(role=1, user_id=4, username="test_user1")
def test_user_dashboard_won_tab(client, setup_database, soup):
    """Test the won tab content in the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Navigate to the won tab
    won_tab = page.find('div', id='won')
    assert won_tab is not None
    
    # Check for won items table
    won_table = won_tab.find('table', class_='auth-table')
    assert won_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in won_table.find_all('th')]
    assert 'Item' in headers
    assert 'Winning Bid' in headers
    assert 'Status' in headers
    assert 'Action' in headers
    
    # Check for won item row
    won_rows = won_table.find_all('tr')[1:]
    assert len(won_rows) > 0
    
    won_item_found = False
    for row in won_rows:
        item_title = row.find('td', class_='item-title').text.strip()
        if "Won Test Item" in item_title:
            won_item_found = True
            
            # Check for item status (should be UNPAID)
            status_cell = row.find('div', class_='authentication-status')
            assert 'UNPAID' in status_cell.text
            
            # Check for Pay button
            pay_button = row.find('button', class_='checkout-button')
            assert pay_button is not None
            assert 'Pay' in pay_button.text
    
    assert won_item_found

@login_as(role=1, user_id=4, username="test_user1")
def test_user_dashboard_paid_tab(client, setup_database, soup):
    """Test the paid tab content in the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Navigate to the paid tab
    paid_tab = page.find('div', id='paid')
    assert paid_tab is not None
    
    # Check for paid items table
    paid_table = paid_tab.find('table', class_='auth-table')
    assert paid_table is not None
    
    # Check for table headers
    headers = [th.text.strip() for th in paid_table.find_all('th')]
    assert 'Item' in headers
    assert 'Paid Amount' in headers
    assert 'Purchase Date' in headers
    assert 'Status' in headers
    
    # Check for paid item row
    paid_rows = paid_table.find_all('tr')[1:]
    assert len(paid_rows) > 0
    
    paid_item_found = False
    for row in paid_rows:
        item_title = row.find('td', class_='item-title').text.strip()
        if "Paid Test Item" in item_title:
            paid_item_found = True
            
            # Check for item status (should be PAID)
            status_cell = row.find('div', class_='authentication-status')
            assert 'PAID' in status_cell.text
            
            # Check paid amount
            paid_amount_cell = row.find('td', {'data-label': 'Paid Amount'}).text.strip()
            assert '£210.00' in paid_amount_cell
    
    assert paid_item_found

@login_as(role=1, user_id=4, username="test_user1")
def test_user_dashboard_watchlist_tab(client, setup_database, soup):
    """Test the watchlist tab content in the user dashboard"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify watchlist tab content
    watchlist_tab = page.find('div', id='watchlist')
    assert watchlist_tab is not None
    
    # First check if we have an empty state message (in case the watchlist is empty)
    empty_state = watchlist_tab.find('div', class_='empty-state')
    if empty_state is not None:
        # If we have an empty state, verify the message
        assert "You are not watching any auctions" in empty_state.text
    else:
        # Check for watchlist table
        watchlist_table = watchlist_tab.find('table', class_='auth-table')
        assert watchlist_table is not None
        
        # Check for table headers
        headers = [th.text.strip() for th in watchlist_table.find_all('th')]
        assert 'Item' in headers
        assert 'Status' in headers
        assert 'Current Price' in headers
        assert 'Time Remaining' in headers
        assert 'Watchers' in headers
        assert 'Action' in headers
        
        # Check for watched item row
        watchlist_rows = watchlist_table.find_all('tr')[1:]
        assert len(watchlist_rows) > 0
        
        watched_item_found = False
        for row in watchlist_rows:
            item_title = row.find('td', class_='item-title').text.strip()
            if "Watched Test Item" in item_title:
                watched_item_found = True
                
                # Check for item status (should be ACTIVE)
                status_cell = row.find('div', class_='authentication-status')
                assert 'ACTIVE' in status_cell.text
                
                # Check for Unwatch button
                unwatch_button = row.find('button', class_='unwatch-btn')
                assert unwatch_button is not None
                assert 'Unwatch' in unwatch_button.text
        
        assert watched_item_found

@login_as(role=1)
def test_user_dashboard_empty_states(client, setup_database, soup):
    """Test the empty states in user dashboard when there are no items"""
    mock_empty_user = MockUser(id=999, username="empty_user", role=1)
    
    # Log in as this empty user
    with logged_in_user(client, mock_empty_user):
        response = client.get('/dashboard/', follow_redirects=True)
        assert response.status_code == 200
        
        page = soup(response.data)
        
        # Check selling tab empty state
        selling_tab = page.find('div', id='selling')
        selling_empty_state = selling_tab.find('div', class_='empty-state')
        assert selling_empty_state is not None
        assert "You don't have any auctions listed yet" in selling_empty_state.text
        
        # Check bidding tab empty state
        bidding_tab = page.find('div', id='live-bidding')
        bidding_empty_state = bidding_tab.find('div', class_='empty-state')
        assert bidding_empty_state is not None
        assert "You are not currently bidding on any auctions" in bidding_empty_state.text
        
        # Check watchlist tab empty state
        watchlist_tab = page.find('div', id='watchlist')
        watchlist_empty_state = watchlist_tab.find('div', class_='empty-state')
        assert watchlist_empty_state is not None
        assert "You are not watching any auctions" in watchlist_empty_state.text