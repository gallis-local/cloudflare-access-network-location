FROM python:3.14.1-slim

WORKDIR /app

COPY access-update.py /app/

RUN chmod +x /app/access-update.py

ENTRYPOINT ["/app/access-update.py"]
