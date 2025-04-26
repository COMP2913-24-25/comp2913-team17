"""Auction creation routes."""

from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from . import create_page
from .forms import CreateAuctionForm
from ..s3_utils import upload_s3
from ..models import db, Item, AuthenticationRequest, ManagerConfig, Image


@create_page.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Render the auction creation page."""
    if current_user.role != 1:
        flash('Only general users can create auctions.', 'danger')
        return redirect(url_for('home_page.index'))

    try:
        base_fee = float(
            ManagerConfig.query.filter_by(config_key='base_platform_fee').first().config_value
        )

    except (ValueError, AttributeError):
        base_fee = 1.00

    try:
        authentication_fee = float(
            ManagerConfig.query.filter_by(config_key='authenticated_platform_fee').first().config_value
        )
    except (ValueError, AttributeError):
        authentication_fee = 5.00

    form = CreateAuctionForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category_id = form.category_id.data
        end = form.auction_end.data
        min_price = form.minimum_price.data
        images = form.images.data

        item = Item(
            seller_id=current_user.id,
            title=title,
            description=description,
            category_id=category_id,
            auction_start=datetime.now(),
            auction_end=end,
            minimum_price=min_price,
        )
        db.session.add(item)
        db.session.flush()

        # checks that the user has uploaded an image and skips db entry if not
        for i, image in enumerate(images):
            if image.filename == '':
                if i == 0:
                    flash('No images uploaded. Please upload at least one image.', 'danger')
                    return redirect(url_for('create_page.index'))
                continue
            filename = secure_filename(image.filename)
            image_filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
            image_url = upload_s3(image, image_filename, folder='auction_items')

            if image_url:
                img = Image(item_id=item.item_id, url=image_url)
                db.session.add(img)

        db.session.commit()

        if form.authenticate_item.data:
            request = AuthenticationRequest(
                item_id=item.item_id,
                requester_id=current_user.id
            )
            db.session.add(request)

        db.session.commit()

        flash('Auction created successfully!', 'success')
        return redirect(url_for('item_page.index', url=item.url))

    return render_template('create.html', form=form, base_fee=base_fee, authentication_fee=authentication_fee)
