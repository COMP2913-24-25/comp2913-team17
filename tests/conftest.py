"""Test client for the app, creates a test database."""

import pytest
import os
import shutil
from main import create_app
from main.models import db
from bs4 import BeautifulSoup
from tests.test_utils import JsonClient

# Names of database files
TEST_DB_PATH = 'database_test.db'
MAIN_DB_PATH = 'database.db'

@pytest.fixture(scope="session")
def app():
    """Create a Flask app context for the tests"""
    import importlib
    import main
    importlib.reload(main)

    # Create an empty database
    os.environ['EMPTY_DB'] = '1'

    # Backup the main database if it exists
    if os.path.exists(f'./main/{MAIN_DB_PATH}'):
        print(f'\nBacking up main database to {MAIN_DB_PATH}.backup')
        shutil.copy2(f'./main/{MAIN_DB_PATH}', f'{MAIN_DB_PATH}.backup')
    
    # Delete test database file if it exists
    test_db_file = f'./main/{TEST_DB_PATH}'
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    # Create test app
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
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
    
    # Restore the main database from backup
    if os.path.exists(f'{MAIN_DB_PATH}.backup'):
        print(f'\nRestoring main database from {MAIN_DB_PATH}.backup')
        shutil.copy2(f'{MAIN_DB_PATH}.backup', f'./main/{MAIN_DB_PATH}')
        os.remove(f'{MAIN_DB_PATH}.backup')

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
