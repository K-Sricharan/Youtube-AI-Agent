import functools
import time
from typing import Callable, Any
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("retry_decorator")

def retry_on_exception(
    max_retries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator to retry a function call with exponential backoff on exceptions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function '{func.__name__}' failed after {max_retries} attempts. Final error: {e}")
                        raise
                    logger.warning(
                        f"Function '{func.__name__}' failed (Attempt {attempt}/{max_retries}). "
                        f"Retrying in {current_delay:.1f}s... Error: {e}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
