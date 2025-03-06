"""Dashboard related routes."""

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from . import dashboard_page
from ..models import db, User, AuthenticationRequest, ExpertAssignment, Item, ManagerConfig, Bid


@dashboard_page.route('/')
@login_required
def index():
    """Dashboard page."""
    manager = {}
    expert = {}
    user = {}

    # Manager interface
    if current_user.role == 3:
        # Check manager configuration and set if not present
        manager['base_fee'] = ManagerConfig.query.filter_by(config_key='base_platform_fee').first()
        manager['authenticated_fee'] = ManagerConfig.query.filter_by(config_key='authenticated_platform_fee').first()
        manager['max_duration'] = ManagerConfig.query.filter_by(config_key='max_auction_duration').first()

        if not manager['base_fee']:
            base_fee = ManagerConfig(config_key='base_platform_fee', config_value='1.00', description='Base platform fee percentage for standard items')
            db.session.add(base_fee)
            manager['base_fee'] = base_fee.config_value
        else:
            manager['base_fee'] = float(manager['base_fee'].config_value)

        if not manager['authenticated_fee']:
            authenticated_fee = ManagerConfig(config_key='authenticated_platform_fee', config_value='5.00', description='Platform fee percentage for authenticated items')
            db.session.add(authenticated_fee)
            manager['authenticated_fee'] = authenticated_fee.config_value
        else:
            manager['authenticated_fee'] = float(manager['authenticated_fee'].config_value)

        if not manager['max_duration']:
            max_duration = ManagerConfig(config_key='max_auction_duration', config_value='5', description='Maximum auction duration in days')
            db.session.add(max_duration)
            manager['max_duration'] = max_duration.config_value
        else:
            manager['max_duration'] = int(manager['max_duration'].config_value)

        db.session.commit()

        # Get all user roles except managers
        manager['users'] = db.session.query(User).filter(User.role != 3).all()

        # Get all pending authentication requests without valid assignments
        pending_requests = AuthenticationRequest.query\
            .filter(and_(
                AuthenticationRequest.status == 1,
                or_(
                    ~AuthenticationRequest.expert_assignments.any(),
                    ~AuthenticationRequest.expert_assignments.any(ExpertAssignment.status != 3)
                )
            )).all()
        requests = []
        for request in pending_requests:
            eligible_experts = User.query\
                .filter(and_(
                    User.role == 2,
                    User.id != request.requester_id,
                    ~User.expert_assignments.any(ExpertAssignment.request_id == request.request_id)
                )).all()
            requests.append((request, eligible_experts))
        manager['requests'] = requests

        # Statistics Calculations
        now = datetime.now()
        
        # Total Revenue (sum of highest bids for completed auctions)
        completed_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(Item.auction_end < now)\
            .group_by(Item.item_id)\
            .subquery()
        total_revenue = db.session.query(func.sum(completed_auctions.c.highest_bid)).scalar() or 0.0
        manager['total_revenue'] = total_revenue

        # Commission Income (based on base_fee and authenticated_fee)
        authenticated_revenue = db.session.query(func.sum(completed_auctions.c.highest_bid))\
            .join(Item, Item.item_id == completed_auctions.c.item_id)\
            .join(AuthenticationRequest, AuthenticationRequest.item_id == Item.item_id)\
            .filter(AuthenticationRequest.status == 2)\
            .scalar() or 0.0
        standard_revenue = total_revenue - authenticated_revenue
        commission_income = (standard_revenue * (manager['base_fee'] / 100)) + (authenticated_revenue * (manager['authenticated_fee'] / 100))
        manager['commission_income'] = commission_income
        manager['commission_percentage'] = round((commission_income / total_revenue) * 100, 2) if total_revenue > 0 else 0.0

        # Active Auctions
        manager['active_auctions'] = Item.query.filter(and_(Item.auction_start <= now, Item.auction_end >= now)).count()

        # Total Users
        manager['user_count'] = User.query.count()

        # Revenue Data for Chart (monthly revenue for last 6 months)
        revenue_data = []
        revenue_labels = []
        for i in range(5, -1, -1):
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i * 30)
            end_date = start_date + timedelta(days=30)
            monthly_revenue = db.session.query(func.sum(Bid.bid_amount))\
                .join(Item, Item.item_id == Bid.item_id)\
                .filter(and_(Item.auction_end >= start_date, Item.auction_end < end_date))\
                .scalar() or 0.0
            revenue_data.append(monthly_revenue)
            revenue_labels.append(start_date.strftime('%b'))
        manager['revenue_data'] = revenue_data
        manager['revenue_labels'] = revenue_labels

    # Expert interface
    elif current_user.role == 2:
        expert['pending'] = ExpertAssignment.query\
            .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 1)).all()
        expert['complete'] = ExpertAssignment.query\
            .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 2)).all()

    # General User interface
    user['auctions'] = Item.query.filter_by(seller_id=current_user.id).all()[::-1]

    # Pass 'now' to the template for chart labels
    return render_template('dashboard.html', manager=manager, expert=expert, user=user, now=now)


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
    if ExpertAssignment.query.filter(and_(
            ExpertAssignment.request_id == request_id,
            ExpertAssignment.status != 3
        )).first():
        return jsonify({'error': 'Request already assigned'}), 400

    # Cannot assign non-expert
    if user.role != 2:
        return jsonify({'error': 'Cannot assign non-expert'}), 403

    # Cannot assign self
    if expert == current_user.id:
        return jsonify({'error': 'Cannot assign self'}), 403
    
    # Cannot assign expert to own request
    if authentication_request.requester_id == expert:
        return jsonify({'error': 'Cannot assign expert to own request'}), 403

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


@dashboard_page.route('/api/update-base', methods=['PUT'])
@login_required
def update_base():
    """Update the base platform fee."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_fee = request.json.get('fee')
    if not isinstance(new_fee, float) and not isinstance(new_fee, int):
        return jsonify({'error': 'Invalid fee'}), 400

    if new_fee < 0:
        return jsonify({'error': 'Fee must be positive'}), 400
    elif new_fee > 100:
        return jsonify({'error': 'Fee cannot be over 100'}), 400

    base = ManagerConfig.query.filter_by(config_key='base_platform_fee').first()
    if not base:
        base = ManagerConfig(
            config_key='base_platform_fee',
            description='Base platform fee percentage for standard items'
        )
        db.session.add(base)

    base.config_value = str(new_fee)
    db.session.commit()

    return jsonify({
        'message': 'Change successful',
        'config_key': base.config_key,
        'config_value': base.config_value
    }), 200


@dashboard_page.route('/api/update-auth', methods=['PUT'])
@login_required
def update_auth():
    """Update the authenticated item fee."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_fee = request.json.get('fee')
    if not isinstance(new_fee, float) and not isinstance(new_fee, int):
        return jsonify({'error': 'Invalid fee'}), 400

    if new_fee < 0:
        return jsonify({'error': 'Fee must be positive'}), 400
    elif new_fee > 100:
        return jsonify({'error': 'Fee cannot be over 100'}), 400

    auth = ManagerConfig.query.filter_by(config_key='authenticated_platform_fee').first()
    if not auth:
        auth = ManagerConfig(
            config_key='authenticated_platform_fee',
            description='Platform fee percentage for authenticated items'
        )
        db.session.add(auth)

    auth.config_value = str(new_fee)
    db.session.commit()

    return jsonify({
        'message': 'Change successful',
        'config_key': auth.config_key,
        'config_value': auth.config_value
    }), 200


@dashboard_page.route('/api/update-dur', methods=['PUT'])
@login_required
def update_dur():
    """Update the maximum listing duration."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_dur = request.json.get('days')
    if not isinstance(new_dur, int):
        return jsonify({'error': 'Invalid fee'}), 400

    if new_dur < 1:
        return jsonify({'error': 'Duration cannot be less than 1 day'}), 400
    elif new_dur > 365:
        return jsonify({'error': 'Duration cannot be over 1 year'}), 400

    dur = ManagerConfig.query.filter_by(config_key='max_auction_duration').first()
    if not dur:
        dur = ManagerConfig(
            config_key='max_auction_duration',
            description='Maximum auction duration in days'
        )
        db.session.add(dur)

    dur.config_value = str(new_dur)
    db.session.commit()

    return jsonify({
        'message': 'Change successful',
        'config_key': dur.config_key,
        'config_value': dur.config_value
    }), 200

