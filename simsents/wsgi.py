"""
WSGI config for simsents project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, site, sys

os.environ["DJANGO_SETTINGS_MODULE"] = "simsents.settings"

from  django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

