from django.utils.timezone import now, localtime
from user_login.models import UserLogin

def get_change_account_settings_template(date_time_change):
    return apply_template(CHANGE_ACCOUNT_SETTINGS, date_time_change=date_time_change)


def get_send_order_template():
    return apply_template(SEND_ORDER)


CHANGE_ACCOUNT_SETTINGS = """Beste,

Op {date_time_change:%Y-%m-%d %H:%M} is er een wijziging doorgevoerd op uw Careweb-certificaten-account.

Herkent u deze activiteit niet, neem dan direct contact op met certificaten@careweb.nl.


Met vriendelijke groet,

Team Careweb certificaten"""

SEND_ORDER = """Beste{name_space},

"""


def apply_template(template, **kwargs):
    data_dict = merge_dicts(BASIC_VARS, get_variable_vars(request=kwargs.get("request")), kwargs)
    return template.format(**data_dict)


def get_variable_vars(request=None):
    var_dict = {"now": localtime(now()), "login_name_space": ""}
    if request:
        person_id = request.POST.get("person")
        user_login = UserLogin.objects.get(user=request.user)
        person_login = user_login.person

        var_dict["name_space"] = ""

    # todo find usefull vars in request
    # see https://docs.djangoproject.com/en/1.11/ref/request-response/
    # pprint(vars(request))
    # print (request.POST)

    return {"now": localtime(now()), "name_space": ""}


BASIC_VARS = {
    "default_date": "%Y-%m-%d",
    "default_time": "%H:%M",
}

# todo more default usages: see https://pyformat.info/#named_placeholders
"""
example usage:

>>> apply_template('current time: {now}.')
'current time: 2017-10-04 18:27:09.060604.'
>>> apply_template('current time: {now:{default_date}}.')
'current time: 2017-10-04.'
>>> apply_template('current time: {now:%Y-%m-%d %H:%M}.')
'current time: 2017-10-04 18:27.'
>>> apply_template('time in {c}: {now:%H:%M:%S}.', c="NL")
'time in NL: 18:31:42.'
>>> apply_template('person: {person.user_first_name}')
'person: laurens'
"""


def merge_dicts(*args):
    """Given n dicts, merge them into a new dict as a shallow copy."""
    if len(args) < 1:
        raise TypeError("merge_dicts(*args) takes 1 or more arguments (0 given)")

    z = args[0].copy()
    for d in args[1:]:
        z.update(d)

    return z
