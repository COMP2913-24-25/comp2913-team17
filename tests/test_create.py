import pytest
from datetime import datetime, timedelta
from main import create_app, db
from main.models import Item, User
from flask import Flask, session
from main import create_app, scheduler

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['AWS_BUCKET'] = 'test-bucket'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def login(client):
    test_user = User(
        username='test-user',
        email='tester-user@testing.com',
        role=1,
        created_at=datetime.now(),
    )

    test_user.set_password('password123')

    db.session.add(test_user)
    db.session.commit()

    # simulates user login
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
    
    # after test is finished, clear the login
    yield client

    # logs out the user from the session
    with client.session_transaction() as session:
        session.pop('user_id', None)

def test_create_form(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'create' in response.data

"""
Auction start is in the future
Auction start is no more than 5 days later
Auctions last a minimum of 1 hour
Auctions last a maximum of 5 days
Auction end is after auction start
"""

def test_future_start(login, client):
    response = client.post('/create/', data={
        'title': 'Test Future Start',
        'description': 'Tests auction starts in the future',
        'auction_start': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })

    assert b'Auction start time must be in the future.' in response.data

def test_start_schedule(login, client):
    response = client.post('/create/', data={
        'title': 'Test Scheduled Auction',
        'description': 'Tests auction is scheduled less than maximum days into the future',
        'auction_start': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(days=9)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })
    
    assert b'Auctions can only be scheduled up to 5 days in advance.' in response.data

def test_min_duration(login, client):
    response = client.post('/create/', data={
        'title': 'Test Min Duration',
        'description': 'Tests auction duration is more than the minimum required',
        'auction_start': (datetime.now()).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })
    
    assert b'Auctions must last for atleast 1 hour.' in response.data

def test_max_duration(login, client):
    response = client.post('/create/', data={
        'title': 'Test Max Duration',
        'description': 'Tests auction exceeding maximum duration',
        'auction_start': (datetime.now()).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })
    
    assert b'Auction duration cannot be longer than 5 days.' in response.data

def test_end_after_start(login, client):
    response = client.post('/create/', data={
        'title': 'Test End After Start',
        'description': 'Tests auction ends after the auction start date',
        'auction_start': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })
    
    assert b'Auction end must occur after auction start time.' in response.data

def test_auction_is_created(login, client):
    response = client.post('/create/', data={
        'title': 'Test Successful auction',
        'description': 'Tests if auction can be successfully created',
        'auction_start': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
        'auction_end': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M'),
        'minimum_price': 1.00,
        'authenticate_item': False,
    })
    
    assert b'Auction created successfully!' in response.data

