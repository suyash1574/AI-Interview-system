import os
import sys
from celery import Celery
from kombu import Exchange, Queue
from backend.config import settings


celery_app = Celery(
    "autergo",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    include=["workers.tasks.evaluation", "workers.tasks.reports"]
)

is_testing = bool(
    os.environ.get("PYTEST_CURRENT_TEST")
    or os.environ.get("TESTING")
    or "pytest" in sys.modules
    or getattr(settings, "ENV", "development") == "test"
)

default_exchange = Exchange("default", type="direct")
dlx_exchange = Exchange("dlx", type="direct")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=is_testing,
    task_eager_propagates=is_testing,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    task_queues=(
        Queue("default", default_exchange, routing_key="default"),
        Queue("dead_letter", dlx_exchange, routing_key="dead_letter"),
    ),
)

