"""Auction viewing routes."""

from main import socketio
from flask_socketio import join_room, leave_room
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.orm import joinedload
from . import authenticate_item_page
from ..models import db, Item, AuthenticationRequest, Message, Notification, MessageImage
from ..email_utils import send_notification_email
from ..s3_utils import upload_s3

MAX_SIZE = 1024 * 1024
MAX_IMAGES = 5


def allowed_file(filename):
    # Check if a file is an allowed type.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


# SocketIO event handlers
@socketio.on('join_chat')
def on_join(data):
    """User joins a chat room."""
    if not current_user.is_authenticated:
        return
    room = data.get('auth_url')
    authentication = AuthenticationRequest.query.filter_by(url=room).first()

    # Check user is allowed to join this room
    expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None
    is_creator = authentication.requester_id == current_user.id
    is_expert = expert and expert.expert_id == current_user.id and expert.status != 3
    is_admin = current_user.role == 3

    if not is_creator and not is_expert and not is_admin:
        return

    if room:
        join_room(room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a chat room."""
    room = data.get('auth_url')
    if room:
        leave_room(room)


@authenticate_item_page.route('/<url>')
@login_required
def index(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first_or_404()
    item = Item.query.filter_by(item_id=authentication.item_id).first()

    # If the item has expired and the authentication request is still pending, mark it as cancelled
    if item.auction_end < datetime.now() and authentication.status == 1:
        authentication.status = 4
        db.session.commit()

    # Check user is allowed to view this page
    expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None
    is_creator = authentication.requester_id == current_user.id
    is_expert = expert and expert.expert_id == current_user.id and expert.status != 3
    is_admin = current_user.role == 3

    if not is_creator and not is_expert and not is_admin:
        flash('You are not authorised to view this page.', 'danger')
        return redirect(url_for('home_page.index'))

    # Get messages with their images
    messages = Message.query.options(
        joinedload(Message.images)
    ).filter(
        Message.authentication_request_id == authentication.request_id
    ).order_by(Message.sent_at.asc()).all()

    # Pre-compute image URLs for each message
    for message in messages:
        setattr(message, 'image_urls', [image.get_url() for image in message.images])

    return render_template('authenticate_item.html', item=item, authentication=authentication.status, is_creator=is_creator, is_expert=is_expert, messages=messages)


@authenticate_item_page.route('/<url>/api/accept', methods=['POST'])
@login_required
def accept(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404

    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400

    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403

    if authentication.item.auction_end < datetime.now():
        return jsonify({'error': 'Auction has ended.'}), 400

    authentication.status = 2
    authentication.expert_assignments[-1].status = 2

    # Send notification to requester
    notification = Notification(
        user_id=authentication.requester_id,
        message=f'Your item has been authenticated!',
        item_url=authentication.item.url,
        item_title=authentication.item.title,
        notification_type=4
    )
    db.session.add(notification)
    db.session.commit()

    # Send real-time notifications
    try:
        socketio.emit('new_notification', {
            'message': notification.message,
            'item_url': notification.item_url,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{authentication.requester.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')

    # Send email
    send_notification_email(authentication.requester, notification)

    try:
        socketio.emit('force_reload', {'status': 'Authentication approved'}, room=url)
    except Exception as e:
        print(f'SocketIO Error: {e}')
    return jsonify({'success': 'Authentication request accepted.'})


@authenticate_item_page.route('/<url>/api/decline', methods=['POST'])
@login_required
def reject(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404

    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400

    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403

    if authentication.item.auction_end < datetime.now():
        return jsonify({'error': 'Auction has ended.'}), 400

    authentication.status = 3
    authentication.expert_assignments[-1].status = 2

    # Send notification to requester
    notification = Notification(
        user_id=authentication.requester_id,
        message=f'Your item authentication has been declined.',
        item_url=authentication.item.url,
        item_title=authentication.item.title,
        notification_type=4
    )
    db.session.add(notification)
    db.session.commit()

    # Send real-time notifications
    try:
        socketio.emit('new_notification', {
            'message': notification.message,
            'item_url': notification.item_url,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{authentication.requester.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')

    # Send email
    send_notification_email(authentication.requester, notification)

    try:
        socketio.emit('force_reload', {'status': 'Authentication declined'}, room=url)
    except Exception as e:
        print(f'SocketIO Error: {e}')
    return jsonify({'success': 'Authentication request rejected.'})


@authenticate_item_page.route('/<url>/api/reassign', methods=['POST'])
@login_required
def reassign(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404

    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400

    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403

    if authentication.item.auction_end < datetime.now():
        return jsonify({'error': 'Auction has ended.'}), 400

    authentication.expert_assignments[-1].status = 3
    db.session.commit()

    return jsonify({'success': 'Authentication request reassignment scheduled.'})


@authenticate_item_page.route('/<url>/api/message', methods=['POST'])
@login_required
def new_message(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404

    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400

    if authentication.item.auction_end < datetime.now():
        return jsonify({'error': 'Auction has ended.'}), 400

    # Check user is allowed to leave message
    expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None
    is_creator = authentication.requester_id == current_user.id
    is_expert = expert and expert.expert_id == current_user.id and expert.status != 3

    if not is_creator and not is_expert:
        return jsonify({'error': 'You are not authorised to leave a message.'}), 403

    message_text = request.form.get('content')
    if not message_text:
        return jsonify({'error': 'Message content is required.'}), 400

    # Create the message
    message = Message(
        authentication_request_id=authentication.request_id,
        sender_id=current_user.id,
        message_text=message_text,
        sent_at=datetime.now()
    )
    db.session.add(message)
    db.session.commit()

    # Upload image if provided
    files = request.files.getlist('files[]')
    image_urls = []

    if len(files) > MAX_IMAGES:
        return jsonify({'error': f'Maximum {MAX_IMAGES} images allowed per message.'}), 400

    for file in files:
        if file and file.filename:
            # Check file type and size
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Only jpg, jpeg, and png are allowed.'}), 400

            if len(file.read()) > MAX_SIZE:
                return jsonify({'error': 'Image file too large. Maximum size is 1MB.'}), 400

            file.seek(0)
            filename = secure_filename(file.filename)
            image_filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
            path = upload_s3(file, image_filename, folder='message_attachments', private=True)

            # Create message image entry
            message_image = MessageImage(
                message_id=message.message_id,
                image_key=path
            )
            db.session.add(message_image)
            db.session.commit()

            # Get image URL for real-time messaging
            image_url = message_image.get_url()
            image_urls.append(image_url)

    # Send real-time message
    try:
        socketio.emit('new_message', {
            'message': message.message_text,
            'sender': current_user.username,
            'sender_id': str(current_user.id),
            'sender_role': str(current_user.role),
            'images': image_urls,
            'sent_at': message.sent_at.strftime('%H:%M - %d/%m/%Y')
        }, room=url)
    except Exception as e:
        print(f'SocketIO Error: {e}')

    # Send notification to recipient
    if is_creator:
        recipient = authentication.expert_assignments[-1].expert if authentication.expert_assignments else None
    else:
        recipient = authentication.requester

    if recipient:
        notification = Notification(
            user_id=recipient.id,
            message=f'You have received a new message regarding an item authentication request.',
            item_url=authentication.item.url,
            item_title=authentication.item.title,
            notification_type=0
        )
        db.session.add(notification)
        db.session.commit()

        # Send real-time notifications
        try:
            socketio.emit('new_notification', {
                'id': notification.id,
                'message': notification.message,
                'item_url': notification.item_url,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{recipient.secret_key}')
        except Exception as e:
            print(f'SocketIO Error: {e}')

    return jsonify({'success': 'Your message has been sent.'})
