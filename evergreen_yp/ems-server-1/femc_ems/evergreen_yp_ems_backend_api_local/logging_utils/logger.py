import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from .constant import LogFormatConst


class Logger:
    @property
    def log_format(self):
        return self._log_format

    @log_format.setter
    def log_format(self, log_format):
        self._log_format = log_format

    def __init__(self, log_format=None):
        if log_format is None:
            log_format = LogFormatConst.FORMAT_2.value
        self._log_format = log_format

    def create(self, name, level=logging.INFO, log_path=None, user_name='system'):
        """
        Get or create logger
        :param name: logger name
        :param level: logging level
        :return: logger object
        """
        if not isinstance(name, str):
            raise TypeError
        logger = logging.getLogger(name)
        if logger.hasHandlers():
            logger.handlers.clear()

        # if log_path is None:
        #     time = datetime.now()
        #     log_path = f'./Log/{time:%Y-%m-%d}/'
        # else:
        #     time = datetime.now()
        #     log_path = os.path.join(log_path, f'{time:%Y-%m-%d}/')
        time = datetime.now()
        log_path = os.path.join(log_path, f'{time:%Y-%m-%d}/', user_name)
        if os.path.isdir(log_path):
            # time = datetime.now()
            # log_path = os.path.join(log_path, f'{time:%Y-%m-%d}/', user_name)
            handler = RotatingFileHandler(f'{log_path}{time:/%Y-%m-%d_%H}.log', maxBytes=10000000, backupCount=5)
        else:
            os.makedirs(log_path)
            handler = RotatingFileHandler(f'{log_path}{time:/%Y-%m-%d_%H}.log', maxBytes=10000000, backupCount=5)

        logger.setLevel(level)
        formatter = logging.Formatter(self.log_format)
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(streamHandler)

        return logger
