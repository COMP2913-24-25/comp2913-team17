"""Auction viewing routes."""

from flask import render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import authenticate_item_page
from ..models import db, Item, AuthenticationRequest

@authenticate_item_page.route('/<url>')
@login_required
def index(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first_or_404()
    item = Item.query.filter_by(item_id=authentication.item_id).first()

    # Check user is allowed to view this page
    expert = authentication.expert_assignments[-1] if authentication.expert_assignments else None
    is_creator = authentication.requester_id == current_user.id
    is_expert = expert and expert.expert_id == current_user.id and expert.status != 3
    is_admin = current_user.role == 3

    if not is_creator and not is_expert and not is_admin:
        flash('You are not authorised to view this page.', 'danger')
        return redirect(url_for('home_page.index'))

    return render_template('authenticate_item.html', item=item, authentication=authentication.status, is_creator=is_creator, is_expert=is_expert, is_admin=is_admin)


@authenticate_item_page.route('/<url>/api/accept', methods=['POST'])
@login_required
def accept(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404
    
    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400
    
    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403
    
    authentication.status = 2
    authentication.expert_assignments[-1].status = 2
    db.session.commit()

    return jsonify({'success': 'Authentication request accepted.'})


@authenticate_item_page.route('/<url>/api/decline', methods=['POST'])
@login_required
def reject(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404
    
    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400
    
    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403
    
    authentication.status = 3
    authentication.expert_assignments[-1].status = 2
    db.session.commit()

    return jsonify({'success': 'Authentication request rejected.'})


@authenticate_item_page.route('/<url>/api/reassign', methods=['POST'])
@login_required
def reassign(url):
    authentication = AuthenticationRequest.query.filter_by(url=url).first()
    if not authentication:
        return jsonify({'error': 'Authentication request not found.'}), 404
    
    if authentication.status != 1:
        return jsonify({'error': 'Authentication request is not pending.'}), 400
    
    if authentication.expert_assignments and (authentication.expert_assignments[-1].expert_id != current_user.id or authentication.expert_assignments[-1].status != 1):
        return jsonify({'error': 'You are not assigned to this authentication request.'}), 403
    
    authentication.expert_assignments[-1].status = 3
    db.session.commit()

    return jsonify({'success': 'Authentication request reassignment scheduled.'})