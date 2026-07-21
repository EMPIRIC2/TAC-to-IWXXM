# F17 / E14-04 — lightweight wis2box *test harness* (MQTT + HTTP dataset).
# Not the full WMO wis2box stack (too heavy for CI). Live WIS2 remains BYOC.
FROM python:3.12.11-slim-bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    mosquitto \
    curl \
    netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

COPY mosquitto.conf /etc/mosquitto/mosquitto.conf
COPY dataset_server.py entrypoint.sh /opt/wis2box-harness/
RUN chmod +x /opt/wis2box-harness/entrypoint.sh \
  && mkdir -p /var/lib/wis2box-harness/datasets

EXPOSE 1883 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=12 \
  CMD curl -sf http://127.0.0.1:8080/health \
    && nc -z 127.0.0.1 1883

ENTRYPOINT ["/opt/wis2box-harness/entrypoint.sh"]
