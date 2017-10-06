import boto.ses
from django.conf import settings
from email_conversation.models import EmailMessage
from email_conversation import email_template_manager as templates


def send_email(email):
    email_list = tuple(email.to_emails)

    if not settings.DEBUG:
        conn = boto.ses.connect_to_region('us-west-2', aws_access_key_id='AKIAJKOKQOIBGLM5OVXQ',
                                          aws_secret_access_key='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')
        conn.send_email(email.from_email, email.subject, str(email.message), list(email_list))
        return

    print (u"***\nEMAIL SEND: \nfrom: " + unicode(email.from_email) + u"\nto: " + unicode(
        email.to_emails) + u"\nsubjet: " + unicode(email.subject) + u"\ncontent:\n" + unicode(
        email.message) + u"\nsent_date: " + unicode(email.sent_date) + u"\nemail_user: " + unicode(
        email.email_user) + u"\n***")


def send_account_change_email(date_time, user_name, email_address):
    try:
        content = templates.get_change_account_settings_template(date_time)
        send_email(EmailMessage(to_emails=[email_address], subject="Account change " + user_name, message=content))
    except:  # silent fail
        pass


def send_order_placed_email(date_time, user_name, email_address):
    try:
        content = "Beste,\n\n\nOp " + date_time.strftime("%Y-%m-%d %H:%M") + " is er een wijziging doorgevoer\
d op uw Careweb-certificaten-account.\n\nHerkent u deze activiteit niet, neem dan direct contact op met certificaten@c\
areweb.nl.\n\n\nMet vriendelijke groet,\n\nTeam Careweb certificaten"
        email = EmailMessage(from_email="info@careweb-certificaten.nl", to_emails=[email_address],
                             subject="Account change " + user_name, message=content)
        send_email(email)
    except:  # silent fail
        pass
