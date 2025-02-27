from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..models import ExpertAvailability, db
from . import expert_page

@expert_page.route('/availability', methods=['GET', 'POST'])
@login_required
def update_availability():
    # Only allow users with the expert role (assuming role 2 is expert)
    if current_user.role != 2:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for("index"))
    
    today = date.today()
    # Compute week_start as the most recent Sunday:
    week_start = today - timedelta(days=(today.weekday() + 1) % 7)

    if request.method == 'POST':
        for i in range(7):
            current_day = week_start + timedelta(days=i)
            start_time_str = request.form.get(f'day_{i}_start')
            end_time_str = request.form.get(f'day_{i}_end')
            status = request.form.get(f'day_{i}_status') == 'available'

            if start_time_str and end_time_str:
                try:
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()
                except ValueError:
                    flash(f"Invalid time format for {current_day}.", "error")
                    continue

                # Validate that times are within 08:00 and 20:00
                if not (start_time >= datetime.strptime("08:00", "%H:%M").time() and
                        end_time <= datetime.strptime("20:00", "%H:%M").time()):
                    flash(f"Availability for {current_day} must be between 08:00 and 20:00.", "error")
                    continue

                # Retrieve or create the availability entry for the day
                availability = ExpertAvailability.query.filter_by(
                    expert_id=current_user.id, day=current_day
                ).first()
                if not availability:
                    availability = ExpertAvailability(
                        expert_id=current_user.id,
                        day=current_day,
                        start_time=start_time,
                        end_time=end_time,
                        status=status
                    )
                    db.session.add(availability)
                else:
                    availability.start_time = start_time
                    availability.end_time = end_time
                    availability.status = status
        db.session.commit()
        flash("Availability updated successfully.", "success")
        return redirect(url_for('update_availability'))
    
    # For GET requests, load current week's availability
    week_availabilities = {
        (week_start + timedelta(days=i)): None for i in range(7)
    }
    availabilities = ExpertAvailability.query.filter_by(
        expert_id=current_user.id
    ).filter(
        ExpertAvailability.day.between(week_start, week_start + timedelta(days=6))
    ).all()
    for avail in availabilities:
        week_availabilities[avail.day] = avail

    # Pass timedelta so the template can use it
    return render_template('update_expert.html', 
                           week_start=week_start, 
                           week_availabilities=week_availabilities,
                           timedelta=timedelta)
