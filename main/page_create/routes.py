"""Auction creation routes."""

import boto3
from botocore.exceptions import ClientError
from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from . import create_page
from .forms import CreateAuctionForm
from ..models import db, Item


def init_s3():
    """Initialise the S3 client."""
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
    )


def upload_s3(file, filename, folder=None):
    """Upload a file to S3 and return the URL."""
    s3 = init_s3()
    bucket = current_app.config['AWS_BUCKET']

    try:
        filepath = f'{folder}/{filename}' if folder else filename

        s3.upload_fileobj(
            file,
            bucket,
            filepath,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        return f'https://{bucket}.s3.amazonaws.com/{filepath}'
    except ClientError as e:
        print(e)
        return None


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

        # If image, try to upload to S3
        image_url = None
        if image:
            filename = secure_filename(image.filename)
            image_filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
            image_url = upload_s3(image, image_filename, folder='auction_items')

            if not image_url:
                flash('Error uploading image')

        item = Item(
            seller_id=current_user.id,
            title=title,
            description=description,
            auction_start=start,
            auction_end=end,
            minimum_price=min_price,
            image=image_url
        )
        db.session.add(item)
        db.session.commit()

        flash('Auction created successfully!', 'success')
        return redirect(url_for('item_page.index', url=item.url))

    return render_template('create.html', form=form)
