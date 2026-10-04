import os
import pytest
from workers.celery_app import celery_app

@pytest.fixture(autouse=True)
def configure_celery_test_mode():
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    yield
