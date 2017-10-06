__author__ = 'laurens'

import random
import string


def random_str():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(99))


def get_person_name_string(person):
    first_name = person.user_first_name
    last_name = person.user_last_name
    infix = person.user_infix

    name_string = ""

    if first_name:
        name_string += first_name.strip() + " "
    if infix:
        name_string += infix.strip() + " "
    if last_name:
        name_string += last_name.strip() + " "

    return name_string.strip()
