"""Dashboard related routes."""

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from . import dashboard_page
from ..models import db, User


@dashboard_page.route('/')
@login_required
def index():
    """Dashboard page."""
    users = None

    # Get all non-managers if user is a manager
    if current_user.role == 3:
        users = db.session.query(User).filter(User.role != 3).all()
    return render_template('dashboard.html', users=users)


@dashboard_page.route('/api/users/<user_id>/role', methods=['PATCH'])
@login_required
def update_user_role(user_id):
    """Update the role of a user."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_role = request.json.get('role')

    # User = 1, Expert = 2, Manager = 3
    if new_role not in [1, 2, 3]:
        return jsonify({'error': 'Invalid role'}), 400

    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    if user.role == 3:
        return jsonify({'error': 'Cannot change manager role'}), 403

    # Prevent self-modification
    if int(user_id) == current_user.id:
        return jsonify({'error': 'Cannot modify own role'}), 403
    
    if user.role == new_role:
        return jsonify({'error': 'User already has this role'}), 400

    time = datetime.now()
    user.role = new_role
    user.updated_at = time
    db.session.commit()

    return jsonify({
        'message': 'Role updated successfully',
        'user_id': user.id,
        'new_role': user.role,
        'updated_at': time
    }), 200
