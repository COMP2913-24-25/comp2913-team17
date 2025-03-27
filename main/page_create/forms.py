"""Contains the form input fields for creating auctions."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, DecimalField, SubmitField, BooleanField, SelectField
from wtforms.fields import DateTimeLocalField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from datetime import datetime, timedelta
from ..models import ManagerConfig, Category


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

    category_id = SelectField('Category', coerce=int, validators=[DataRequired(
        message="Please select a category"
    )])

    auction_end = DateTimeLocalField(
        'Auction End Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M',
        default=lambda: datetime.now() + timedelta(hours=1)  # Default to 1 hour from now
    )

    minimum_price = DecimalField(
        'Minimum Price (£)',
        validators=[
            NumberRange(min=0.00, max=999998.00, message='Minimum price must be between £0.00 and £999,998.00')
        ],
        places=2,
        default=0.00
    )

    image = FileField('Image (optional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], '.jpg, .jpeg, or .png images only'),
        FileSize(max_size=1024 * 1024, message='Image must be 1MB or less')
    ])

    images = MultipleFileField(
    'Upload Images',
    validators=[Optional(), Length(max=5, message='You can upload up to 5 images only.')]
    )

    authenticate_item = BooleanField("Authenticate Item", default=False)

    submit = SubmitField('Create Auction')

    def __init__(self, *args, **kwargs):
        super(CreateAuctionForm, self).__init__(*args, **kwargs)

        # Get all categories and order by name
        categories = Category.query.order_by(Category.name).all()
        
        # Set the choices for the category select field
        self.category_id.choices = [
            (c.id, c.name) for c in categories
        ]
        
        # Store descriptions to use in the template
        self.category_descriptions = {
            c.id: c.description for c in categories if c.description
        }

    def validate_auction_end(self, field):
        try:
            days = ManagerConfig.query.filter_by(config_key='max_auction_duration').first()
            maximum_duration = timedelta(days=int(days.config_value))
        except:
            maximum_duration = timedelta(days=5)

        minimum_duration = timedelta(hours=1)
        req_duration = self.auction_end.data - datetime.now()

        if self.auction_end.data <= datetime.now():
            raise ValidationError("Auction end must occur after auction start time.")
        elif req_duration > maximum_duration:
            raise ValidationError(f"Auction duration cannot be longer than {maximum_duration.days} days.")
        elif req_duration < minimum_duration:
            raise ValidationError("Auctions must last for at least 1 hour.")
