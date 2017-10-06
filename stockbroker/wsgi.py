"""
WSGI config for careweb_stock_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

# import os

#
# from django.core.wsgi import get_wsgi_application
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockbroker.settings")
#
# application = get_wsgi_application()

import os
import sys
sys.path.append('installdir/apps/django/django_projects/PROJECT')
os.environ.setdefault("PYTHON_EGG_CACHE", "installdir/apps/django/django_projects/PROJECT/egg_cache")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PROJECT.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
