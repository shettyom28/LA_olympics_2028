#!/usr/bin/env python3
"""
Example microservice.

Receives messages from a REDIS queue.
Posts a category code back to the application via the REST API.
Sends a notification to a REDIS result queue.

Environment variables:
    REDIS_URL
    API_BASE
    SERVICE_API_TOKEN
"""

import json
import logging
import os
import time
from typing import Callable

import redis
import requests
from opentelemetry import trace
from opentelemetry.propagate import extract as otel_extract_trace_ctx
from opentelemetry.propagate import inject as otel_inject_trace_ctx

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

REDIS_URL = os.environ["REDIS_URL"]
API_BASE = os.environ["API_BASE"].rstrip("/")
API_HEADERS = {"Authorization": f"Token {os.environ['SERVICE_API_TOKEN']}"}


def handle_example_message(data: dict) -> None:
    """Message queue handler for 'example:messages'.

    When a new message has been created on the server,
    respond with a simple Olympics helper code.
    """

    message_id = data["message_id"]
    text = data.get("text", "")
    username = data.get("username", "unknown")
    logger.info("Processing message %s from %s: %s", message_id, username, text)

    text_lower = text.lower()

    if "schedule" in text_lower:
        number = 101
    elif "medal" in text_lower:
        number = 202
    elif "ticket" in text_lower:
        number = 303
    else:
        number = 999

    result = {
        "random_number": number
    }

    url = f"{API_BASE}/api/v1/example-messages/{message_id}/result/"
    response = requests.post(url, json=result, headers=API_HEADERS)
    logger.info(
        "  -> Posted result random_number=%d for message %d (API %s)",
        number,
        message_id,
        response.status_code,
    )

    redis_publish(
        "example:results",
        {"message_id": message_id, "random_number": number, "status": "processed"},
    )


HANDLERS: dict[str, Callable[[dict], None]] = {
    "example:messages": handle_example_message,
}


def redis_subscribe() -> None:
    """Consume messages from Redis work queues and dispatch to handlers."""
    queues = list(HANDLERS)
    while True:
        try:
            redis_client = redis.from_url(REDIS_URL)
            logger.info("Listening on Redis queues %s ...", queues)
            while True:
                queue, raw = redis_client.brpop(queues, timeout=0)
                queue = queue.decode() if isinstance(queue, bytes) else queue
                try:
                    data = json.loads(raw)
                    logger.info("Redis: received from '%s': %s", queue, data)
                    otel_ctx = otel_extract_trace_ctx(data)
                    with tracer.start_as_current_span(
                        f"redis_consume:{queue}",
                        context=otel_ctx,
                        kind=trace.SpanKind.CONSUMER,
                    ):
                        HANDLERS[queue](data)
                except Exception:
                    logger.exception("Error handling message on %s", queue)
        except Exception:
            logger.exception("Redis connection error, retrying...")
            time.sleep(10)


def redis_publish(queue: str, data: dict) -> None:
    """Publish a message to a Redis work queue."""
    otel_inject_trace_ctx(data)
    redis.from_url(REDIS_URL).lpush(queue, json.dumps(data).encode())
    logger.info("Redis: published to %s: %s", queue, data)


def main():
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(logging.INFO)
    redis_subscribe()


if __name__ == "__main__":
    main()