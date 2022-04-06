from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab

from datetime import timedelta

# You can use rabbitmq instead here.
BASE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robosats.settings")

app = Celery("robosats")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL

# this allows schedule items in the Django admin.
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"


# Configure the periodic tasks
app.conf.beat_schedule = {
    "users-cleansing": {  # Cleans abandoned users at midnight
        "task": "users_cleansing",
        "schedule": crontab(hour=0, minute=0),
    },
    "give-rewards": {  # Referral rewards go from 'pending' to 'earned' at midnight
        "task": "give_rewards",
        "schedule": crontab(hour=0, minute=0),
    },
    "do-accounting": {  # Does accounting for the last day
        "task": "do_accounting",
        "schedule": crontab(hour=23, minute=55),
    },
    "cache-market-prices": {  # Cache market prices every minute
        "task": "cache_external_market_prices",
        "schedule": timedelta(seconds=60),
    },
}

app.conf.timezone = "UTC"
