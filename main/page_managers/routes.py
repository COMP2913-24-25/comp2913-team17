from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models import User, ExpertAvailability
from . import manager_page 

@manager_page.route('/expert_availability')
@login_required
def expert_availability():
    # Only allow managers (role 3)
    if current_user.role != 3:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for("index"))
    
    today = date.today()
    
    # Build daily time slots (every hour from 08:00 to 20:00)
    time_slots = []
    slot_interval = 60  # minutes
    current_slot_dt = datetime(today.year, today.month, today.day, 8, 0)
    end_time_dt = datetime(today.year, today.month, today.day, 20, 0)
    while current_slot_dt < end_time_dt:
        time_slots.append(current_slot_dt.time())
        current_slot_dt += timedelta(minutes=slot_interval)
    
    # Compute the current timeslot (floor current time to the hour)
    current_time = datetime.now().time()
    current_slot = current_time.replace(minute=0, second=0, microsecond=0)
    
    # Get all experts (users with role 2)
    experts = User.query.filter_by(role=2).all()
    
    # For daily view: get each expert's availability for today
    daily_availability = {}
    for expert in experts:
        record = ExpertAvailability.query.filter_by(expert_id=expert.id, day=today).first()
        daily_availability[expert.id] = record
    
    # For weekly view: list of days from today to today+6 days
    days = [today + timedelta(days=i) for i in range(7)]
    weekly_availability = {}
    for expert in experts:
        weekly_availability[expert.id] = {}
        for d in days:
            rec = ExpertAvailability.query.filter_by(expert_id=expert.id, day=d).first()
            weekly_availability[expert.id][d] = rec.status if rec else False
    
    return render_template(
        'manager_expert_availability.html',
        today=today,
        time_slots=time_slots,
        experts=experts,
        daily_availability=daily_availability,
        days=days,
        weekly_availability=weekly_availability,
        current_time=current_time,
        current_slot=current_slot,
        timedelta=timedelta
    )

@manager_page.route('/filter-experts', methods=['GET'])
def filter_experts():
    #Filter experts based on category or expertise
    catergory_id = request.args.get('category_id'), type=int)

    query = User.query.filter_by(role=2)

    if category_id:
        query = query.join(ExpertCategory).filter(ExpertCategory_id==category_id)

    experts = query.all()

    return jsonify([{'id': e.id, 'username': e.username, 'email': e.email} for e in experts])
