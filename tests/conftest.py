"""Test client for the app, creates a test database for the tests to use."""

import pytest
import os
from main import create_app
from main.models import db
from bs4 import BeautifulSoup
from tests.test_utils import JsonClient

# Path to test database file
TEST_DB_PATH = 'database_test.db'

@pytest.fixture(scope="session")
def app():
    """Create a Flask app context for the tests"""
    import importlib
    import main
    importlib.reload(main)

    # Create an empty database
    os.environ['EMPTY_DB'] = '1'

    # Delete test database file if it exists
    if os.path.exists(f'./main/{TEST_DB_PATH}'):
        os.remove(f'./main/{TEST_DB_PATH}')

    app = create_app(testing=True, database_path=TEST_DB_PATH)
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

    yield app

    # Clean up after all tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

    # Remove the test database file
    if os.path.exists(f'./main/{TEST_DB_PATH}'):
        os.remove(f'./main/{TEST_DB_PATH}')

@pytest.fixture
def client(app):
    """Create a test client for the app"""
    with app.test_client() as client:
        yield client

@pytest.fixture
def json_client(client):
    """Create a JSON test client"""
    return JsonClient(client)

@pytest.fixture
def soup():
    """Return a BeautifulSoup parser for HTML content"""
    def _soup(html_content):
        return BeautifulSoup(html_content, 'html.parser')
    return _soup
