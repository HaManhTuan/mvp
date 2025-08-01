from celery import Celery
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger("celery")

# Configure Celery app
celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_hijack_root_logger=False,
    task_send_sent_event=True,
)

# Initialize Celery app
def initialize_celery():
    logger.info("Initializing Celery app")
    return celery_app
