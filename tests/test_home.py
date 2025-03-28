"""Test homepage functionality."""

import pytest
from main.models import Item, User, Category, db, Bid, Image
from tests.test_utils import (
    MockUser, logged_in_user, login_as, setup_test_data, clean_test_data,
    common_setup_database, verify_page_title, verify_element_exists, create_test_items, 
    reset_database_for_test, clear_all_tables
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for homepage tests"""
    test_data = {}
    
    with app.app_context():
        users = User.query.all()
        categories = Category.query.all()
        items = create_test_items(users, categories)
        
        # Store the IDs
        test_data = {
            'user_ids': [user.id for user in users],
            'category_ids': [category.id for category in categories],
            'item_ids': [item.item_id for item in items]
        }
    
    yield test_data

# Tests for homepage access and content
def test_home_page_access(client, setup_database):
    """Test that home page is accessible and returns correct status code"""
    response = client.get('/')
    assert response.status_code == 200

def test_home_page_title(client, setup_database, soup):
    """Test that home page has the correct title"""
    response = client.get('/')
    page = soup(response.data)
    verify_page_title(page, 'Vintage Vault')

def test_home_page_hero_section(client, setup_database, soup):
    """Test that the home page hero section is present"""
    response = client.get('/')
    page = soup(response.data)
    
    hero_content = page.find(['div', 'section'], class_=lambda x: x and 'hero' in x)
    assert hero_content is not None
    
    main_heading = page.find(['h1', 'h2'], class_=lambda x: x and 'title' in x)
    assert main_heading is not None

# Tests with different user roles
@login_as(role=1)
def test_home_page_as_regular_user(client, setup_database, soup):
    """Test home page content when logged in as a regular user"""
    response = client.get('/')
    page = soup(response.data)
    
    # Look for auction creation link
    start_button = page.find('a', string='START YOUR AUCTION')
    assert start_button is not None
    
    # Should NOT see the login/register buttons
    login_button = page.find('a', string='LOGIN')
    register_button = page.find('a', string='REGISTER')
    assert login_button is None
    assert register_button is None

@login_as(role=2)
def test_home_page_as_expert(client, setup_database, soup):
    """Test home page content when logged in as an expert"""
    response = client.get('/')
    page = soup(response.data)
    
    # Expert users should see the dashboard button in hero section
    dashboard_button = page.find('a', string='VIEW YOUR DASHBOARD')
    assert dashboard_button is not None
    
    # And should not see the start auction button
    start_button = page.find('a', string='START YOUR AUCTION')
    assert start_button is None

@login_as(role=3)
def test_home_page_as_manager(client, setup_database, soup):
    """Test home page content when logged in as a manager"""
    response = client.get('/')
    page = soup(response.data)
    
    # Manager should see the dashboard button
    dashboard_button = page.find('a', string='VIEW YOUR DASHBOARD')
    assert dashboard_button is not None

# Tests for auction items display
def test_auction_items_displayed(client, setup_database, soup):
    """Test that auction items are displayed on the home page"""
    response = client.get('/')
    page = soup(response.data)
    
    # Check that items from the database are displayed
    items = Item.query.all()
    assert len(items) > 0
    
    # Count item divs on the page
    auction_items = page.select('.auction-item')
    assert len(auction_items) > 0
    
    # Check for title of first item
    first_item_title = items[0].title
    assert first_item_title in page.text

def test_auction_items_with_images(client, setup_database, soup):
    """Test that auction items with images display correctly"""
    response = client.get('/')
    page = soup(response.data)
    
    # Find items with images
    items_with_images = Item.query.filter(Item.images.any()).all()
    assert len(items_with_images) > 0
    
    # Check at least one image is displayed
    auction_images = page.select('.auction-image')
    assert len(auction_images) > 0
    
    # Check the placeholder for items without images
    placeholder_images = page.select('.placeholder-image')
    items_without_images = Item.query.filter(~Item.images.any()).all()
    assert len(placeholder_images) == len(items_without_images)

def test_auction_items_with_bids(client, setup_database, soup):
    """Test that auction items with bids display correctly"""
    response = client.get('/')
    page = soup(response.data)
    
    # Find items with bids
    items_with_bids = Item.query.filter(Item.bids.any()).all()
    assert len(items_with_bids) > 0
    
    # Check bid counts on the page
    bid_counts = page.select('.bid-count')
    assert len(bid_counts) >= len(items_with_bids)

def test_auction_countdown_displayed(client, setup_database, soup):
    """Test that auction countdown is displayed for items"""
    response = client.get('/')
    page = soup(response.data)
    
    # Find all countdown elements
    countdown_elements = page.select('.countdown')
    
    # Check count of countdown elements matches the number of items
    items = Item.query.all()
    assert len(countdown_elements) == len(items)
    
    # Each countdown should have a data-end attribute
    for countdown in countdown_elements:
        assert 'data-end' in countdown.attrs

# Tests for search functionality, not used in the current implementation
def test_search_api_endpoint(json_client, setup_database):
    """Test the search API endpoint returns correct JSON data"""
    response = json_client.get('/api/search')
    assert response.status_code == 200
    
    # Check items count matches database
    items_count = Item.query.count()
    assert len(response.json) == items_count
    
    # Check structure of returned items
    first_item = response.json[0]
    assert 'item_id' in first_item
    assert 'title' in first_item
    assert 'url' in first_item

def test_search_filter_functionality(client, setup_database, soup):
    """Test that search and filter elements exist and have proper attributes"""
    response = client.get('/')
    page = soup(response.data)
    
    # Check search bar exists
    search_bar = page.select_one('#search-bar')
    assert search_bar is not None
    assert search_bar['placeholder'] == 'SEARCH AUCTIONS...'
    
    # Check auction type filter exists
    type_filter = page.select_one('#type-filter')
    assert type_filter is not None
    options = type_filter.select('option')
    assert len(options) == 3
    
    # Check values of options
    assert options[0]['value'] == '0'
    assert options[1]['value'] == '1'
    assert options[2]['value'] == '2'

# Tests for categories display
def test_categories_filter_displayed(client, setup_database, soup):
    """Test that categories are displayed in the filter dropdown"""
    response = client.get('/')
    page = soup(response.data)
    
    # Get categories from database
    categories = Category.query.all()
    assert len(categories) > 0
    
    # Check category dropdown exists
    category_filter = page.select_one('#category-filter')
    assert category_filter is not None
    
    # Check category dropdown options
    category_options = category_filter.select('option')
    assert len(category_options) == len(categories) + 1
    
    # Check each category is displayed
    for category in categories:
        option_text = category.name.upper()
        category_option = page.find('option', string=option_text)
        assert category_option is not None

# Test authentication filter
def test_authentication_filter(client, setup_database, soup):
    """Test that authentication filter is present"""
    response = client.get('/')
    page = soup(response.data)
    
    # Check authentication checkbox exists
    auth_checkbox = page.find('input', {'id': 'authenticated-only'})
    assert auth_checkbox is not None
    auth_label = page.find('label', {'for': 'authenticated-only'})
    assert auth_label is not None
    assert "ONLY SHOW AUTHENTICATED ITEMS" in auth_label.text

# Test with no items in database
def test_home_page_with_no_items(client, app, soup):
    """Test how the page displays when no items exist"""
    with app.app_context():
        # Temporarily clear items but keep other data
        db.session.query(Bid).delete()
        db.session.query(Image).delete()
        db.session.query(Item).delete()
        db.session.commit()
        
        response = client.get('/')
        page = soup(response.data)
        
        # Should show "No auctions available" message
        no_auctions_message = page.find(string="No auctions available at the moment.")
        assert no_auctions_message is not None
        
        # For anonymous users, check registration link
        register_link = page.find('a', string=lambda text: text and 'register' in text.lower())
        assert register_link is not None
    
    # Restore test data for other tests
    with app.app_context():
        users = User.query.all()
        categories = Category.query.all()
        create_test_items(users, categories)

# Test with an authenticated user and no items
@login_as(role=1)
def test_home_page_authenticated_no_items(client, app, soup):
    """Test how the page displays when no items exist but user is authenticated"""
    with app.app_context():
        # Temporarily clear just the items
        db.session.query(Bid).delete()
        db.session.query(Image).delete()
        db.session.query(Item).delete()
        db.session.commit()
        
        response = client.get('/')
        page = soup(response.data)
        
        # For authenticated users, check create auction button
        create_button = page.find('a', string="CREATE AN AUCTION")
        assert create_button is not None
    
    # Restore test data for other tests
    with app.app_context():
        users = User.query.all()
        categories = Category.query.all()
        create_test_items(users, categories)

# Test about us section
def test_about_us_section(client, setup_database, soup):
    """Test that the About Us section is present"""
    response = client.get('/')
    page = soup(response.data)
    
    # Check section exists
    about_section = page.find('h2', string='Thinking Of Selling?')
    assert about_section is not None
    
    # Check for the join button
    join_button = page.find('a', string=lambda s: s and 'JOIN' in s)
    assert join_button is not None

# Test footer
def test_footer_section(client, setup_database, soup):
    """Test that the footer section is present and contains necessary information"""
    response = client.get('/')
    page = soup(response.data)
    
    # Check footer exists
    footer = page.select_one('footer')
    assert footer is not None
    
    # Check useful links section
    useful_links = footer.find('h5', string='Useful Links.')
    assert useful_links is not None
    
    # Check contact us section
    contact_us = footer.find('h5', string='Contact Us.')
    assert contact_us is not None
    
    # Check newsletter signup
    newsletter = footer.select_one('#newsletter-email')
    assert newsletter is not None
    
    # Check copyright
    copyright_text = footer.find(string=lambda text: '© ' in text)
    assert copyright_text is not None
