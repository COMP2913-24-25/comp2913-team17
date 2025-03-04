from celery import Celery
from flask_mail import Message
from flask import current_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# Initialize Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True, max_retries=3)
def send_winner_email(self, recipient, item_title, bid_amount, end_date):
    """
    Send winner email notification asynchronously with retry logic
    """
    try:
        # Get Flask app context
        from . import create_app
        app = create_app()
        
        with app.app_context():
            msg = Message(
                'Congratulations! You won the auction!',
                sender=app.config['MAIL_USERNAME'],
                recipients=[recipient]
            )
            msg.body = f"""
            Congratulations! You won the auction for {item_title}!
            
            Item Details:
            - Title: {item_title}
            - Final Price: £{bid_amount}
            - End Date: {end_date}
            
            Please login to your account to complete the payment.
            """
            
            app.extensions['mail'].send(msg)
            logger.info(f"Successfully sent winner email to {recipient}")
            
    except Exception as exc:
        logger.error(f"Failed to send winner email to {recipient}: {str(exc)}")
        # Retry with exponential backoff: 2, 4, 8 seconds
        self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery.task(bind=True, max_retries=3)
def send_loser_email(self, recipient, item_title, item_url, end_date):
    """
    Send loser email notification asynchronously with retry logic
    """
    try:
        # Get Flask app context
        from . import create_app
        app = create_app()

        with app.app_context():
            msg = Message(
                'Auction Ended: Better Luck Next Time',
                sender=app.config['MAIL_USERNAME'],
                recipients=[recipient]
            )
            msg.body = f"""
            The auction for {item_title} has ended.
            
            Unfortunately, you were not the highest bidder this time.
            
            Item Details:
            - Title: {item_title}
            - End Date: {end_date}
            
            Check out other ongoing auctions on our platform!
            """

            app.extensions['mail'].send(msg)
            logger.info(f"Successfully sent loser email to {recipient}")

    except Exception as exc:
        logger.error(f"Failed to send loser email to {recipient}: {str(exc)}")
        # Retry with exponential backoff: 2, 4, 8 seconds