"""
Script to start Celery worker.

This script runs a Celery worker that processes background tasks.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.workers.celery_app import celery_app
from app.utils.logger import get_logger

logger = get_logger("celery_worker")

if __name__ == "__main__":
    logger.info("Starting Celery worker")
    sys.argv = ["celery", "worker", "--loglevel=info"]
    celery_app.worker_main(sys.argv)
