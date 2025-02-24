"""Auction viewing routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import authenticate_item_page
from ..models import Item, AuthenticationRequest

@authenticate_item_page.route('/<url>')
@login_required
def index(url):
    item = Item.query.filter_by(url=url).first_or_404()

    # Check authentication status
    authentication = AuthenticationRequest.query.filter_by(item_id=item.item_id).first()
    if not authentication:
        return redirect(url_for('home_page.index'))
    
    # Check user is allowed to view this page
    expert = authentication.expert_assignments[0] if authentication.expert_assignments else None
    is_allowed = (
        authentication.requester_id == current_user.id or
        expert and expert.expert_id == current_user.id or
        current_user.role == 3
    )

    if not is_allowed:
        flash('You are not authorised to view this page.', 'danger')
        return redirect(url_for('home_page.index'))

    return render_template('authenticate_item.html', item=item, authentication=authentication.status)
