"""Celery application configured with Redis broker and result backend."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "plotiq",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.score_tasks",
        "app.workers.document_tasks",
        "app.workers.embedding_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry config applied per-task
    task_default_retry_delay=10,
    task_max_retries=3,
    # Beat schedule for periodic tasks
    beat_schedule={
        "flag-stale-listings": {
            "task": "app.workers.score_tasks.flag_stale_listings_task",
            "schedule": 86400.0,  # daily
        }
    },
)
