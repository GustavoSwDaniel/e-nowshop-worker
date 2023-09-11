import os

from aiologger.logger import Logger as AIOLogger
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler


class Logger(AIOLogger):
    def __init__(self) -> None:
        super().__init__(level=os.getenv('LOG_LEVEL', 'DEBUG'))
        formatter = \
            Formatter(fmt='%(asctime)s.%(msecs)d [%(process)d] [%(funcName)s.%(lineno)d] [%(levelname)s] %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
        default_handler = AsyncStreamHandler(level=os.getenv('LOG_LEVEL', 'DEBUG'), formatter=formatter)
        self.add_handler(default_handler)
