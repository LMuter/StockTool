from django.test import TestCase

from stock_register.controller import *
from stock_register.views import *
from user_login.models import *


class TestController(TestCase):
    def setUp(self):
        self.jw = new_person_no_login(
            {'name': "jw", 'surname': "Bentum", 'title': "dhr.", 'infix': "", "user_type": 'third party',
             'email': "test_jw@test.com"})

        self.jw.number_of_stocks = 123
        self.jw.save()

        self.jeroen = new_person_no_login(
            {'name': "j", 'surname': "Jansen", 'title': "dhr.", 'infix': "", "user_type": 'third party',
             'email': "test_jj@test.com"})

        self.jeroen.number_of_stocks = 10
        self.jeroen.save()

        for n in range(1, 101):
            stock = Stock(owner=self.jw, stock_ref=str(n))
            stock.save()

        for n in range(101, 201):
            stock = Stock(owner=self.jeroen, stock_ref=str(n))
            stock.save()

        for n in range(201, 251):
            stock = Stock(owner=self.jw, stock_ref=str(n))
            stock.save()

        for n in range(300, 351):
            stock = Stock(owner=self.jw, stock_ref=str(n))
            stock.save()

    def test_list_stock_register(self):

        # =================================================================
        # test: list stock register no variables, all data expected
        # =================================================================

        register_dict_exp = {self.jeroen: [[u'101', u'200']],
                             self.jw: [[u'1', u'100'], [u'201', u'250'], [u'300', u'350']]}
        register_dict_real = list_stock_register_person()

        self.assertEquals(register_dict_real, register_dict_exp)

        # =================================================================
        # test: list stock register person parameter filled in
        # =================================================================

        register_dict_exp = {self.jeroen: [[u'101', u'200']],}
        register_dict_real = list_stock_register_person(self.jeroen)

        self.assertEquals(register_dict_real, register_dict_exp)

        register_dict_exp = {self.jw: [[u'1', u'100'], [u'201', u'250'], [u'300', u'350']]}
        register_dict_real = list_stock_register_person(person=self.jw)

        self.assertEquals(register_dict_real, register_dict_exp)

        # =================================================================
        # test: list stock register person view
        # =================================================================

        stock_register_view_exp = """This document is created by: dhr.  (jw)  Bentum\r\nowner_id,owner_full_name,share_amount,share_ranges\r\n1,dhr.  (jw)  Bentum,123,"[[u\'1\', u\'100\'], [u\'201\', u\'250\'], [u\'300\', u\'350\']]"\r\n2,dhr.  (j)  Jansen,10,"[[u\'101\', u\'200\']]"\r\n"""

        # stock_register_view_exp = json.dumps(stock_register_view_exp)

        stock_register_view_real = get_stock_register_export(user_person=self.jw).getvalue()

        self.assertEquals(stock_register_view_real[63:], stock_register_view_exp)

        # =================================================================
        # test: sort persons by last name, first name
        # =================================================================

        # save extra persons
        self.aa = new_person_no_login(
            {'name': "a", 'surname': "Aa", 'title': "dhr.", 'infix': "", "user_type": 'third party',
             'email': "test_aa@test.com"})

        self.aa.number_of_stocks = 9
        self.aa.save()

        self.az = new_person_no_login(
            {'name': "z", 'surname': "Aa", 'title': "dhr.", 'infix': "", "user_type": 'third party',
             'email': "test_az@test.com"})

        self.az.number_of_stocks = 8
        self.az.save()

        self.zz = new_person_no_login(
            {'name': "a", 'surname': "Zz", 'title': "dhr.", 'infix': "", "user_type": 'third party',
             'email': "test_zz@test.com"})

        self.zz.number_of_stocks = 7
        self.zz.save()

        # save extra stocks for persons
        for n in range(351, 451):
            stock_1 = Stock(owner=self.aa, stock_ref=str(n))
            stock_2 = Stock(owner=self.az, stock_ref=str(n + 100))
            stock_3 = Stock(owner=self.zz, stock_ref=str(n + 200))

            stock_1.save()
            stock_2.save()
            stock_3.save()

        stock_register_view_exp = """This document is created by: dhr.  (jw)  Bentum\r\nowner_id,owner_full_name,share_amount,share_ranges\r\n3,dhr.  (a)  Aa,9,"[[u\'351\', u\'450\']]"\r\n4,dhr.  (z)  Aa,8,"[[u\'451\', u\'550\']]"\r\n1,dhr.  (jw)  Bentum,123,"[[u\'1\', u\'100\'], [u\'201\', u\'250\'], [u\'300\', u\'350\']]"\r\n2,dhr.  (j)  Jansen,10,"[[u\'101\', u\'200\']]"\r\n5,dhr.  (a)  Zz,7,"[[u\'551\', u\'650\']]"\r\n"""

        stock_register_view_real = get_stock_register_export(user_person=self.jw).getvalue()
        self.assertEquals(stock_register_view_real[63:], stock_register_view_exp)
