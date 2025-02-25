"""Launches the Flask app with WebSocket support"""

from main import create_app
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app, debug=True)
