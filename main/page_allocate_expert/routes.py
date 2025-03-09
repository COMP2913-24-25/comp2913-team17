from flask import Blueprint, render_template, request, redirect, url_for
from main.models import db, Expert, ItemAssignment, Item
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

# Define Flask-WTF form
class ExpertAssignmentForm(FlaskForm):
    item_id = SelectField("Item", coerce=int)
    expert_id = SelectField("Expert", coerce=int)
    submit = SubmitField("Assign Expert")

# Fix: Match the blueprint name from __init__.py
allocate_expert_bp = Blueprint("allocate_expert_bp", __name__, template_folder="templates")

@allocate_expert_bp.route("/", methods=["GET", "POST"])  
def allocate_expert():
    """Displays the expert assignment page and handles assignments"""
    experts = Expert.query.all()
    items = Item.query.all()
    assignments = ItemAssignment.query.all()

    # Initialize the form
    form = ExpertAssignmentForm()

    # Populate dropdown choices
    form.item_id.choices = [(item.item_id, item.title) for item in items]
    form.expert_id.choices = [(expert.id, expert.name) for expert in experts]

    if request.method == "POST" and form.validate_on_submit():
        assignment = ItemAssignment(
            item_id=form.item_id.data,
            expert_id=form.expert_id.data,
            assigned_at=datetime.now()
        )
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for("allocate_expert_bp.allocate_expert"))  

    return render_template("allocate_expert.html", form=form, experts=experts, assignments=assignments, items=items)
