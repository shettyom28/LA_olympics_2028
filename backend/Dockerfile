FROM docker.io/library/python:3.12

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Required for any Python requirements that need to be compiled
#RUN apt-get update -y \
#    && apt-get install -y --no-install-recommends \
#        build-essential \
#        pkg-config \
#        python3-dev \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --root-user-action ignore --no-cache-dir -r requirements.txt

COPY . .

# Build-time tests: bypass with docker --build-arg RUN_TESTS=0
ARG RUN_TESTS=1
RUN if [ "$RUN_TESTS" = "1" ]; then pip install --root-user-action ignore --no-cache-dir -r requirements-dev.txt; fi
RUN if [ "$RUN_TESTS" = "1" ]; then DJANGO_SETTINGS_MODULE=mysite.settings.dev python -m pytest; fi
RUN if [ "$RUN_TESTS" = "1" ]; then pip-audit -r requirements.txt; fi

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Collect static files for WhiteNoise
RUN DJANGO_SETTINGS_MODULE=mysite.settings.build python manage.py collectstatic --no-input

# Default environment for production containers
ENV DJANGO_SETTINGS_MODULE="mysite.settings.prod"

# OpenTelemetry - default to off
ENV OTEL_SERVICE_NAME="app-backend"
ENV OTEL_TRACES_EXPORTER="none"
ENV OTEL_METRICS_EXPORTER="none"
ENV OTEL_LOGS_EXPORTER="none"
ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"
ENV OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
ENV OTEL_PYTHON_DJANGO_EXCLUDED_URLS="health,metrics"

EXPOSE 8000

VOLUME ["/app/storage"]

CMD ["sh", "/app/entrypoint.sh"]
