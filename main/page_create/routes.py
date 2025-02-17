"""Auction creation routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from . import create_page
from .forms import CreateAuctionForm
from ..models import db, Item

@create_page.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Render the auction creation page."""
    form = CreateAuctionForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        start = form.auction_start.data
        end = form.auction_end.data
        min_price = form.minimum_price.data
        image = form.image.data

        image_filename = None
        if image:
            filename = secure_filename(image.filename)
            image_filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'

        item = Item(
            seller_id = current_user.id,
            title=title,
            description=description,
            auction_start=start,
            auction_end=end,
            minimum_price=min_price,
            image=image_filename
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Auction created successfully!', 'success')
        return redirect(url_for('item_page.index', url=item.url))

    return render_template('create.html', form=form)
