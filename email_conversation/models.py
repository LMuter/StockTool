from datetime import datetime

from django.db import models

from user_login.models import Person


# Run python manage.py makemigrations to create migrations for those changes.
# Run python manage.py check to check migrations for errors.
# Run python manage.py migrate to apply those changes to the database.


class Email(models.Model):
    email_id = models.AutoField(primary_key=True)

    email_from = models.CharField(max_length=100)
    email_to = models.CharField(max_length=100)
    email_subject = models.CharField(max_length=100)
    email_content = models.TextField()

    send_date = models.DateTimeField(default=datetime.now)

    participant = models.ForeignKey(Person)

    def __unicode__(self):
        return unicode(str(self.email_id) + ' ' + unicode(self.email_to) + ' ' + unicode(self.email_subject))


email_readonly_fields = ('email_id', 'send_date', 'email_from', 'email_to', 'email_subject', 'email_content')


# todo implement
# class EmailTemplate(models.Model):
#     template_type = models.CharField(max_length=16, default="")
#     template_name = models.CharField(max_length=128, default="")
#     template_text = models.TextField(default="")
#     template_html = models.TextField(default="")


class EmailMessage:
    def __init__(self, from_email="info@careweb-certificaten.nl", to_emails=(), subject="", message="",
                 sent_date=datetime.now(), email_user=None):
        self.from_email = from_email
        self.to_emails = to_emails
        self.subject = subject
        self.message = message
        self.sent_date = sent_date
        self.email_user = email_user
