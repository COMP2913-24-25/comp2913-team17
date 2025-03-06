"""Dashboard related routes."""

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_
from . import dashboard_page
from ..models import ExpertAvailability, db, User, AuthenticationRequest, ExpertAssignment, Item, ManagerConfig, WatchedItem


def get_expert_availability(expert):
    # Returns a string indicating the expert's availability for today.
    today = date.today()
    avail = None
    if expert.expert_availabilities:
        for a in expert.expert_availabilities:
            if a.day == today:
                avail = a
                break
    now = datetime.now().time()
    if avail:
        if avail.status:  # Expert is marked available in the record
            if avail.start_time <= now < avail.end_time:
                return "Currently available"
            elif now < avail.start_time:
                delta = (datetime.combine(today, avail.start_time) - datetime.combine(today, now)).seconds // 3600
                return f"Available in {delta} hour{'s' if delta != 1 else ''}"
            else:
                return "Not available today"
        else:
            return "Not available today"
    return "Availability not set"


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
        manager['base_fee'] = ManagerConfig.query.filter_by(config_key='base_platform_fee')
        manager['authenticated_fee'] = ManagerConfig.query.filter_by(config_key='authenticated_platform_fee')
        manager['max_duration'] = ManagerConfig.query.filter_by(config_key='max_auction_duration')

        if not manager['base_fee']:
            base_fee = ManagerConfig(
                config_key='base_platform_fee',
                config_value=1.00,
                description='Base platform fee percentage for standard items'
            )
            db.session.add(base_fee)
            manager['base_fee'] = base_fee
        else:
            manager['base_fee'] = manager['base_fee'].first().config_value

        if not manager['authenticated_fee']:
            authenticated_fee = ManagerConfig(
                config_key='authenticated_platform_fee',
                config_value=5.00,
                description='Platform fee percentage for authenticated items'
            )
            db.session.add(authenticated_fee)
            manager['authenticated_fee'] = authenticated_fee
        else:
            manager['authenticated_fee'] = manager['authenticated_fee'].first().config_value

        if not manager['max_duration']:
            max_duration = ManagerConfig(
                config_key='max_auction_duration',
                config_value=5,
                description='Maximum auction duration in days'
            )
            db.session.add(max_duration)
            manager['max_duration'] = max_duration
        else:
            manager['max_duration'] = manager['max_duration'].first().config_value

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
        for req in pending_requests:
            eligible_experts = User.query\
                .filter(and_(
                    User.role == 2,
                    User.id != req.requester_id,
                    ~User.expert_assignments.any(
                        ExpertAssignment.request_id == req.request_id
                    )
                )).all()
            requests.append((req, eligible_experts))
        manager['requests'] = requests

    # Expert interface
    elif current_user.role == 2:
        expert['pending'] = ExpertAssignment.query\
            .filter(and_(
                ExpertAssignment.expert_id == current_user.id,
                ExpertAssignment.status == 1
            )).all()
        
        expert['complete'] = ExpertAssignment.query\
            .filter(and_(
                ExpertAssignment.expert_id == current_user.id,
                ExpertAssignment.status == 2
            )).all()

    # General User interface, all users can see their own auctions
    user['auctions'] = Item.query.filter_by(seller_id=current_user.id).all()[::-1
    # Add watched items
    watched_items = db.session.query(Item)\
        .join(WatchedItem, WatchedItem.item_id == Item.item_id)\
        .filter(WatchedItem.user_id == current_user.id)\
        .all()
    
    user['watched_items'] = watched_items

    return render_template('dashboard.html', manager=manager, expert=expert, user=user, get_expert_availability=get_expert_availability)

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
    if ExpertAssignment.query.filter(
            and_(ExpertAssignment.request_id == request_id,
                 ExpertAssignment.status != 3)
        ).first():
        return jsonify({'error': 'Request already assigned'}), 400

    # Cannot assign non-expert
    if user.role != 2:
        return jsonify({'error': 'Cannot assign non-expert'}), 403

    # Prevent self-assignment and assigning expert to own request
    if expert == current_user.id:
        return jsonify({'error': 'Cannot assign self'}), 403
    if authentication_request.requester_id == expert:
        return jsonify({'error': 'Cannot assign expert to own request'}), 403

    # The expert must have at least one availability record between now and auction end day (inclusive)
    item = authentication_request.item  # Assumes relationship exists
    auction_end = item.auction_end        # Auction end as datetime
    auction_end_date = auction_end.date()
    threshold_time = (auction_end - timedelta(hours=3)).time()  # On auction end day

    now_dt = datetime.now()
    now_date = now_dt.date()
    now_time = now_dt.time()

    # Get all availability records for the expert between now and auction end date (inclusive)
    avail_records = db.session.query(ExpertAvailability).filter(
        ExpertAvailability.expert_id == expert,
        ExpertAvailability.day >= now_date,
        ExpertAvailability.day <= auction_end_date
    ).all()

    valid = False
    for record in avail_records:
        if not record.status:
            continue
        if record.day == now_date:
            # For today: expert must be available later than now.
            if now_time < record.end_time:
                valid = True
                break
        elif record.day < auction_end_date:
            # For intermediate days, any available record counts.
            valid = True
            break
        else:  # record.day == auction_end_date
            # On the auction end day, expert must be available at least until threshold_time.
            if record.end_time >= threshold_time:
                valid = True
                break

    if not valid:
        return jsonify({'error': 'Expert is not available at any time from now until 3 hours before auction end'}), 400

    # All checks passed—create the assignment.
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
