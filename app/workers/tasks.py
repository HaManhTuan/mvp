from app.workers.celery_app import celery_app
from app.utils.logger import get_logger
from celery.utils.log import get_task_logger

# Get Celery task logger
celery_logger = get_task_logger(__name__)
# Get application logger
logger = get_logger("tasks")

@celery_app.task(name="example_task")
def example_task(name: str):
    """
    Example task that logs a message
    
    Args:
        name: Name to include in the logged message
    
    Returns:
        Result message
    """
    logger.info(f"Running example task for {name}")
    
    # Simulate task processing
    import time
    time.sleep(2)
    
    result = f"Hello, {name}! Task completed."
    logger.info(f"Task completed with result: {result}")
    
    return result

@celery_app.task(name="process_data", bind=True, max_retries=3)
def process_data(self, data_id: str, options: dict = None):
    """
    Example of data processing task with retry capabilities
    
    Args:
        self: Task instance (injected by Celery when bind=True)
        data_id: ID of the data to process
        options: Optional processing options
    
    Returns:
        Processing result
    """
    logger.info(f"Processing data {data_id} with options {options}")
    
    try:
        # Simulate processing
        import time
        time.sleep(3)
        
        # Return success result
        return {"status": "success", "data_id": data_id, "message": "Data processed successfully"}
        
    except Exception as exc:
        logger.error(f"Error processing data {data_id}: {str(exc)}")
        # Retry with exponential backoff
        retry_in = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=retry_in)
