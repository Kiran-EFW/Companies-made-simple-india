import time
import functools
from typing import Callable, Any
from src.utils.logging_utils import logger

def with_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    A simple decorator for retrying a function with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e
                    
                    logger.info(f"Retrying {func.__name__} in {current_delay}s... (Attempt {retries}/{max_retries})")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator
