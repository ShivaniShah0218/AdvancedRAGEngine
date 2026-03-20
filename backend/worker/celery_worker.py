"""
Celery application configuration.
- Broker: Redis
- Result backend: Redis
- Tasks are discovered via conf.imports
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ingestion_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.imports = ["backend.worker.tasks"]

celery_app.conf.task_routes = {
    "backend.worker.tasks.ingest_document": {"queue": "ingestion_queue"},
}

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
