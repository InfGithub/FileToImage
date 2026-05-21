from time import time, strftime, localtime
from atexit import register
from typing import Literal, TextIO, List
from functools import wraps


LEVELS: List[str] = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
type LevelType = Literal["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]

class Logger:
    def __init__(
        self,
        path: str = "latest.log",
        level: LevelType = "INFO"
    ):
        self.path: str = path
        self.level: LevelType = level

        with open(self.path, mode="w", encoding="utf-8"):
            pass

        self.handle: TextIO = open(self.path, mode="a", encoding="utf-8", buffering=1)
        register(self.exit)

    def log(
        self,
        *texts: object,
        level: LevelType,
        thread: str,
        **kwargs
    ):
        if LEVELS.index(level) < LEVELS.index(self.level):
            return

        for obj in texts:
            text: str = f"[{strftime("%H:%M:%S", localtime())}] [{thread}/{level}]: {obj}\n"
            self.handle.write(text)
            self.handle.flush()

            print(text, end="", **kwargs)

    def set(self, level: LevelType):
        self.level = level

    def exit(self):
        if hasattr(self, "handle") and self.handle and not self.handle.closed:
            self.handle.close()

    def trace(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "TRACE", thread = thread, *texts, **kwargs)

    def debug(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "DEBUG", thread = thread, *texts, **kwargs)

    def info(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "INFO", thread = thread, *texts, **kwargs)

    def warn(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "WARN", thread = thread, *texts, **kwargs)

    def error(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "ERROR", thread = thread, *texts, **kwargs)

    def fatal(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "FATAL", thread = thread, *texts, **kwargs)


def timer(func):
    """
    简易装饰器函数。

    该函数用于测量被装饰函数的执行时间。

    Args:
        func (callable): 要被测量执行时间的函数。
    
    Returns:
        callable: 被装饰后的函数。

    Example:
        >>> @timer
        ... def my_function():
        ...     pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper