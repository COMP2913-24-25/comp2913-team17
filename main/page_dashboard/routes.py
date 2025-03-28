"""Dashboard related routes."""

from main import socketio
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from sqlalchemy import and_, or_, func
from random import choice
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
    return 'Not Expert'

def calculate_expert_suitability(expert, request, all_experts_assignments, now):
    # Calculate an expert's suitability score for a request.
    # Availability Score (40%)
    today = date.today()
    auction_end = request.item.auction_end.date()
    avail_score = 0
    for avail in expert.expert_availabilities:
        if avail.day >= today and avail.day <= auction_end and avail.status:
            if avail.day == today:
                current_time = now.time()
                if avail.start_time <= current_time < avail.end_time:
                    # Currently available
                    avail_score = 1.0
                    break
                elif current_time < avail.start_time:
                    # Available later today
                    avail_score = max(avail_score, 0.7)
            else:
                # Available in future
                avail_score = max(avail_score, 0.5)

    # Workload Score (30%) - max 5 assignments
    current_assignments = all_experts_assignments.get(expert.id, 0)
    workload_score = max(0, 1 - (current_assignments / 5))

    # Expertise Score (30%)
    expertise_score = 0
    for cat in expert.expert_categories:
        if cat.category_id == request.item.category_id:
            expertise_score = 1.0
            break

    total_score = (0.4 * avail_score) + (0.3 * workload_score) + (0.3 * expertise_score)
    return total_score

@dashboard_page.route('/')
@login_required
def index():
    """Dashboard page that redirects to relevant dashboard based on user role."""
    now = datetime.now()

    if current_user.role == 3:
        return handle_manager(now)
    elif current_user.role == 2:
        return handle_expert(now)
    else:
        return handle_user(now)


def handle_manager(now):
    """Handle the dashboard for a manager."""
    manager = {}

    # Manager configuration
    manager['base_fee'] = ManagerConfig.query.filter_by(config_key='base_platform_fee').first()
    manager['authenticated_fee'] = ManagerConfig.query.filter_by(config_key='authenticated_platform_fee').first()
    manager['max_duration'] = ManagerConfig.query.filter_by(config_key='max_auction_duration').first()

    if not manager['base_fee']:
        base_fee = ManagerConfig(config_key='base_platform_fee', config_value='1.00',
                                 description='Base platform fee percentage for standard items')
        db.session.add(base_fee)
        manager['base_fee'] = base_fee.config_value
    else:
        manager['base_fee'] = float(manager['base_fee'].config_value)

    if not manager['authenticated_fee']:
        authenticated_fee = ManagerConfig(config_key='authenticated_platform_fee',
                                          config_value='5.00', description='Platform fee percentage for authenticated items')
        db.session.add(authenticated_fee)
        manager['authenticated_fee'] = authenticated_fee.config_value
    else:
        manager['authenticated_fee'] = float(manager['authenticated_fee'].config_value)

    if not manager['max_duration']:
        max_duration = ManagerConfig(config_key='max_auction_duration', config_value='5',
                                     description='Maximum auction duration in days')
        db.session.add(max_duration)
        manager['max_duration'] = max_duration.config_value
    else:
        manager['max_duration'] = int(manager['max_duration'].config_value)

    db.session.commit()

    # Get all user roles except managers ordered by role and username
    manager['users'] = db.session.query(User).filter(
        User.role != 3).order_by(User.role.desc(), User.username.asc()).all()

    # Pending authentication requests
    manager_authentications(manager, now)

    # Statistics calculations
    manager_stats(manager, now)

    return render_template('dashboard_manager.html', manager=manager, now=now, get_expert_availability=get_expert_availability, get_expertise=get_expertise)

def manager_authentications(manager, now):
    """Handle pending authentication requests for a manager."""
    pending_requests = AuthenticationRequest.query\
        .filter(and_(
            AuthenticationRequest.status == 1,
            or_(
                ~AuthenticationRequest.expert_assignments.any(),
                ~AuthenticationRequest.expert_assignments.any(ExpertAssignment.status != 3)
            )
        )).all()

    requests = []
    all_experts_assignments = dict(db.session.query(
        ExpertAssignment.expert_id, func.count(ExpertAssignment.request_id)
    ).filter(ExpertAssignment.status.in_([1, 2])).group_by(ExpertAssignment.expert_id).all())

    for req in pending_requests:
        eligible_experts = User.query\
            .filter(and_(
                User.role == 2,
                User.id != req.requester_id,
                ~User.expert_assignments.any(
                    ExpertAssignment.request_id == req.request_id
                )
            )).order_by(User.username.asc()).all()
        # Calculate AI expert recommendation for eligible experts
        if eligible_experts:
            scores = [(expert, calculate_expert_suitability(expert, req, all_experts_assignments, now))
                      for expert in eligible_experts]
            max_score = max(score for _, score in scores) if scores else 0
            best_experts = [expert for expert, score in scores if score == max_score]
            # Pick randomly in case of tie
            recommended_expert = choice(best_experts) if best_experts else None
        else:
            recommended_expert = None
        requests.append((req, eligible_experts, recommended_expert))
    manager['requests'] = requests

def manager_stats(manager, now):
    """Compute manager statistics."""
    # Projected Revenue (sum of highest bids for all completed auctions, paid and unpaid)
    completed_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
        .join(Bid, Item.item_id == Bid.item_id)\
        .filter(Item.auction_end < now)\
        .group_by(Item.item_id)\
        .subquery()
    projected_revenue = db.session.query(func.sum(completed_auctions.c.highest_bid)).scalar() or 0.0
    manager['projected_revenue'] = projected_revenue

    # Paid Revenue (sum of highest bids for paid auctions only, status == 3)
    paid_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
        .join(Bid, Item.item_id == Bid.item_id)\
        .filter(Item.auction_end < now, Item.status == 3)\
        .group_by(Item.item_id)\
        .subquery()
    paid_revenue = db.session.query(func.sum(paid_auctions.c.highest_bid)).scalar() or 0.0
    manager['paid_revenue'] = paid_revenue

    # Get all paid authenticated items
    authenticated_items = db.session.query(paid_auctions.c.item_id)\
        .select_from(paid_auctions)\
        .join(AuthenticationRequest, AuthenticationRequest.item_id == paid_auctions.c.item_id)\
        .filter(AuthenticationRequest.status == 2)\
        .subquery()

    # Get authenticated item commission
    authenticated_commission = db.session.query(func.sum(paid_auctions.c.highest_bid * Item.auth_fee / 100))\
        .select_from(paid_auctions)\
        .join(Item, Item.item_id == paid_auctions.c.item_id)\
        .filter(Item.item_id.in_(
            db.session.query(authenticated_items.c.item_id)
        ))\
        .scalar() or 0.0

    # Get unauthenticated item commission
    unauthenticated_commission = db.session.query(func.sum(paid_auctions.c.highest_bid * Item.base_fee / 100))\
        .select_from(paid_auctions)\
        .join(Item, Item.item_id == paid_auctions.c.item_id)\
        .filter(Item.item_id.notin_(
            db.session.query(authenticated_items.c.item_id)
        ))\
        .scalar() or 0.0

    paid_revenue = float(paid_revenue)
    authenticated_commission = float(authenticated_commission)
    unauthenticated_commission = float(unauthenticated_commission)

    commission_income = authenticated_commission + unauthenticated_commission
    manager['commission_income'] = commission_income
    manager['commission_percentage'] = round((commission_income / paid_revenue) * 100, 2) if paid_revenue > 0 else 0.0

    # Active Auctions
    manager['active_auctions'] = Item.query.filter(and_(Item.auction_start <= now, Item.auction_end >= now)).count()

    # Total Users
    manager['user_count'] = User.query.count()

    # Paid vs Total Completed Auctions
    manager['paid_auctions_count'] = Item.query.filter(Item.auction_end < now, Item.status == 3).count()
    manager['total_completed_auctions'] = Item.query.filter(Item.auction_end < now).count()

    # Revenue Data for Chart (1 week, 1 month, 6 months, both projected and paid)
    manager['revenue_data'] = {
        'week': {'projected': {'labels': [], 'values': []}, 'paid': {'labels': [], 'values': []}},
        'month': {'projected': {'labels': [], 'values': []}, 'paid': {'labels': [], 'values': []}},
        'six_months': {'projected': {'labels': [], 'values': []}, 'paid': {'labels': [], 'values': []}}
    }

    # 1 Week (daily revenue for last 7 days)
    for i in range(6, -1, -1):
        start_date = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        # Projected (all completed auctions)
        daily_projected_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now
            ))\
            .group_by(Item.item_id)\
            .subquery()
        daily_projected_revenue = db.session.query(func.sum(daily_projected_auctions.c.highest_bid)).scalar() or 0.0
        daily_projected_revenue = float(daily_projected_revenue)

        # Paid (status == 3)
        daily_paid_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now,
                Item.status == 3
            ))\
            .group_by(Item.item_id)\
            .subquery()
        daily_paid_revenue = db.session.query(func.sum(daily_paid_auctions.c.highest_bid)).scalar() or 0.0
        daily_paid_revenue = float(daily_paid_revenue)

        manager['revenue_data']['week']['projected']['values'].append(daily_projected_revenue)
        manager['revenue_data']['week']['paid']['values'].append(daily_paid_revenue)
        manager['revenue_data']['week']['projected']['labels'].append(start_date.strftime('%a'))
        manager['revenue_data']['week']['paid']['labels'].append(start_date.strftime('%a'))

    # 1 Month (weekly revenue for last 4 weeks)
    for i in range(3, -1, -1):
        start_date = (now - timedelta(days=i * 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)

        # Projected (all completed auctions)
        weekly_projected_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now
            ))\
            .group_by(Item.item_id)\
            .subquery()
        weekly_projected_revenue = db.session.query(func.sum(weekly_projected_auctions.c.highest_bid)).scalar() or 0.0
        weekly_projected_revenue = float(weekly_projected_revenue)

        # Paid (status == 3)
        weekly_paid_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now,
                Item.status == 3
            ))\
            .group_by(Item.item_id)\
            .subquery()
        weekly_paid_revenue = db.session.query(func.sum(weekly_paid_auctions.c.highest_bid)).scalar() or 0.0
        weekly_paid_revenue = float(weekly_paid_revenue)

        manager['revenue_data']['month']['projected']['values'].append(weekly_projected_revenue)
        manager['revenue_data']['month']['paid']['values'].append(weekly_paid_revenue)
        manager['revenue_data']['month']['projected']['labels'].append(f"Week {4 - i}")
        manager['revenue_data']['month']['paid']['labels'].append(f"Week {4 - i}")

    # 6 Months (monthly revenue for last 6 months)
    for i in range(5, -1, -1):
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i * 30)
        end_date = start_date + timedelta(days=30)

        # Projected (all completed auctions)
        monthly_projected_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now
            ))\
            .group_by(Item.item_id)\
            .subquery()
        monthly_projected_revenue = db.session.query(func.sum(monthly_projected_auctions.c.highest_bid)).scalar() or 0.0
        monthly_projected_revenue = float(monthly_projected_revenue)

        # Paid (status == 3)
        monthly_paid_auctions = db.session.query(Item.item_id, func.max(Bid.bid_amount).label('highest_bid'))\
            .join(Bid, Item.item_id == Bid.item_id)\
            .filter(and_(
                Item.auction_end >= start_date,
                Item.auction_end < end_date,
                Item.auction_end < now,
                Item.status == 3
            ))\
            .group_by(Item.item_id)\
            .subquery()
        monthly_paid_revenue = db.session.query(func.sum(monthly_paid_auctions.c.highest_bid)).scalar() or 0.0
        monthly_paid_revenue = float(monthly_paid_revenue)

        manager['revenue_data']['six_months']['projected']['values'].append(monthly_projected_revenue)
        manager['revenue_data']['six_months']['paid']['values'].append(monthly_paid_revenue)
        manager['revenue_data']['six_months']['projected']['labels'].append(start_date.strftime('%b'))
        manager['revenue_data']['six_months']['paid']['labels'].append(start_date.strftime('%b'))

def handle_expert(now):
    """Handle the dashboard for an expert."""
    expert = {}

    # Authentication assignments
    expert['pending'] = ExpertAssignment.query\
        .join(ExpertAssignment.authentication_request)\
        .join(AuthenticationRequest.item)\
        .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 1))\
        .order_by(Item.auction_end.asc())\
        .all()
    expert['complete'] = ExpertAssignment.query\
        .filter(and_(ExpertAssignment.expert_id == current_user.id, ExpertAssignment.status == 2)).all()

    # Get a list of expert's expertise as well as all categories
    expert['categories'] = Category.query.order_by(Category.name).all()
    expert['expertise'] = Category.query.join(
        ExpertCategory,
        Category.id == ExpertCategory.category_id
    ).filter(
        ExpertCategory.expert_id == current_user.id
    ).all()

    return render_template('dashboard_expert.html', expert=expert, now=now)


def handle_user(now):
    """Handle the dashboard for a user."""
    user = {}

    # General User interface, all users can see their own auctions
    user['auctions'] = Item.query.filter_by(seller_id=current_user.id).all()[::-1]

    # Get auctions the user has participated in (via bidding, winning or paying)
    # Bidding: any open auction (status == 1) where the user has at least one bid.
    bidding_items = (
        Item.query.join(Bid, Item.item_id == Bid.item_id)
        .filter(Bid.bidder_id == current_user.id, Item.status == 1)
        .distinct()
        .all()
    )

    # Won: auctions that are finalized (status == 2) where the user is the winner.
    won_items = (
        Item.query.filter(Item.status == 2, Item.winning_bid.has(bidder_id=current_user.id))
        .all()
    )
    # Paid: auctions where the item is paid for (status == 3) and the user is the winner.
    paid_items = (
        Item.query.filter(Item.status == 3, Item.winning_bid.has(bidder_id=current_user.id))
        .all()
    )

    user['participated_auctions'] = {
        'bidding': bidding_items,
        'won': won_items,
        'paid': paid_items
    }

    user_data = {
        'auctions': user['auctions'],
        'watched_items': current_user.watched_items.all() if hasattr(current_user, 'watched_items') else [],
        'participated_auctions': user['participated_auctions']
    }

    return render_template('dashboard_user.html', user=user_data, now=now)

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
        'updated_date': time.strftime('%d/%m/%Y'),
        'updated_time': time.strftime('%H:%M:%S')
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

    try:
        socketio.emit('new_message', {
            'message': 'Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
            'sender': user.username,
            'sender_id': str(expert),
            'sender_role': str(2),
            'images': None,
            'sent_at': message.sent_at.strftime('%H:%M - %d/%m/%Y')
        }, room=authentication_request.url)
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

@dashboard_page.route('/api/auto-assign-expert/<request_id>', methods=['POST'])
@login_required
def auto_assign_expert(request_id):
    """Auto-assign the recommended expert to an authentication request."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    auth_request = db.session.query(AuthenticationRequest).filter_by(request_id=request_id).first()
    if not auth_request:
        return jsonify({'error': 'Request not found'}), 404
    if auth_request.status != 1:
        return jsonify({'error': 'Request not pending'}), 400

    # Check for existing valid assignment
    if ExpertAssignment.query.filter(
            and_(ExpertAssignment.request_id == request_id, ExpertAssignment.status != 3)).first():
        return jsonify({'error': 'Request already assigned'}), 400

    # Get eligible experts
    eligible_experts = User.query\
        .filter(and_(
            User.role == 2,
            User.id != auth_request.requester_id,
            ~User.expert_assignments.any(ExpertAssignment.request_id == request_id)
        )).all()
    if not eligible_experts:
        return jsonify({'error': 'No available experts'}), 400

    # Calculate suitability scores
    now = datetime.now()

    # Get number of pending assignments for each expert
    all_experts_assignments = dict(db.session.query(
        ExpertAssignment.expert_id, func.count(ExpertAssignment.request_id)
    ).filter(ExpertAssignment.status == 1).group_by(ExpertAssignment.expert_id).all())

    scores = [(expert, calculate_expert_suitability(expert, auth_request, all_experts_assignments, now))
              for expert in eligible_experts]
    max_score = max(score for _, score in scores)
    best_experts = [expert for expert, score in scores if score == max_score]
    best_expert_ids = set(expert.id for expert in best_experts)
    print(best_expert_ids)

    # Preferentially pick the expert displayed in the recommendation
    if request.is_json and request.json.get('recommendation') and request.json.get('recommendation') in best_expert_ids:
        recommended_expert = User.query.filter_by(id=request.json['recommendation']).first()
    else:
        recommended_expert = choice(best_experts)

    # Assign the expert
    assignment = ExpertAssignment(request_id=request_id, expert_id=recommended_expert.id)
    db.session.add(assignment)

    # Create message
    message = Message(
        authentication_request_id=request_id,
        sender_id=recommended_expert.id,
        message_text='Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
        sent_at=now
    )
    db.session.add(message)

    # Send notifications
    notification_expert = Notification(
        user_id=recommended_expert.id,
        message=f'You have been assigned to authenticate {auth_request.item.title}',
        item_url=auth_request.item.url,
        item_title=auth_request.item.title,
        notification_type=4
    )
    notification_requester = Notification(
        user_id=auth_request.requester_id,
        message=f'An expert has been assigned to authenticate your item: {auth_request.item.title}',
        item_url=auth_request.item.url,
        item_title=auth_request.item.title,
        notification_type=4
    )
    db.session.add_all([notification_expert, notification_requester])
    db.session.commit()

    # Send real-time notifications and emails
    try:
        socketio.emit('new_notification', {
            'message': notification_expert.message,
            'item_url': notification_expert.item_url,
            'created_at': notification_expert.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{recommended_expert.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')

    try:
        socketio.emit('new_notification', {
            'message': notification_requester.message,
            'item_url': notification_requester.item_url,
            'created_at': notification_requester.created_at.strftime('%Y-%m-%d %H:%M')
        }, room=f'user_{auth_request.requester.secret_key}')
    except Exception as e:
        print(f'SocketIO Error: {e}')

    try:
        socketio.emit('new_message', {
            'message': message.message_text,
            'sender': recommended_expert.username,
            'sender_id': str(recommended_expert.id),
            'sender_role': str(2),
            'images': None,
            'sent_at': message.sent_at.strftime('%H:%M - %d/%m/%Y')
        }, room=auth_request.url)
    except Exception as e:
        print(f'SocketIO Error: {e}')

    send_notification_email(recommended_expert, notification_expert)
    send_notification_email(auth_request.requester, notification_requester)

    return jsonify({
        'message': 'Expert auto-assigned successfully',
        'request_id': request_id,
        'expert_id': recommended_expert.id
    }), 200

@dashboard_page.route('/api/bulk-auto-assign-experts', methods=['POST'])
@login_required
def bulk_auto_assign_experts():
    """Auto-assign experts to multiple authentication requests."""
    if current_user.role != 3:
        return jsonify({'error': 'Unauthorised'}), 403

    if not request.is_json or 'request_ids' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400

    request_ids = request.json['request_ids']
    if not isinstance(request_ids, list):
        return jsonify({'error': 'Request IDs must be a list'}), 400

    now = datetime.now()

    # Get number of pending assignments for each expert
    all_experts_assignments = dict(db.session.query(
        ExpertAssignment.expert_id, func.count(ExpertAssignment.request_id)
    ).filter(ExpertAssignment.status == 1).group_by(ExpertAssignment.expert_id).all())

    assignments_made = []
    for request_id in request_ids:
        auth_request = db.session.query(AuthenticationRequest).filter_by(request_id=request_id).first()
        if not auth_request or auth_request.status != 1 or ExpertAssignment.query.filter(
                and_(ExpertAssignment.request_id == request_id, ExpertAssignment.status != 3)).first():
            continue

        eligible_experts = User.query\
            .filter(and_(
                User.role == 2,
                User.id != auth_request.requester_id,
                ~User.expert_assignments.any(ExpertAssignment.request_id == request_id)
            )).all()
        if not eligible_experts:
            continue

        scores = [(expert, calculate_expert_suitability(expert, auth_request, all_experts_assignments, now))
                  for expert in eligible_experts]
        max_score = max(score for _, score in scores)
        best_experts = [expert for expert, score in scores if score == max_score]
        recommended_expert = choice(best_experts)

        assignment = ExpertAssignment(request_id=request_id, expert_id=recommended_expert.id)
        db.session.add(assignment)

        message = Message(
            authentication_request_id=request_id,
            sender_id=recommended_expert.id,
            message_text='Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
            sent_at=now
        )
        db.session.add(message)

        notification_expert = Notification(
            user_id=recommended_expert.id,
            message=f'You have been assigned to authenticate {auth_request.item.title}',
            item_url=auth_request.item.url,
            item_title=auth_request.item.title,
            notification_type=4
        )
        notification_requester = Notification(
            user_id=auth_request.requester_id,
            message=f'An expert has been assigned to authenticate your item: {auth_request.item.title}',
            item_url=auth_request.item.url,
            item_title=auth_request.item.title,
            notification_type=4
        )
        db.session.add_all([notification_expert, notification_requester])

        # Update workload
        all_experts_assignments[recommended_expert.id] = all_experts_assignments.get(recommended_expert.id, 0) + 1
        assignments_made.append({'request_id': request_id, 'expert_id': recommended_expert.id})

    db.session.commit()

    # Send notifications
    for assignment in assignments_made:
        expert = db.session.get(User, assignment['expert_id'])
        auth_request = db.session.get(AuthenticationRequest, assignment['request_id'])
        
        try:
            socketio.emit('new_notification', {
                'message': f'You have been assigned to authenticate {auth_request.item.title}',
                'item_url': auth_request.item.url,
                'created_at': now.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{expert.secret_key}')
        except Exception as e:
            print(f'SocketIO Error: {e}')

        try:
            socketio.emit('new_notification', {
                'message': f'An expert has been assigned to authenticate your item: {auth_request.item.title}',
                'item_url': auth_request.item.url,
                'created_at': now.strftime('%Y-%m-%d %H:%M')
            }, room=f'user_{auth_request.requester.secret_key}')
        except Exception as e:
            print(f'SocketIO Error: {e}')

        try:
            socketio.emit('new_message', {
                'message': 'Hi, I have been assigned to authenticate this item. To expedite the process, please provide any relevant information or documentation.',
                'sender': expert.username,
                'sender_id': str(expert.id),
                'sender_role': str(2),
                'images': None,
                'sent_at': now.strftime('%H:%M - %d/%m/%Y')
            }, room=auth_request.url)
        except Exception as e:
            print(f'SocketIO Error: {e}')

        send_notification_email(expert, Notification(
            user_id=expert.id, message=f'You have been assigned to authenticate {auth_request.item.title}',
            item_url=auth_request.item.url, item_title=auth_request.item.title, notification_type=4))

        send_notification_email(auth_request.requester, Notification(
            user_id=auth_request.requester_id, message=f'An expert has been assigned to authenticate your item: {auth_request.item.title}',
            item_url=auth_request.item.url, item_title=auth_request.item.title, notification_type=4))

    return jsonify({
        'message': 'Bulk auto-assignment successful',
        'assignments': assignments_made
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
        return jsonify({'error': 'Invalid duration'}), 400

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
