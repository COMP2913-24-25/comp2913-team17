import pytest
from main import create_app
from main.models import db

@pytest.fixture(scope="session")
def app():
    """Create a Flask app context for the tests."""
    # Force any previously imported modules to reload to avoid stale imports
    import importlib
    import main
    importlib.reload(main)
    
    app = create_app(testing=True)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    # Clean up after all tests
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client
