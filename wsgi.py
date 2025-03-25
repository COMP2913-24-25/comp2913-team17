"""WSGI entry point for Gunicorn with proper monkey patching"""
# Initialise eventlet and monkey patch before any other imports
import eventlet
eventlet.monkey_patch()

# Import the Flask app
from main import create_app, socketio

app = create_app()

# For Gunicorn
application = app

if __name__ == '__main__':
    socketio.run(app) 