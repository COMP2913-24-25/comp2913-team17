from flask import current_app
from flask_mail import Mail, Message
import logging

logger = logging.getLogger(__name__)

def send_notification_email(user, notification):
    """Send an email notification to the user.
    
    Args:
        user: The user to send the email to
        notification: The notification object containing message details
    """
    try:
        mail = Mail(current_app)
        
        # Determine subject based on notification type
        subject = "Auction Notification"
        
        # Customize subject based on notification type
        # 1 = Outbid, 2 = Winner, 3 = Loser
        if notification.notification_type == 1:
            subject = f"You've been outbid on {notification.item_title}"
        elif notification.notification_type == 2:
            subject = f"Congratulations! You won the auction for {notification.item_title}"
        elif notification.notification_type == 3:
            subject = f"Auction for {notification.item_title} has ended"
        elif notification.notification_type == 4:
            subject = f"Update on authentication request for {notification.item_title}"
        
        # Build email body
        body = f"{notification.message}\n\n"
        if notification.item_url:
            body += f"View item: {current_app.config.get('BASE_URL', '127.0.0.1:5000')}/item/{notification.item_url}\n\n"
        body += "Thank you for using Vintage Vault!"
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            body=body
        )
        mail.send(msg)
        logger.info(f"Email notification sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")