"""
Application Background Tasks.

For scheduled tasks and once-off tasks invoked during HTTP/etc requests.

Simple Database-backed queue using Django 6.0's new built-in task system.
(Traditionally handled by heavy dependencies like Celery w/ Redis).

Task code is actually run by "manage.py db_worker"
"""

import logging
import schedule
from django_tasks import task

logger = logging.getLogger(__name__)


@task()
def example_task():
    """Example background task that logs a message."""
    logger.info('example_task: running background task')


# Add your scheduled tasks here
task_scheduler = schedule.Scheduler()
task_scheduler.every(60).seconds.do(example_task.enqueue)
