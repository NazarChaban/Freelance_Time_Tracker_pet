FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    gcc \
    musl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

WORKDIR /app/freelance_time_tracker

EXPOSE 8000

ENTRYPOINT [ "/app/docker-entrypoint.sh" ]