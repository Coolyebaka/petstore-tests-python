import time
from typing import Any, Callable, Optional

from config.settings import Settings
from utils.logger import logger


def retry_until_condition(
    operation: Callable[[], Any],
    condition: Callable[[Any], bool],
    max_retries: Optional[int] = None,
    delay: Optional[float] = None,
    error_message: Optional[str] = None,
) -> Any:
    max_retries = max_retries or Settings.MAX_RETRIES
    delay = delay or Settings.RETRY_DELAY
    error_message = error_message or "Condition not met after all retries"

    last_result = None
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            result = operation()
            last_result = result

            if condition(result):
                if attempt > 1:
                    logger.info(f"Condition met on attempt {attempt}")
                return result
            else:
                if attempt < max_retries:
                    logger.debug(
                        f"Condition not met on attempt {attempt}/{max_retries}, retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.warning(f"Condition not met after {max_retries} attempts")

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.debug(
                    f"Operation failed on attempt {attempt}/{max_retries}: {str(e)}, retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"Operation failed after {max_retries} attempts: {str(e)}")

    if last_exception:
        raise AssertionError(f"{error_message}. Last error: {str(last_exception)}")
    else:
        raise AssertionError(f"{error_message}. Last result: {last_result}")
