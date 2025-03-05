"""Contains the form input fields for creating auctions."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, BooleanField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime, timedelta


class CreateAuctionForm(FlaskForm):
    """Form for creating a new auction item."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=10, max=256, message='Title must be 256 characters or less')
    ])

    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required"),
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

    def validate_auction_start(self, field):
        schedule_limit = timedelta(days=5)

        if field.data <= datetime.now():
            raise ValidationError("Auction start time must be in the future.")
        elif field.data - datetime.now() > schedule_limit:
            raise ValidationError("Auctions can only be scheduled up to 5 days in advance.")

    def validate_auction_end(self, field):
        maximum_duration = timedelta(days=5)
        minimum_duration = timedelta(hours=1)
        req_duration = self.auction_end.data - self.auction_start.data

        if self.auction_end.data <= self.auction_start.data:
            raise ValidationError("Auction end must occur after auction start time.")
        elif req_duration > maximum_duration:
            raise ValidationError("Auction duration cannot be longer than 5 days.")
        elif req_duration < minimum_duration:
            raise ValidationError("Auctions must last for atleast 1 hour.")
