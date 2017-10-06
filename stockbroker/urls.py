"""careweb_stock_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.cache import cache_page

import home.views
import user_login.views

urlpatterns = [
    # url('^', include('django.contrib.auth.urls')),
    url(r'^$', home.views.index, name='index'),
    url(r'^home/$', home.views.index, name='index'),
    url(r'^orders/$', user_login.views.get_orders_view, name='orders'),
    url(r'^catalog/$', user_login.views.get_catalog_view, name='catalog'),
    url(r'^user/$', user_login.views.user_view, name='user'),
    url(r'^login/$', user_login.views.index, name='login'),
    url(r'^logout/$', user_login.views.logout_view, name='logout'),
    url(r'^order/$', user_login.views.new_order_view, name='new_order'),
    url(r'^person/$', user_login.views.new_person_view, name='new_person'),
    url(r'^create_login/$', user_login.views.new_login_view, name='new_login'),
    url(r'^change_credentials/$', user_login.views.change_credentials_view, name='change_credentials'),
    url(r'^terms/$', user_login.views.terms_view, name='terms'),
    url(r'^register/$', user_login.views.register_view, name='register'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test_transactions/', user_login.views.test_transactions, name='test_transactions'),
    url(r'^export_mailing_list/$', user_login.views.export_mailing_list, name='export_mailing_list'),
    url(r'^export_register/$', user_login.views.export_stock_register, name='export_register'),
    url(r'^export_transactions/$', user_login.views.export_transactions, name='export_transactions'),
    url(r'^send_test_email/$', user_login.views.send_test_email, name='send_test_email'),
    url('^.*/$', home.views.index, name='home'),
]
