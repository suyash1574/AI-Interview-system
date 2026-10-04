import os
import sys
from celery import Celery
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
    or settings.ENVIRONMENT == "test"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=is_testing,
    task_eager_propagates=is_testing,
)
