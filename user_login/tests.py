from django.test import TestCase
from stock_order.models import StockOrder
from user_login.models import new_person, UserLogin
from django.contrib.auth.models import User


class PersonTestCase(TestCase):
    def setUp(self):
        person = new_person({'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
                             'passwordRetype': 'test123', 'email': 'test@test.nl'})

        StockOrder.objects.create(owner=person)

    def test_new_person(self):
        "test: person is created"
        user = User.objects.get(username='testPerson1')
        user_login = UserLogin.objects.get(user=user)
        person1 = user_login.person

        self.assertEquals(person1.user_last_name, 'Surname1')
        self.assertEquals(person1.user_first_name, 'Name1')
        self.assertEquals(person1.user_email_address, 'test@test.nl')

        # test case: username must be unique
        # test case: e-mail must be unique
        # passwordRetype and password do not match
