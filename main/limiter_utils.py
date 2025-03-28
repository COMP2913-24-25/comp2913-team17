"""Rate limiting utilities to protect sensitive operations."""

from flask import request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per minutes"],
    storage_uri="memory://",
)

def configure_limiter(app):
    """Configure the rate limiter with the Flask app."""
    limiter.init_app(app)

    # Set default limits for all routes
    limiter.default_limits = ["1000 per minutes"]

    # Add exempt paths for static files
    @limiter.request_filter
    def exempt_static_paths():
        return request.path.startswith('/static')

    return limiter

def get_limiter():
    """Get the limiter instance."""
    return limiter
