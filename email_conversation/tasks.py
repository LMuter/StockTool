from celery.utils.log import get_task_logger
from django.core.mail import send_mail

logger = get_task_logger(__name__)


def send_email_message(email):
    logger.info("Sent feedback email")
    # todo via email conversation, save message etc.
    message_send = send_mail.delay(email.subject, email.message, email.from_email, email.to_emails, fail_silently=False)

    save_sent_message(message_send)

    return message_send


def save_sent_message(message_send):
    pass
