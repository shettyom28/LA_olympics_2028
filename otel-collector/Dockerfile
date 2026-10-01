FROM docker.io/otel/opentelemetry-collector-contrib:0.147.0
COPY otelcol-contrib-config.yaml /etc/otelcol-contrib/config.yaml
CMD ["--config", "/etc/otelcol-contrib/config.yaml", "--feature-gates", "receiver.postgresql.separateSchemaAttr"]
