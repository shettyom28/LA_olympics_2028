import logging
import time
from contextvars import ContextVar

_request = ContextVar("request", default=None)

access_log = logging.getLogger("django.request")


class RequestLoggingMiddleware:
    """Log every HTTP request/response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request.set(request)   # Used by RequestContextFilter
        start = time.monotonic()
        status = 500

        try:
            response = self.get_response(request)
            status = response.status_code
        except Exception:
            username = self._username(request)
            access_log.exception(
                f"{username} {request.method} {request.get_full_path()} {status}",
                extra=self._extra(request, status, start),
            )
            raise

        username = self._username(request)
        extra = self._extra(request, status, start)

        if status >= 400 and 'application/json' in response.get('Content-Type', ''):
            try:
                extra['response_body'] = response.content.decode()
            except Exception:
                pass

        access_log.info(
            f"{username} {request.method} {request.get_full_path()} {status}",
            extra=extra,
        )
        return response

    @staticmethod
    def _username(request):
        if hasattr(request, "user") and request.user.is_authenticated:
            return request.user.username
        return "anonymous"

    @staticmethod
    def _extra(request, status, start):
        return {
            "http_method": request.method,
            "http_path": request.get_full_path(),
            "http_status": status,
            "duration_ms": round((time.monotonic() - start) * 1000, 1),
        }


class RequestContextFilter(logging.Filter):
    """Inject HTTP request context into every log record.

    Resolved at log generation time so that DRF authentication (which runs inside
    the view, after middleware) is picked up correctly.
    """

    def filter(self, record):
        # Incoming HTTP Request headers:
        # https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpRequest.META
        request = _request.get()

        if request and hasattr(request, "user") and request.user.is_authenticated:
            record.user_id = request.user.pk
            record.username = request.user.username
        else:
            record.user_id = None
            record.username = ""

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/User-Agent
        record.user_agent = request.META.get("HTTP_USER_AGENT", "") if request else ""

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",", 1)[0].strip() if request else ""
        remote_addr = request.META.get("REMOTE_ADDR", "-") if request else "-"
        record.client_ip = forwarded_for if forwarded_for else remote_addr

        # https://www.w3.org/TR/trace-context/
        if not hasattr(record, "otelTraceID"):
            record.otelTraceID = ""

        return True


class WebSocketLoggingMiddleware:
    """Log Channels ASGI WebSocket events."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        user = scope.get("user")
        username = (user.username if user and user.is_authenticated else "anonymous")
        start = time.monotonic()

        async def logging_receive():
            message = await receive()
            if message["type"] == "websocket.receive":
                access_log.info(
                    f"{username} WS RECEIVE {path}",
                    extra={"ws_event": "receive", "ws_path": path, "username": username},
                )
            return message

        async def logging_send(message):
            if message["type"] == "websocket.accept":
                access_log.info(
                    f"{username} WS CONNECT {path}",
                    extra={"ws_event": "connect", "ws_path": path, "username": username},
                )
            elif message["type"] == "websocket.close":
                duration = round((time.monotonic() - start) * 1000, 1)
                access_log.info(
                    f"{username} WS DISCONNECT {path} duration_ms={duration}",
                    extra={"ws_event": "disconnect", "ws_path": path,"username": username, "duration_ms": duration},
                )
            await send(message)

        await self.app(scope, logging_receive, logging_send)


