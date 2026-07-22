"""
WSGI config for Expense Tracker project.
Run `python manage.py runserver` to start the development server at http://127.0.0.1:8000/
This is your expense tracker website with signup/login and dashboard!
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
