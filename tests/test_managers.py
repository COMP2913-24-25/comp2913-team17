"""Test manager manager expert availability page functionality."""

import pytest
from datetime import date, datetime, timedelta
from main.models import db, User, Category, ExpertAvailability, ExpertCategory
from tests.test_utils import (
    login_as, verify_element_exists, verify_page_title,
    verify_flash_message, MockUser, mock_login_user
)

def create_expert_availability(expert_id, day, start_time, end_time, status=True):
    """Create an expert availability record."""
    availability = ExpertAvailability(
        expert_id=expert_id,
        day=day,
        start_time=start_time,
        end_time=end_time,
        status=status
    )
    db.session.add(availability)
    db.session.commit()
    return availability

def setup_expert_categories(expert_id, category_ids):
    """Set up expert categories."""
    for category_id in category_ids:
        expert_category = ExpertCategory(
            expert_id=expert_id,
            category_id=category_id
        )
        db.session.add(expert_category)
    db.session.commit()

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    return None

@pytest.fixture
def setup_expert_availability_data(app):
    """Set up test data for expert availability."""
    with app.app_context():
        # Get existing users and categories or create new ones
        users = User.query.all()
        categories = Category.query.all()
        
        if not users or len(users) < 3:
            users = User.query.all()
        
        if not categories or len(categories) < 2:
            categories = Category.query.all()
        
        # Check if we have at least one expert
        experts = [user for user in users if user.role == 2]
        if not experts:
            # Create an expert if none exists
            expert = User(
                username="test_expert", 
                email="test_expert@example.com", 
                role=2
            )
            expert.set_password("Password@123")
            db.session.add(expert)
            db.session.commit()
            experts = [expert]
        
        # Get today's date for availability records
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        # Clear any existing availability records for testing
        ExpertAvailability.query.delete()
        
        # Store expert usernames for testing
        expert_usernames = [expert.username for expert in experts]
        
        # Create availability records for experts
        availabilities = []
        for expert in experts:
            # Today's availability (all day)
            today_avail = create_expert_availability(
                expert_id=expert.id,
                day=today,
                start_time=datetime.strptime("08:00", "%H:%M").time(),
                end_time=datetime.strptime("20:00", "%H:%M").time(),
                status=True
            )
            
            # Tomorrow's availability (morning)
            tomorrow_avail = create_expert_availability(
                expert_id=expert.id,
                day=tomorrow,
                start_time=datetime.strptime("08:00", "%H:%M").time(),
                end_time=datetime.strptime("12:00", "%H:%M").time(),
                status=True
            )
            
            # Next week availability (not available)
            next_week_avail = create_expert_availability(
                expert_id=expert.id,
                day=next_week,
                start_time=datetime.strptime("08:00", "%H:%M").time(),
                end_time=datetime.strptime("20:00", "%H:%M").time(),
                status=False
            )
            
            availabilities.extend([today_avail, tomorrow_avail, next_week_avail])
            
            # Set up expert categories
            if categories:
                setup_expert_categories(expert.id, [categories[0].id])
        
        db.session.commit()
        
        return {
            'users': users,
            'experts': experts,
            'expert_usernames': expert_usernames,
            'categories': categories,
            'availabilities': availabilities,
            'today': today,
            'tomorrow': tomorrow,
            'next_week': next_week
        }

# Access tests
def test_availability_page_access_logged_out(client):
    """Test that logged-out users are redirected to login."""
    response = client.get('/manager/expert_availability', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in' in response.data or b'sign in' in response.data or b'Log in' in response.data

@login_as(role=1, user_id=1, username="regular_user")
def test_availability_page_access_as_regular_user(client):
    """Test that regular users are denied access."""
    response = client.get('/manager/expert_availability', follow_redirects=True)
    assert response.status_code == 200
    # Check for redirection to home page
    assert b'Welcome to Vintage Vault' in response.data or b'not authorized' in response.data

@login_as(role=2, user_id=2, username="expert_user")
def test_availability_page_access_as_expert_user(client):
    """Test that experts are denied access."""
    response = client.get('/manager/expert_availability', follow_redirects=True)
    assert response.status_code == 200
    # Check for redirection to home page
    assert b'Welcome to Vintage Vault' in response.data or b'not authorized' in response.data

@login_as(role=3, user_id=3, username="manager_user")
def test_availability_page_access_as_manager(client):
    """Test that managers can access the page."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    assert b'Expert Availability Overview' in response.data

# Page element tests
@login_as(role=3, user_id=3, username="manager_user")
def test_manager_dashboard_tabs(client, setup_expert_availability_data, soup):
    """Test that the dashboard tabs exist."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    verify_page_title(page, 'Expert Availability Overview')
    
    # Verify tabs exist
    daily_tab = verify_element_exists(page, 'a', {'id': 'daily-tab'})
    assert 'Daily View' in daily_tab.text
    
    weekly_tab = verify_element_exists(page, 'a', {'id': 'weekly-tab'})
    assert 'Weekly View' in weekly_tab.text

@login_as(role=3, user_id=3, username="manager_user")
def test_manager_availability_daily_view(client, setup_expert_availability_data, soup):
    """Test the daily view table and components."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify daily table exists
    daily_table = verify_element_exists(page, 'table', {'id': 'dailyTable'})
    
    # Verify time slots in header
    headers = daily_table.find_all('th')
    assert len(headers) > 1
    
    # Verify there's a header for 8:00 AM
    found_8am = False
    for header in headers:
        if "08:00" in header.text:
            found_8am = True
            break
    assert found_8am, "Could not find 08:00 time slot in table headers"
    
    # Verify table has rows
    assert len(daily_table.find_all('tr')) > 1, "Expected at least one expert row in the table"

@login_as(role=3, user_id=3, username="manager_user")
def test_manager_availability_weekly_view(client, setup_expert_availability_data, soup):
    """Test the weekly view table and components."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Switch to the weekly tab
    weekly_tab = page.find('a', {'id': 'weekly-tab'})
    weekly_content = page.find('div', {'id': 'weekly'})
    
    # Verify weekly table exists
    weekly_table = verify_element_exists(weekly_content, 'table', {'id': 'weeklyTable'})
    
    # Verify days in header (7 days from today)
    headers = weekly_table.find_all('th')
    assert len(headers) > 1
    
    # Verify the first day is today
    today_str = setup_expert_availability_data['today'].strftime('%b %d')
    today_header_found = False
    for header in headers[1:]:
        if today_str in header.text:
            today_header_found = True
            break
    assert today_header_found, f"Could not find today's date ({today_str}) in weekly headers"
    
    # Verify table has rows
    assert len(weekly_table.find_all('tr')) > 1, "Expected at least one expert row in the table"

@login_as(role=3, user_id=3, username="manager_user")
def test_category_filter(client, setup_expert_availability_data, soup):
    """Test the category filter component."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify category filter exists
    category_filter = verify_element_exists(page, 'select', {'id': 'expert-category-filter'})
    
    # Verify it contains the default "All Categories" option
    all_option = category_filter.find('option', value='')
    assert all_option is not None
    assert 'ALL CATEGORIES' in all_option.text
    
    assert category_filter is not None

@login_as(role=3, user_id=3, username="manager_user")
def test_expert_search(client, setup_expert_availability_data, soup):
    """Test the expert search component."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify expert search input exists
    search_input = verify_element_exists(page, 'input', {'id': 'expert-search'})
    assert search_input['placeholder'] == 'SEARCH EXPERTS...'

@login_as(role=3, user_id=3, username="manager_user")
def test_expert_availability_data(client, setup_expert_availability_data, soup):
    """Test that expert availability data is correctly passed to the template."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Find the daily table
    daily_table = page.find('table', {'id': 'dailyTable'})
    assert daily_table is not None
    
    # Check there are rows with availability data (should have green or red cells)
    rows = daily_table.find_all('tr')
    assert len(rows) > 1, "No expert rows found in availability table"
    
    # Check at least one availability cell exists (green or red)
    availability_cells = daily_table.find_all('td', class_=['bg-success', 'bg-danger'])
    assert len(availability_cells) > 0, "No availability data cells found"

@login_as(role=3, user_id=3, username="manager_user")
def test_time_slots_generated(client, setup_expert_availability_data, soup):
    """Test that time slots are correctly generated."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify daily table has the correct time slots
    daily_table = page.find('table', {'id': 'dailyTable'})
    headers = daily_table.find_all('th')
    
    # Time slots should be from 08:00 to 20:00 (13 slots)
    time_slots = [header.text for header in headers[1:]]
    
    # Check if we have expected time slots (at least 08:00, 12:00, and 19:00)
    assert '08:00' in ''.join(time_slots), "08:00 time slot not found"
    assert '12:00' in ''.join(time_slots), "12:00 time slot not found"
    assert '19:00' in ''.join(time_slots), "19:00 time slot not found"

@login_as(role=3, user_id=3, username="manager_user")
def test_toggle_filter_button(client, setup_expert_availability_data, soup):
    """Test that the toggle filter button exists."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify toggle filter button exists
    toggle_button = verify_element_exists(page, 'button', {'id': 'toggleFilter'})
    assert 'Show Only Currently Available Experts' in toggle_button.text

@login_as(role=3, user_id=3, username="manager_user")
def test_current_time_display(client, setup_expert_availability_data, soup):
    """Test that the current time is displayed."""
    response = client.get('/manager/expert_availability')
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify page contains current time text
    assert 'Current time:' in page.get_text() 