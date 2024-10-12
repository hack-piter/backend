
FROM python:slim

WORKDIR /app

RUN pip install --no-cache-dir alembic sqlalchemy[asyncio] psycopg2-binary apscheduler confluent_kafka python-dotenv asyncpg


ENV PYTHONUNBUFFERED=1

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_NAME

ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_PORT=$POSTGRES_PORT
ENV POSTGRES_NAME=$POSTGRES_NAME

COPY ./db /app/scheduler/db
COPY ./scheduler /app/scheduler

CMD ["python", "./scheduler/run_scheduler.py"]