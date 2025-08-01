from fastapi import Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import set_request_id, get_logger, get_request_id

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that makes request context available throughout the request lifecycle.
    This allows accessing request info like the request_id from anywhere in the code.
    """
    
    async def dispatch(self, request: Request, call_next):
        # The request ID is already set in LoggingMiddleware,
        # but we could add more request context here if needed
        
        # Continue processing the request
        response = await call_next(request)
        return response


def get_context_logger(name=None):
    """
    Get a logger with the current request ID and optional name
    
    This is a convenience wrapper around get_logger that ensures
    we're using the current request ID from the context.
    
    Args:
        name: Optional name for the logger context
        
    Returns:
        Logger instance with request ID bound
    """
    # The request ID should already be set in the context by the LoggingMiddleware
    # This function just makes it easier to get a logger with that ID
    return get_logger(name)

def get_request_context(request: Request):
    """
    Dependency to extract and return important context data from the request.
    Can be used in route functions to access request context.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        Dict containing request context information
    """
    request_id = getattr(request.state, "request_id", None)
    
    # You could add more context data here if needed
    context = {
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
    }
    
    return context
