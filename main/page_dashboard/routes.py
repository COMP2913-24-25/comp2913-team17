"""Dashboard related routes."""

from app import socketio
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_, func
from . import dashboard_page
from ..models import ExpertAvailability, db, User, AuthenticationRequest, ExpertAssignment, Item, ManagerConfig, Bid, Notification, Message, Category, ExpertCategory
from ..email_utils import send_notification_email


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


def get_expertise(expert, item):
    # Returns a string indicating the expert's expertise in relation to the item.
    if expert.expert_categories:
        for cat in expert.expert_categories:
            if cat.category_id == item.category_id:
                return 'Expert'
    return 'Not an Expert'


@dashboard_page.route('/')
@login_required
def index():
    """Dashboard page."""
    manager = {}
    expert = {}
    user = {}
    now = datetime.now()

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

        # Statistics Calculations
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
        
        total_revenue = float(total_revenue)
        authenticated_revenue = float(authenticated_revenue)
        
        standard_revenue = total_revenue - authenticated_revenue
        commission_income = (standard_revenue * (manager['base_fee'] / 100)) + (authenticated_revenue * (manager['authenticated_fee'] / 100))
        manager['commission_income'] = commission_income
        manager['commission_percentage'] = round((commission_income / total_revenue) * 100, 2) if total_revenue > 0 else 0.0

        # Active Auctions
        manager['active_auctions'] = Item.query.filter(and_(Item.auction_start <= now, Item.auction_end >= now)).count()

        # Total Users
        manager['user_count'] = User.query.count()

        # Revenue Data for Chart (monthly revenue for last 6 months)
        manager['revenue_data'] = []
        manager['revenue_labels'] = []

        for i in range(5, -1, -1):
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i * 30)
            end_date = start_date + timedelta(days=30)
            
            # Get highest bid for each ended auction in this period
            monthly_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
                .join(Bid, Item.item_id == Bid.item_id)\
                .filter(and_(
                    Item.auction_end >= start_date, 
                    Item.auction_end < end_date,
                    Item.auction_end < now  # Only include ended auctions
                ))\
                .group_by(Item.item_id)\
                .subquery()
            
            # Sum the highest bids from each auction
            monthly_revenue = db.session.query(func.sum(monthly_auctions.c.highest_bid)).scalar()
            
            # Convert None to 0.0 for JSON
            if monthly_revenue is None:
                monthly_revenue = 0.0
            else:
                # Ensure the value is float
                monthly_revenue = float(monthly_revenue)
    
            manager['revenue_data'].append(monthly_revenue)
            manager['revenue_labels'].append(start_date.strftime('%b'))

    # Expert interface
    elif current_user.role == 2:
        expert['pending'] = ExpertAssignment.query\
            .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 1)).all()
        expert['complete'] = ExpertAssignment.query\
            .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 2)).all()
        
        # Get a list of expert's experise as well as all categories
        expert['categories'] = Category.query.order_by(Category.name).all()
        expert['expertise'] = Category.query.join(
            ExpertCategory, 
            Category.id == ExpertCategory.category_id
        ).filter(
            ExpertCategory.expert_id == current_user.id
        ).all()

    # General User interface, all users can see their own auctions
    user['auctions'] = Item.query.filter_by(seller_id=current_user.id).all()[::-1]
    user_data = {
        'auctions': user['auctions'],
        'watched_items': current_user.watched_items.all() if hasattr(current_user, 'watched_items') else []
    }
    return render_template('dashboard.html', manager=manager, expert=expert, user=user_data, now=now, get_expert_availability=get_expert_availability, get_expertise=get_expertise)


@dashboard_page.route('/api/users/<user_id>/role', methods=['PATCH'])
@login_required
def update_user_role(user_id):
    """Update the role of a user."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_role = request.json.get('role')
    role_strings = ['User', 'Expert', 'Manager']

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
    old_role = user.role
    user.role = new_role
    user.updated_at = time

    # Send notification to user whose role was changed
    notification = Notification(
        user_id=user.id,
        message=f'Your role has been updated from {role_strings[old_role - 1]} to {role_strings[new_role - 1]}',
        notification_type=0
    )
    db.session.add(notification)
    db.session.commit()
        
    # Send real-time notification
    try:
        socketio.emit('new_notification', {
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{user.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')
        
    # Send email
    send_notification_email(user, notification)

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
        # If the availability is on a day before the auction end day, it's valid.
        if record.day < auction_end_date:
            valid = True
            break
        # If the availability is on the auction end day, then ensure it doesn't start too late.
        elif record.day == auction_end_date:
            # Calculate the threshold time (auction end time minus 3 hours)
            threshold_time = (auction_end - timedelta(hours=3)).time()
            # The expert's availability is valid only if it starts before the threshold.
            if record.start_time < threshold_time:
                valid = True
                break

    if not valid:
        return jsonify({'error': 'Expert is not available at any time before the last 3 hours of the auction'}), 400


    # All checks passed—create the assignment.
    assignment = ExpertAssignment(
        request_id=request_id,
        expert_id=expert
    )
    db.session.add(assignment)

    # Create new message in the chat
    message = Message(
        authentication_request_id=request_id,
        sender_id=expert,
        message_text='Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
        sent_at=datetime.now()
    )
    db.session.add(message)

    # Send notification to expert and requester
    notification_expert = Notification(
        user_id=expert,
        message=f'You have been assigned to authenticate an item',
        item_url=item.url,
        item_title=item.title,
        notification_type=4
    )
    db.session.add(notification_expert)

    notification_requester = Notification(
        user_id=authentication_request.requester_id,
        message=f'An expert has been assigned to authenticate your item',
        item_url=item.url,
        item_title=item.title,
        notification_type=4
    )
    db.session.add(notification_requester)
    db.session.commit()
        
    # Send real-time notifications
    try:
        socketio.emit('new_notification', {
            'message': notification_expert.message,
            'item_url': notification_expert.item_url, 
            'created_at': notification_expert.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{user.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')

    try:
        socketio.emit('new_notification', {
            'message': notification_requester.message,
            'item_url': notification_requester.item_url, 
            'created_at': notification_requester.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{authentication_request.requester.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')
        
    # Send emails
    send_notification_email(user, notification_expert)
    send_notification_email(authentication_request.requester, notification_requester)

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


@dashboard_page.route('/api/expert/<int:user_id>', methods=['PUT'])
@login_required
def update_expertise(user_id):
    """Update the expertise of an expert."""
    if current_user.role != 2:
        return jsonify({'error': 'Unauthorised'}), 403
    
    if current_user.id != int(user_id):
        return jsonify({'error': 'Cannot modify other user\'s expertise'}), 403

    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400

    new_expertise = request.json.get('expertise')

    if not isinstance(new_expertise, list):
        return jsonify({'error': 'Invalid expertise format'}), 400
    
    # Get all categories
    categories = Category.query.all()
    category_ids = {c.id for c in categories}

    # Check if all expertise are valid
    for cat in new_expertise:
        if not isinstance(cat, int) or cat not in category_ids:
            return jsonify({'error': 'Invalid expertise'}), 400

    # Remove all existing expertise
    ExpertCategory.query.filter_by(expert_id=user_id).delete()

    # Add new expertise
    for cat in new_expertise:
        expertise = ExpertCategory(expert_id=user_id, category_id=cat)
        db.session.add(expertise)
    db.session.commit()

    return jsonify({
        'message': 'Expertise updated successfully',
        'expertise': new_expertise
    }), 200