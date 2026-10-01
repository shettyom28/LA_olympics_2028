"""
Simple Django consumer for general purpose REDIS message queues.

Intended for basic queue-based communication with microservices.

Use services.pub:redis_publish() to send messages to the queues.
Register message handlers in services_sub:HANDLERS

This uses plain REDIS for demonstration simplicity. There are no advanced
queue handling features like Dead-Letter-Queues, Fan-Out, RPC,
Message persistence etc. For those, you would need a better Message Broker
or Enterprise Service Bus such as NATS, Kafka, AMQP (RabbitMQ).
"""

import json
import logging
import time

import redis
from django.conf import settings
from django.core.management.base import BaseCommand
from opentelemetry import trace
from opentelemetry.propagate import extract as otel_extract_trace_ctx

from myapp.service_sub import HANDLERS

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class Command(BaseCommand):
    help = 'Consume messages from Redis work queues'

    def handle(self, *args, **options):
        redis_url = getattr(settings, 'REDIS_URL')

        queues = list(HANDLERS)
        self.stdout.write(f'redis_subscriber: consuming {queues}')

        while True:
            try:
                redis_client = redis.from_url(redis_url)
                logger.info(f'Listening on Redis queues {queues}')
                while True:
                    queue, raw = redis_client.brpop(queues, timeout=0)
                    queue = queue.decode() if isinstance(queue, bytes) else queue
                    try:
                        data = json.loads(raw)
                        logger.info(f'Redis: received from {queue}: {data}')
                        otel_ctx = otel_extract_trace_ctx(data)
                        with tracer.start_as_current_span(f"redis_consume:{queue}", context=otel_ctx, kind=trace.SpanKind.CONSUMER):
                            HANDLERS[queue](data)
                    except Exception:
                        logger.exception(f'Error handling message on {queue}')
            except Exception:
                logger.exception(f'Redis connection error, retrying...')
                time.sleep(10)
