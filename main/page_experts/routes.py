from datetime import date, datetime, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..models import ExpertAvailability, db
from . import expert_page

@expert_page.route('/availability', methods=['GET', 'POST'])
@login_required
def update_availability():
    # Only allow users with the expert rol
    if current_user.role != 2:
        flash("You are not authorised to access this page.", "error")
        return redirect(url_for("index"))
    
    today = date.today()
    # Compute current week's start (most recent Sunday)
    current_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
    
    # Determine week_start from GET query parameter or POST hidden field.
    if request.method == 'POST':
        week_start_str = request.form.get('week_start')
    else:
        week_start_str = request.args.get('week_start')
    
    if week_start_str:
        try:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            week_start = current_week_start
    else:
        week_start = current_week_start

    if request.method == 'POST':
        for i in range(7):
            current_day = week_start + timedelta(days=i)
            start_time_str = request.form.get(f'day_{i}_start')
            end_time_str = request.form.get(f'day_{i}_end')
            status_value = request.form.get(f'day_{i}_status')
            status = True if status_value == 'available' else False

            # Retrieve the availability entry for the day if it exists
            availability = ExpertAvailability.query.filter_by(
                expert_id=current_user.id, day=current_day
            ).first()
            
            # If times are provided, update or create the record with these times and status
            if start_time_str and end_time_str:
                try:
                    start_time = datetime.strptime(start_time_str, '%H:%M').time()
                    end_time = datetime.strptime(end_time_str, '%H:%M').time()
                except ValueError:
                    flash(f"Invalid time format for {current_day}.", "error")
                    continue
                # Validate times between 08:00 and 20:00
                if not (start_time >= datetime.strptime("08:00", "%H:%M").time() and
                        end_time <= datetime.strptime("20:00", "%H:%M").time()):
                    flash(f"Availability for {current_day} must be between 08:00 and 20:00.", "error")
                    continue
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
            else:
                # If times are not provided (likely because they're disabled), update only status
                if availability:
                    availability.status = status
                else:
                    default_start = datetime.strptime("08:00", "%H:%M").time()
                    default_end = datetime.strptime("20:00", "%H:%M").time()
                    availability = ExpertAvailability(
                        expert_id=current_user.id,
                        day=current_day,
                        start_time=default_start,
                        end_time=default_end,
                        status=status
                    )
                    db.session.add(availability)
        db.session.commit()
        flash("Availability updated successfully.", "success")
        # Redirect back to the same week view
        return redirect(url_for('expert_page.update_availability', week_start=week_start.strftime('%Y-%m-%d')))
    
    # For GET: Load availability for the specified week.
    week_availabilities = {week_start + timedelta(days=i): None for i in range(7)}
    availabilities = ExpertAvailability.query.filter_by(
        expert_id=current_user.id
    ).filter(
        ExpertAvailability.day.between(week_start, week_start + timedelta(days=6))
    ).all()
    for avail in availabilities:
        week_availabilities[avail.day] = avail

    return render_template('update_expert.html',
                           week_start=week_start,
                           week_availabilities=week_availabilities,
                           timedelta=timedelta,
                           today=today,
                           current_week_start=current_week_start)
