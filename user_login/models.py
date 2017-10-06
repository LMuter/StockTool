from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from user_login.constants import *
from django.db.models import Q
from user_login.user_login_errors import *
import re
from django.utils import timezone


# Run python manage.py makemigrations to create migrations for those changes.
# Run python manage.py check to check migrations for errors.
# Run python manage.py migrate to apply those changes to the database.


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    number_of_orders_max = models.PositiveSmallIntegerField(default=5)
    number_of_orders_total = models.PositiveSmallIntegerField(default=0)
    number_of_orders_accepted = models.PositiveSmallIntegerField(default=0)
    number_of_orders_pending = models.PositiveSmallIntegerField(default=0)
    number_of_orders_final = models.PositiveSmallIntegerField(default=0)
    number_of_orders_archived = models.PositiveSmallIntegerField(default=0)
    number_of_stocks = models.IntegerField(default=0)

    # todo implement
    # user_stock_register = models.CharField(max_length=1024, default="")

    """
    todo future improvements:
    - text field with stock ranges (123-125, 456-460, etc..)
    - text field with communication settings type ("no email", "email on stock changes", "email on account changes", "email als koop start") 
    """

    user_last_name = models.CharField(max_length=256, default="", blank=True)
    user_first_name = models.CharField(max_length=256, default="", blank=True)
    user_title = models.CharField(max_length=50, default="", blank=True)
    user_initials = models.CharField(max_length=256, default="", blank=True)
    user_infix = models.CharField(max_length=50, default="", blank=True)
    user_sex = models.PositiveSmallIntegerField(default=0, blank=True)
    user_country = models.CharField(max_length=256, default="", blank=True)
    user_date_of_birth = models.DateField(default=timezone.datetime(year=1900, month=1, day=1))
    user_date_of_death = models.DateField(default=timezone.datetime(year=1900, month=1, day=1))

    user_infix_of_birth = models.CharField(max_length=50, default="", blank=True)
    user_last_name_of_birth = models.CharField(max_length=256, default="", blank=True)
    user_city_of_birth = models.CharField(max_length=256, default="", blank=True)
    user_country_of_birth = models.CharField(max_length=256, default="", blank=True)

    user_street_name = models.CharField(max_length=256, default="", blank=True)
    user_house_number = models.CharField(max_length=256, default="", blank=True)
    user_house_number_addition = models.CharField(max_length=256, default="", blank=True)
    user_postal_code = models.CharField(max_length=256, default="", blank=True)
    user_residence = models.CharField(max_length=256, default="", blank=True)
    user_telephone = models.CharField(max_length=50, default="", blank=True)
    user_email_address = models.CharField(max_length=256, default="", blank=True)
    user_mobile_telephone_number = models.CharField(max_length=256, default="", blank=True)

    user_nationality = models.CharField(max_length=256, default="", blank=True)
    user_bsn_number = models.CharField(max_length=50, default="", blank=True)
    user_civil_state = models.CharField(max_length=50, default="", blank=True)
    user_card_number = models.CharField(max_length=50, default="", blank=True)

    user_type = models.CharField(max_length=2, choices=USER_TYPES, default=THIRD_PARTY)

    # todo implement
    # user_communication_type = models.CharField(max_length=2, choices=USER_COMMUNICATION_TYPES, default=NO_EMAIL)

    def get_full_name(self):
        full_name = unicode(self.user_title) + " " + unicode(self.user_initials) + " "
        if self.user_first_name:
            full_name += "(" + unicode(self.user_first_name) + ") "
        return unicode(full_name + unicode(self.user_infix) + " " + unicode(self.user_last_name))

    def __unicode__(self):
        return unicode(self.user_title) + " " + unicode(self.user_initials) + " " + unicode(
            self.user_first_name) + " " + unicode(self.user_infix) + " " + unicode(self.user_last_name)


class UserLogin(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    person = models.ForeignKey(Person)


username_pattern = re.compile('(^[a-zA-Z0-9@.+\-_]+$)')
password_pattern = re.compile('(^[a-zA-Z0-9!@#$%^&*()_+-=,.<>/\\?\[\]{}|;:]+$)')
password_requirement = re.compile('(^(?=.*[A-Z])(?=.*\d).{8,}$)')
email_pattern = re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')


# check if user / e-mail exists
# check password
# check email
# at error, return message
def new_person(info_dict):
    username = info_dict.get('username')
    name = info_dict.get('name')
    surname = info_dict.get('surname')
    email = info_dict.get('email')
    password = info_dict.get('password')
    password_retype = info_dict.get('passwordRetype')

    if not username_pattern.match(username):
        raise UsernameException("Invalid username only characters a-z, A-Z, 0-9 and @.+-_ are allowed.")

    if password != password_retype:
        raise PasswordsException('Password does not match confirmation password.')

    if not password_pattern.match(password):
        raise PasswordsException('Password contains non-supported character.')

    try:
        User.objects.get(Q(email=email) | Q(username=username))
        raise DuplicatePersonException("Username or e-mail already in use.")

    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password)

        user.last_name = surname
        user.first_name = name
        user.save()

    try:
        Person.objects.get(user_last_name=surname, user_first_name=name, user_email_address=email)
        raise DuplicatePersonException("Person already exists.")

    except Person.DoesNotExist:
        person = Person.objects.create(user_last_name=surname, user_first_name=name, user_email_address=email)

    UserLogin.objects.create(user=user, person=person)

    return person


def new_person_no_login(info_dict):
    name = info_dict.get('name')
    surname = info_dict.get('surname')
    title = info_dict.get('title')
    infix = info_dict.get('infix')
    user_type = info_dict.get('user_type')
    email = info_dict.get('email')

    try:
        User.objects.get(email=email)
        raise DuplicatePersonException("E-mail already in use.")
    except (Person.DoesNotExist, User.DoesNotExist):
        pass

    try:
        Person.objects.get(user_email_address=email)
        raise DuplicatePersonException("E-mail already in use.")
    except (Person.DoesNotExist, User.DoesNotExist):
        person = Person.objects.create(user_title=title, user_last_name=surname, user_infix=infix,
                                       user_first_name=name, user_type=user_type, user_email_address=email)

    return person


def new_person_login(info_dict):
    person_id = info_dict.get('person')
    username = info_dict.get('username')
    password = info_dict.get('password')
    password_retype = info_dict.get('passwordRetype')

    if not username_pattern.match(username):
        raise UsernameException("Invalid username only characters a-z, A-Z, 0-9 and @.+-_ are allowed.")

    if password != password_retype:
        raise PasswordsException('Password does not match confirmation password.')

    if not password_pattern.match(password):
        raise PasswordsException(
            'Password contains a non-supported character. You can use: !@#$%^&*()_+-=,.<>/\\?\[\]{}|;:)')

    try:
        person = Person.objects.get(person_id=person_id)
    except (Person.DoesNotExist, ValueError):
        raise PersonException("Person does not exist.")

    try:
        User.objects.get(username=username)
        raise DuplicatePersonException("Username already in use.")

    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=person.user_email_address, password=password)

        user.last_name = person.user_last_name
        user.first_name = person.user_first_name
        user.save()

    return UserLogin.objects.create(user=user, person=person)


def change_password(info_dict):
    username = info_dict.get('username')
    password_old = info_dict.get('password')
    password_new = info_dict.get('passwordNew', '')
    password_retype = info_dict.get('passwordRetype', '')

    if password_new != password_retype:
        raise PasswordsException('Password does not match confirmation password.')

    if password_new == password_old:
        raise PasswordsException('New password should be different from old password.')

    if len(str(password_new)) < 8 or len(str(password_retype)) < 8:
        raise PasswordsException('Password should be at least 8 characters long.')

    if not password_requirement.match(password_new):
        raise PasswordsException('Password should contain at least one digit and one uppercase letter.')

    if not password_pattern.match(password_new):
        raise PasswordsException(
            'New password contains a non-supported character. You can use: !@#$%^&*()_+-=,.<>/\\?\[\]{}|;:)')

    user_object = authenticate(username=username, password=password_old)

    if not user_object:
        raise PasswordsException('Login failed, username or password is incorrect.')

    user_object.set_password(password_new)
    user_object.save()

    return user_object


def change_credentials(info_dict):
    username = info_dict.get('username')
    password = info_dict.get('password')
    person_id = info_dict.get('person')

    user_object = authenticate(username=username, password=password)

    try:
        person = Person.objects.get(person_id=person_id)
    except (Person.DoesNotExist, ValueError):
        raise PersonException("Person does not exist.")

    if info_dict.get('user_email_address'):
        if not email_pattern.match(info_dict.get('user_email_address')):
            raise EmailException('Invalid email pattern.')
        user_object.email = info_dict.get('user_email_address')
        user_object.save()

    if user_object and person:
        attribute_list = info_dict.keys()

        for att in attribute_list:
            if hasattr(person, att):
                setattr(person, att, info_dict.get(att))

    person.save()

    return person
