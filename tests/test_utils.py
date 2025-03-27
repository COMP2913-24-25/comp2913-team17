"""Test utilities for common test functions."""

import flask_login
from flask import session, g
from functools import wraps
from contextlib import contextmanager

class MockUser:
    """Mock user class for testing Flask-Login functionality"""

    def __init__(self, id=None, username=None, is_authenticated=True, role=1):
        self.id = id
        self.username = username
        self.is_authenticated = is_authenticated
        self.role = role
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        """Return user ID as string"""
        return str(self.id)

@contextmanager
def logged_in_user(client, user, remember=False):
    """Context manager for testing as a logged-in user"""
    # Store original function
    original_get_user = flask_login.utils._get_user

    try:
        # Replace with our mock function
        flask_login.utils._get_user = lambda: user
        yield
    finally:
        # Restore original function
        flask_login.utils._get_user = original_get_user

def login_as(role, user_id=1, username="testuser"):
    """Decorator to run a test function with a specific user role logged in"""
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(client, *args, **kwargs):
            # Create mock user
            mock_user = MockUser(id=user_id, username=username, is_authenticated=True, role=role)

            # Store original function
            original_get_user = flask_login.utils._get_user

            try:
                # Replace with our mock function
                flask_login.utils._get_user = lambda: mock_user

                # Run the test
                return test_func(client, *args, **kwargs)
            finally:
                # Restore original function
                flask_login.utils._get_user = original_get_user

        return wrapper
    return decorator

def mock_login_user(monkeypatch, user):
    """Mock the flask_login.current_user functionality"""
    monkeypatch.setattr('flask_login.utils._get_user', lambda: user)
