# main/socket_events.py
from flask_socketio import SocketIO, emit

# Initialize SocketIO
socketio = SocketIO()

def init_socketio(app):
    socketio.init_app(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

def send_notification(user_id, notification_data):
    """Send a real-time notification to a specific user"""
    socketio.emit('new_notification', notification_data, room=f'user_{user_id}')