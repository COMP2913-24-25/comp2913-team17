from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required

from main.models import ExpertAvailability, User
from . import manager_page

@manager_page.route('/expert_availability')
@login_required
def expert_availability():
    # Only allow managers (e.g. role == 3)
    if current_user.role != 3:
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    today = date.today()
    # Define daily time slots (e.g., every 30 minutes)
    time_slots = []
    start_hour = 8
    end_hour = 20
    slot_interval = 30  # minutes
    current = datetime(today.year, today.month, today.day, start_hour)
    while current.hour < end_hour:
        time_slots.append(current.time())
        current += timedelta(minutes=slot_interval)
    
    # Get all experts (role==2)
    experts = User.query.filter_by(role=2).all()
    
    # For each expert, compute today’s availability for the daily grid
    # and also create a dictionary for the weekly grid.
    daily_availability = {}  # {expert_id: availability for today}
    weekly_availability = {}  # {expert_id: {day: available_bool}}

    # For simplicity, assume each expert has one ExpertAvailability record per day.
    # In practice, you might need to adjust the logic if an expert can have multiple availabilities per day.
    for expert in experts:
        # Daily view: Get expert's availability record for today
        record = ExpertAvailability.query.filter_by(expert_id=expert.id, day=today).first()
        daily_availability[expert.id] = record
        
        # Weekly view: For the next 7 days (including today)
        weekly_availability[expert.id] = {}
        for d in (today + timedelta(days=i) for i in range(7)):
            rec = ExpertAvailability.query.filter_by(expert_id=expert.id, day=d).first()
            # We mark them available if there is a record and status is True
            weekly_availability[expert.id][d] = rec.status if rec else False

    return render_template('manager_expert_availability.html',
                        today=today,
                        time_slots=time_slots,
                        experts=experts,
                        daily_availability=daily_availability,
                        weekly_availability=weekly_availability,
                        current_time=datetime.now().time(),
                        timedelta=timedelta)
