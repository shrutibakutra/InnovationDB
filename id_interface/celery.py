from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django setting module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'id_interface.settings')
app = Celery('id_interface',
             broker_url='redis://127.0.0.1:6379',
             )
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Using a string here means the worker will not have to
# pickle the object when using Windows
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
