"""
Functions to publish messages to Redis message-queues
"""
from __future__ import annotations

import json
import logging

import redis
from django.conf import settings
from opentelemetry.propagate import inject as otel_inject_trace_ctx

logger = logging.getLogger(__name__)


def redis_publish(queue: str, payload: bytes) -> None:
    """Push a message onto a Redis list (work queue).

    No-op when REDIS_URL is not configured.
    """
    redis_url = getattr(settings, 'REDIS_URL', None)
    if not redis_url:
        return
    try:
        redis_client = redis.from_url(redis_url)
        redis_client.lpush(queue, payload)
        logger.info(f'Redis: published to {queue}: {payload.decode()}')
    except Exception:
        logger.exception(f'Failed to publish to Redis queue {queue}')


def publish_example_message(message_id: int, text: str, username: str, history: list | None = None) -> None:
    """Publish a user message to the chatbot queue, including conversation history."""
    message = {
        'message_id': message_id,
        'text': text,
        'username': username,
        'history': history or [],
    }
    otel_inject_trace_ctx(message)
    redis_publish('example:messages', json.dumps(message).encode())
    logger.info(f'Published example message: {text}')
