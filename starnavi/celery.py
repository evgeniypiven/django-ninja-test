"""
Celery Config
"""
# Standard library imports.
from __future__ import absolute_import, unicode_literals
import os

# Related third party imports.
from celery import Celery

# Local application/library specific imports.


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starnavi.settings')

# Create an instance of Celery and configure it using the Django settings.
app = Celery('starnavi')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# If you have tasks in a separate tasks.py file in each Django app
app.autodiscover_tasks()
