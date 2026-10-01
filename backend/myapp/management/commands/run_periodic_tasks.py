import logging
import time

from django.core.management.base import BaseCommand

from myapp.tasks import task_scheduler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run periodic tasks in a loop'

    def handle(self, *args, **options):
        self.stdout.write('Starting periodic task loop')
        while True:
            try:
                task_scheduler.run_pending()
            except Exception:
                logger.exception('Error running periodic tasks')
            time.sleep(10)
