from __future__ import absolute_import, unicode_literals
import logging
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BaylorGrants.settings")
app = Celery("BaylorGrants")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

app.conf.beat_schedule = {
    "deactivate-expired-grants": {
        "task": "grants_management.tasks.deactivate_expired_grants",
        "schedule": crontab(minute=0, hour=0),
    },
    "close-dead-grants": {
        "task": "grants_management.tasks.close_dead_grants",
        "schedule": crontab(minute=0, hour=0),
    },

    "generate-monthly-financial-report": {
        "task": "grants_management.tasks.generate_monthly_financial_report",
        "schedule": crontab(0, 0, day_of_month='1'),
    },
    "send-report-reminders": {
        'task' : "grants_management.tasks.send_report_reminders",
        'schedule': crontab(minute=0, hour=9),
    },
    "send-disbursement-reminders": {
        'task' : "grants_management.tasks.send_disbursement_reminders",
        'schedule' : crontab(minute=0, hour=0),
    },
}
