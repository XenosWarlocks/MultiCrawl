import logging
import traceback
from typing import Callable, Any, Optional
import asyncio
from functools import wraps

class ErrorHandler:
    """
    Utility class for handling and managing errors across the application.
    Provides decorators and methods for robust error management.
    """
    
    def __init__(self, 
                 log_file: Optional[str] = 'app_errors.log', 
                 log_level: int = logging.ERROR):
        """
        Initialize the error handler with logging configuration.
        
        :param log_file: Path to the error log file
        :param log_level: Logging level
        """
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def retry(
        max_attempts: int = 3, 
        delay: float = 1.0, 
        backoff: float = 2.0, 
        exceptions: tuple = (Exception,)
    ):
        """
        Decorator to retry a function with exponential backoff.
        
        :param max_attempts: Maximum number of retry attempts
        :param delay: Initial delay between retries
        :param backoff: Multiplier for delay between retries
        :param exceptions: Tuple of exceptions to catch and retry
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                _delay = delay
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts - 1:
                            raise
                        
                        logging.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {_delay} seconds..."
                        )
                        
                        await asyncio.sleep(_delay)
                        _delay *= backoff
            return wrapper
        return decorator
    
    def handle_exception(self, 
                         func: Callable, 
                         default_return: Any = None, 
                         log_traceback: bool = True):
        """
        Decorator to handle exceptions for a given function.
        
        :param func: Function to wrap
        :param default_return: Value to return if exception occurs
        :param log_traceback: Whether to log full traceback
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {e}")
                
                if log_traceback:
                    self.logger.error(traceback.format_exc())
                
                return default_return
        return wrapper
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """
        Log an error with optional exception details.
        
        :param message: Error message
        :param error: Optional exception object
        """
        if error:
            self.logger.error(f"{message}: {error}")
            self.logger.error(traceback.format_exc())
        else:
            self.logger.error(message)