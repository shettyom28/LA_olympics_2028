"""
Redis work-queue consumer handlers.
Receives messages from the REDIS queues back into the Django app.

Add entries to HANDLERS here to register new queues.

Subscriber code is actually run by "manage.py redis_subscriber"
"""
import logging
from typing import Callable

logger = logging.getLogger(__name__)


def handle_example_message(data: dict):
    """Example handler that logs received messages."""
    text = data.get('text', '')
    logger.info(f'Received example message: {text}')


HANDLERS: dict[str, Callable[[dict], None]] = {
    'example:results': handle_example_message,
}
