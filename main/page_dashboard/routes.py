"""Dashboard related routes."""

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import and_
from . import dashboard_page
from ..models import db, User, AuthenticationRequest, ExpertAssignment, Item


@dashboard_page.route('/')
@login_required
def index():
    """Dashboard page."""
    manager = {}
    expert = {}
    user = {}

    # Manager interface
    if current_user.role == 3:
        # Get all user roles except managers
        manager['users'] = db.session.query(User).filter(User.role != 3).all()

        # Get all pending authentication requests without assignments
        manager['requests'] = AuthenticationRequest.query\
            .filter(and_(
                AuthenticationRequest.status == 1,
                ~AuthenticationRequest.expert_assignments.any()
            )).all()

        # Get all available experts, for now all experts - add filtering later
        manager['experts'] = User.query.filter_by(role=2).all()
    # Expert interface
    elif current_user.role == 2:
        expert['requests'] = ExpertAssignment.query.filter_by(expert_id=current_user.id).all()
    
    # General User interface, all users can see their own auctions
    user['auctions'] = Item.query.filter_by(seller_id=current_user.id).all()[::-1]

    return render_template('dashboard.html', manager=manager, expert=expert, user=user)


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

@dashboard_page.route('/api/assign-expert/<request_id>', methods=['POST'])
@login_required
def assign_expert(request_id):
    """Assign an expert to an authentication request."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400
    
    authentication_request = db.session.query(AuthenticationRequest).filter_by(request_id=request_id).first()
    if authentication_request is None:
        return jsonify({'error': 'Request not found'}), 404
    
    if authentication_request.status != 1:
        return jsonify({'error': 'Request not pending'}), 400

    expert = request.json.get('expert')

    if not isinstance(expert, int):
        return jsonify({'error': 'Invalid expert'}), 400

    user = db.session.query(User).filter_by(id=expert).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    # Cannot double-assign
    if ExpertAssignment.query.filter_by(request_id=request_id).first():
        return jsonify({'error': 'Request already assigned'}), 400

    # Cannot assign non-expert
    if user.role != 2:
        return jsonify({'error': 'Cannot assign non-expert'}), 403
    
    # Cannot assign self
    if expert == current_user.id:
        return jsonify({'error': 'Cannot assign self'}), 403
    
    assignment = ExpertAssignment(
        request_id=request_id,
        expert_id=expert
    )
    db.session.add(assignment)
    db.session.commit()

    return jsonify({
        'message': 'Assignment successful',
        'request_id': request_id,
        'expert_id': expert
    }), 200
