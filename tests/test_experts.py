"""Test expert functionality."""

import pytest
from datetime import date, timedelta, time
from main.models import db, User, ExpertAvailability
from tests.test_utils import (
    MockUser, logged_in_user, login_as, mock_login_user,
    common_setup_database, verify_page_title, verify_element_exists,
    clear_all_tables
)

@pytest.fixture(scope="module")
def setup_database(app, common_setup_database):
    """Create custom test data for expert page tests"""
    test_data = {}
    
    with app.app_context():
        # Get existing users created by common_setup_database
        regular_user = User.query.filter_by(username="regular_user").first()
        expert_user = User.query.filter_by(username="expert_user").first()
        manager_user = User.query.filter_by(username="manager_user").first()
        
        # Create some test availability data for the expert user
        today = date.today()
        # Current week start (Sunday)
        current_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        
        # Create availability for the current week
        for i in range(7):
            current_day = current_week_start + timedelta(days=i)
            
            # Make the expert available on MWF and unavailable on other days
            is_available = (i in [0, 2, 4])
            
            availability = ExpertAvailability(
                expert_id=expert_user.id,
                day=current_day,
                start_time=time(9, 0) if is_available else time(8, 0),
                end_time=time(17, 0) if is_available else time(20, 0),
                status=is_available
            )
            db.session.add(availability)
        
        # Create availability for next week (only Monday)
        next_week_monday = current_week_start + timedelta(days=8)
        next_monday_avail = ExpertAvailability(
            expert_id=expert_user.id,
            day=next_week_monday,
            start_time=time(10, 0),
            end_time=time(16, 0),
            status=True
        )
        db.session.add(next_monday_avail)
        
        db.session.commit()
        
        # Store IDs
        test_data = {
            'regular_user_id': regular_user.id,
            'expert_user_id': expert_user.id,
            'manager_user_id': manager_user.id,
            'current_week_start': current_week_start,
            'next_week_start': current_week_start + timedelta(days=7)
        }
    
    yield test_data
    
    # Clean up test data
    with app.app_context():
        # Delete all availability data created for tests
        ExpertAvailability.query.filter_by(expert_id=expert_user.id).delete()
        db.session.commit()

# Access Control Tests
def test_availability_page_access_logged_out(client, setup_database):
    """Test that logged out users are redirected when trying to access the expert availability page"""
    response = client.get('/expert/availability', follow_redirects=False)
    assert response.status_code == 302 
    
    # Follow redirect to confirm we go to login page
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

@login_as(role=1)
def test_availability_page_access_as_regular_user(client, setup_database, soup):
    """Test that regular users cannot access the expert availability page"""
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    
    # Should be redirected to home page with error
    page = soup(response.data)
    verify_page_title(page, "Vintage Vault")
    
    # Check for error message
    flash_message = page.find('div', class_='alert-error') or page.find('div', class_='alert-danger')
    assert flash_message is not None
    assert "not authorised" in flash_message.text.lower()

@login_as(role=3)
def test_availability_page_access_as_manager_user(client, setup_database, soup):
    """Test that manager users cannot access the expert availability page"""
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    
    # Should be redirected to home page with error
    page = soup(response.data)
    verify_page_title(page, "Vintage Vault")
    
    # Check for error message
    flash_message = page.find('div', class_='alert-error') or page.find('div', class_='alert-danger')
    assert flash_message is not None
    assert "not authorised" in flash_message.text.lower()

@login_as(role=2)
def test_availability_page_access_as_expert(client, setup_database, soup):
    """Test that expert users can access the expert availability page"""
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that we can see the expert availability page
    page = soup(response.data)
    verify_page_title(page, "Expert Availability")
    
    # Verify the heading
    heading = page.find('h1', class_='availability-heading')
    assert heading is not None
    assert "Update Weekly Availability" in heading.text

# UI Tests
@login_as(role=2) 
def test_availability_page_components(client, setup_database, soup):
    """Test that the availability page has all required components"""
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Verify form exists
    form = page.find('form', {'name': 'ExpertAvailability'})
    assert form is not None
    
    # Verify table exists
    table = form.find('table')
    assert table is not None
    
    # Verify table has headers
    headers = [th.text.strip() for th in table.find_all('th', scope='col')]
    assert 'Day' in headers
    assert 'Start Time (8:00 - 20:00)' in headers
    assert 'End Time (8:00 - 20:00)' in headers
    assert 'Status' in headers
    
    # Verify rows for each day of the week
    rows = table.find_all('tr')
    # First row is header, then 7 days of the week
    assert len(rows) == 8
    
    # Verify the bulk action buttons exist
    mark_unavailable_btn = page.find('button', id='mark-week-unavailable')
    assert mark_unavailable_btn is not None
    assert "Mark Whole Week as Unavailable" in mark_unavailable_btn.text
    
    mark_available_btn = page.find('button', id='mark-week-available')
    assert mark_available_btn is not None
    assert "Mark Whole Week as Available" in mark_available_btn.text
    
    # Verify save button exists
    save_btn = page.find('button', {'type': 'submit'})
    assert save_btn is not None
    assert "Save Availability" in save_btn.text

@login_as(role=2) 
def test_availability_page_week_navigation(client, setup_database, soup):
    """Test the week navigation buttons on the availability page"""
    # First go to the current week
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # Check if we have a "Next Week" button but no "Previous Week" button on the current week
    next_week_btn = page.find('a', string=lambda s: s and "Next Week" in s)
    assert next_week_btn is not None
    
    # Navigate to next week
    next_week_url = next_week_btn['href']
    response = client.get(next_week_url, follow_redirects=True)
    assert response.status_code == 200
    
    page = soup(response.data)
    
    # On next week, we should have both "Previous Week" and "Next Week" buttons
    prev_week_btn = page.find('a', string=lambda s: s and "Previous Week" in s)
    next_week_btn = page.find('a', string=lambda s: s and "Next Week" in s)
    
    assert prev_week_btn is not None
    assert next_week_btn is not None

# Form Submission Tests

@login_as(role=2) 
def test_update_availability_submit(client, setup_database):
    """Test submitting the availability form"""
    # Get the current week start
    current_week_start = setup_database['current_week_start']
    
    # First, get the page to extract the CSRF token
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    csrf_token = response.data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    
    # Prepare form data with minimal fields - just set Sunday to available
    form_data = {
        'csrf_token': csrf_token,
        'week_start': current_week_start.strftime('%Y-%m-%d'),
        'day_0_start': '09:00',
        'day_0_end': '17:00',
        'day_0_status': 'available'
    }
    
    # Submit the form
    response = client.post('/expert/availability', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Check for success message
    assert b'Availability updated successfully' in response.data
    
    # Verify the data was updated in the database
    with client.application.app_context():
        expert_user_id = setup_database['expert_user_id']
        
        # Check Sunday (day 0)
        sunday = current_week_start 
        sunday_avail = ExpertAvailability.query.filter_by(
            expert_id=expert_user_id,
            day=sunday
        ).first()
        
        assert sunday_avail is not None
        assert sunday_avail.status is True, "Sunday should be available"

@login_as(role=2)
def test_update_availability_mixed_status(client, setup_database):
    """Test updating availability with mixed statuses"""
    # Get the current week start
    current_week_start = setup_database['current_week_start']
    
    # First, get the page to extract the CSRF token
    response = client.get('/expert/availability', follow_redirects=True)
    assert response.status_code == 200
    csrf_token = response.data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    
    # Prepare form data with explicit status for different days
    form_data = {
        'csrf_token': csrf_token,
        'week_start': current_week_start.strftime('%Y-%m-%d')
    }
    
    # Set just a few specific days with different statuses
    form_data['day_0_start'] = '10:00'
    form_data['day_0_end'] = '16:00'
    form_data['day_0_status'] = 'available'
    
    form_data['day_1_start'] = '10:00'
    form_data['day_1_end'] = '16:00'
    form_data['day_1_status'] = 'unavailable'
    
    # Submit the form
    response = client.post('/expert/availability', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Check for success message
    assert b'Availability updated successfully' in response.data
    
    # Verify the data was updated in the database
    with client.application.app_context():
        expert_user_id = setup_database['expert_user_id']
        
        # Check Sunday - should be available
        sunday = current_week_start
        sunday_avail = ExpertAvailability.query.filter_by(
            expert_id=expert_user_id,
            day=sunday
        ).first()
        assert sunday_avail is not None
        assert sunday_avail.status is True, "Sunday should be available"
        
        # Check Monday - should be unavailable
        monday = current_week_start + timedelta(days=1)
        monday_avail = ExpertAvailability.query.filter_by(
            expert_id=expert_user_id,
            day=monday
        ).first()
        assert monday_avail is not None
        assert monday_avail.status is False, "Monday should be unavailable"

@login_as(role=2)
def test_update_availability_invalid_times(client, setup_database, soup):
    """Test submitting the availability form with invalid times"""
    # Get the current week start
    current_week_start = setup_database['current_week_start']
    
    # Prepare form data with invalid times (outside 08:00-20:00 range)
    form_data = {
        'csrf_token': 'dummy_token',
        'week_start': current_week_start.strftime('%Y-%m-%d')
    }
    
    # Set one day with invalid times
    form_data['day_0_start'] = '07:00'
    form_data['day_0_end'] = '21:00' 
    form_data['day_0_status'] = 'available'
    
    # Set the rest of the days with valid times
    for i in range(1, 7):
        form_data[f'day_{i}_start'] = '10:00'
        form_data[f'day_{i}_end'] = '16:00'
        form_data[f'day_{i}_status'] = 'available'
    
    # Submit the form
    response = client.post('/expert/availability', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Check for errors
    page = soup(response.data)
    flash_message = page.find('div', class_='alert-error') or page.find('div', class_='alert-danger')
    assert flash_message is not None
    assert "must be between 08:00 and 20:00" in flash_message.text

@login_as(role=2) 
def test_update_availability_next_week(client, setup_database):
    """Test updating availability for a future week"""
    # Get the next week start
    next_week_start = setup_database['next_week_start']
    
    # First, get the next week page to extract the CSRF token
    response = client.get(f'/expert/availability?week_start={next_week_start.strftime("%Y-%m-%d")}', follow_redirects=True)
    assert response.status_code == 200
    csrf_token = response.data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    
    # Prepare form data
    form_data = {
        'csrf_token': csrf_token,
        'week_start': next_week_start.strftime('%Y-%m-%d')
    }
    
    # Set just one day to simplify the test
    form_data['day_1_start'] = '11:00' 
    form_data['day_1_end'] = '15:00'
    form_data['day_1_status'] = 'available'
    
    # Submit the form
    response = client.post('/expert/availability', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Check for success message
    assert b'Availability updated successfully' in response.data
    
    # Verify the data was updated in the database
    with client.application.app_context():
        expert_user_id = setup_database['expert_user_id']
        
        # Check the Monday of next week
        next_week_monday = next_week_start + timedelta(days=1) 
        availability = ExpertAvailability.query.filter_by(
            expert_id=expert_user_id,
            day=next_week_monday
        ).first()
        
        assert availability is not None
        assert availability.start_time.strftime('%H:%M') == '10:00'
        assert availability.end_time.strftime('%H:%M') == '16:00'
        assert availability.status is True