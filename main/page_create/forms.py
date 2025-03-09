"""Contains the form input fields for creating auctions."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, BooleanField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime


class CreateAuctionForm(FlaskForm):
    """Form for creating a new auction item."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=256, message='Title must be 256 characters or less')
    ])

    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters')
    ])

    auction_start = DateTimeLocalField(
        'Auction Start Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M',
        default=datetime.now()
    )

    auction_end = DateTimeLocalField(
        'Auction End Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M'
    )

    minimum_price = DecimalField(
        'Minimum Price (£)',
        validators=[
            NumberRange(min=0.00, message='Minimum price cannot be negative')
        ],
        places=2,
        default=0.00
    )

    image = FileField('Image (optional)', validators=[
        FileAllowed(['jpg', 'png'], '.jpg or .png images only'),
        FileSize(max_size=1024 * 1024, message='Image must be 1MB or less')
    ])

    authenticate_item = BooleanField("Authenticate Item", default=False)

    submit = SubmitField('Create Auction')
