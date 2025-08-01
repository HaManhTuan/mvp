import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.tracing import get_trace_logger, set_trace_context_from_request, add_trace_headers_to_response

logger = get_trace_logger("http")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set up request tracing context and get the request ID
        request_id = set_trace_context_from_request(request)
        
        # Get logger with request ID from context
        request_logger = get_trace_logger("http")
        
        # Log the request
        request_logger.info(f"{request.method} {request.url.path}")
        
        # Process the request and track timing
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log the response
            request_logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - Time: {process_time:.4f}s"
            )
            
            # Add trace headers to response
            add_trace_headers_to_response(response, request_id)
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            request_logger.error(
                f"{request.method} {request.url.path} - "
                f"Error: {str(e)} - Time: {process_time:.4f}s"
            )
            raise

def setup_logging_middleware(app: FastAPI):
    """Setup logging middleware for FastAPI app"""
    app.add_middleware(LoggingMiddleware)
    return app
