from typing import Callable, Any
import time
import phdkit
import phdkit.log

class AutoRetryError(Exception):
    """Custom exception for LLMBridge errors."""
    def __init__(self, message: str, exceptions: list[Exception] = []):
        super().__init__(message)
        self.message = message
        self.exceptions = exceptions

    def __str__(self) -> str:
        return f"AutoRetryError: {self.message}"

    def __repr__(self) -> str:
        return f"AutoRetryError({self.message!r}, {self.exceptions!r})"


class AutoRetry:
    def __init__(self, func: Callable[..., Any], logger: phdkit.log.Logger | None = None, *, max_retrys: int = 5, increment_factor: float = 2, decrement_num: int = 10):
        self.llm_api_call = func
        self.max_retrys = max_retrys
        self.__init_retry_delay = 10.0
        self.retry_delay = self.__init_retry_delay
        self.increment_factor = increment_factor
        self.decrement_num = decrement_num
        self.logger = logger

    def reset(self):
        """Reset the retry count and delay to initial values."""
        self.retry_delay = self.__init_retry_delay

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Call the wrapped function with retry logic."""
        return self.call(*args, **kwds)

    def call(self, *args, **kwargs) -> Any:
        exceptions = []
        retry_count = 0
        while retry_count < self.max_retrys:
            try:
                r = self.llm_api_call(*args, **kwargs)
                self.retry_delay -= max(self.__init_retry_delay, self.decrement_num)
                if self.logger is not None:
                    self.logger.debug(f"AutoRetry: {self.llm_api_call.__name__} succeeded",
                                      f"{args=}, {kwargs=}, result={repr(r)}\n{retry_count=}, {self.retry_delay=}")
                return r
            except Exception as e:
                exceptions.append(e)
                retry_count += 1
                if self.logger is not None:
                    self.logger.debug(f"AutoRetry: {self.llm_api_call.__name__} failed",
                                        f"{args=}, {kwargs=}\n{repr(e)}\n{retry_count=}, {self.retry_delay=}")
                if retry_count >= self.max_retrys:
                    if self.logger is not None:
                        self.logger.error(f"AutoRetry: {self.llm_api_call.__name__} failed",
                                          f"{args=}, {kwargs=}\n{exceptions=}\n{self.max_retrys=}, {self.retry_delay=}")
                    raise AutoRetryError(
                        f"AutoRetry failed after {self.max_retrys} attempts.",
                        exceptions=exceptions
                    )
                self.retry_delay *= self.increment_factor
                time.sleep(self.retry_delay)

