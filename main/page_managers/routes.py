from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models import User, ExpertAvailability
from . import manager_page  # your manager blueprint

@manager_page.route('/expert_availability')
@login_required
def expert_availability():
    # Only allow managers (assuming role 3 is manager)
    if current_user.role != 3:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for("index"))
    
    today = date.today()
    
    # Build daily time slots (every 30 minutes from 08:00 to 20:00)
    time_slots = []
    slot_interval = 30  # minutes
    current_slot = datetime(today.year, today.month, today.day, 8, 0)
    end_time = datetime(today.year, today.month, today.day, 20, 0)
    while current_slot < end_time:
        time_slots.append(current_slot.time())
        current_slot += timedelta(minutes=slot_interval)
    
    # Get all experts (users with role 2)
    experts = User.query.filter_by(role=2).all()
    
    # For daily view: for each expert, get today’s availability record
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
            # Mark available if record exists and status is True; otherwise unavailable.
            weekly_availability[expert.id][d] = rec.status if rec else False
    
    current_time = datetime.now().time()
    
    return render_template(
        'manager_expert_availability.html',
        today=today,
        time_slots=time_slots,
        experts=experts,
        daily_availability=daily_availability,
        days=days,
        weekly_availability=weekly_availability,
        current_time=current_time,
        timedelta=timedelta
    )
