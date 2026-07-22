FROM python:3.12-slim

WORKDIR /app
COPY server.py /app/server.py
ENV F19_HARNESS_PORT=9099
EXPOSE 9099
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9099/health').read()"
CMD ["python", "-u", "/app/server.py"]
