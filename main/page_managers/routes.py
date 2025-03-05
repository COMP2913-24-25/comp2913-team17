from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from . import manager_page

@manager_page.route('/expert_availability')
@login_required
def expert_availability():
    # Only allow users with the expert role
    if current_user.role != 3:
        flash("You are not authorised to access this page.", "error")
        return redirect(url_for("index"))
    

    return render_template('manager_expert_availability.html')
