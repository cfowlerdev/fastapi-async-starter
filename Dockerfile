FROM python:3.11.2-slim-buster

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt clean && \
    rm -rf /var/cache/apt/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH "$PATH:/app/scripts"

RUN useradd -m -d /app -s /bin/bash app \
    && chown -R app:app /app/* && chmod +x /app/scripts/*

WORKDIR /app
USER app

CMD ["./scripts/start-dev.sh"]
