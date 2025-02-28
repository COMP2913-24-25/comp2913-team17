"""Launches the Flask app with WebSocket support"""

from main import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
