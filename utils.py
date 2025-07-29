from flask_mail import Message
from app import mail, app

def send_email(subject, recipients, html_body):
    with app.app_context():
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
