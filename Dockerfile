FROM python:3.15.0a6-slim

WORKDIR /app

COPY access-update.py /app/

RUN chmod +x /app/access-update.py

ENTRYPOINT ["/app/access-update.py"]
