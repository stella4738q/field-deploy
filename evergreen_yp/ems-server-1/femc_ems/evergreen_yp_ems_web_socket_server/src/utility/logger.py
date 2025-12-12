import logging
import os
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler


class LogFormatConst(Enum):
    CONSOLE_FORMAT = '[%(asctime)s] - {%(lineno)d} - %(name)s - %(levelname)s - %(message)s'
    FILE_FORMAT = '[%(asctime)s] - p%(process)s - {%(pathname)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s'


class MyLogger:
    def __init__(self, logger_name, logging_level: str = 'debug'):
        """
        My logger used to log system execution information.
        Logging level is fixed (debug for main logger, info for console handler, debug/error for file handler).

        :param logger_name: logger name
        """
        logger = logging.getLogger(logger_name)
        if logger.hasHandlers():
            logger.handlers.clear()

        logging_level = logging_level.upper()
        logging_level_eval = eval(f'logging.{logging_level}')
        if logging_level_eval not in [logging.CRITICAL, logging.FATAL, logging.ERROR, logging.WARNING, logging.WARN,
                                      logging.INFO, logging.DEBUG, logging.NOTSET]:
            raise ValueError(f'{logging_level} not in available list.')
        logger.setLevel(logging_level)

        self.__logger = logger
        self.add_console_handler(logging_level)

    @staticmethod
    def setup(handler, log_format):
        handler.setFormatter(logging.Formatter(log_format))
        return handler

    def get(self):
        return self.__logger

    @staticmethod
    def create_log_dir(log_dir):
        if os.path.exists(log_dir):
            if os.path.isdir(log_dir):
                pass
            else:
                raise FileExistsError
        else:
            os.makedirs(log_dir)

    @staticmethod
    def generate_log_file_name():
        time = datetime.now()
        debug_log_file, info_log_file, error_log_file = \
            f'debug_{time:%Y-%m-%d}.log', f'info_{time:%Y-%m-%d}.log', f'error_{time:%Y-%m-%d}.log'
        return debug_log_file, info_log_file, error_log_file

    def __add_file_handler(self, filepath, level):
        backup_cnt = 10
        max_bytes = 10 ** 7
        handler = RotatingFileHandler(filepath, maxBytes=max_bytes, backupCount=backup_cnt)
        handler.setLevel(level)
        handler = self.setup(handler, LogFormatConst.FILE_FORMAT.value)
        self.__logger.addHandler(handler)

    def add_file_handler(self, log_dir, log_file_name=None):
        """
        Info/Debug/Error log files will be generated under log_dir.
        Log files with respect to different level will be separated and with different prefix.

        :param log_dir: log directory name
        :param log_file_name: log file name
        :return: logger
        """
        self.create_log_dir(log_dir)
        if log_file_name is None:
            debug_log_file, info_log_file, error_log_file = self.generate_log_file_name()
        else:
            debug_log_file = 'debug_' + log_file_name
            info_log_file = 'info_' + log_file_name
            error_log_file = 'error_' + log_file_name

        # add debug handler
        debug_log_file_path = os.path.join(log_dir, debug_log_file)
        self.__add_file_handler(debug_log_file_path, logging.DEBUG)

        # add info handler
        info_log_file_path = os.path.join(log_dir, info_log_file)
        self.__add_file_handler(info_log_file_path, logging.INFO)

        # add error handler
        error_log_file_path = os.path.join(log_dir, error_log_file)
        self.__add_file_handler(error_log_file_path, logging.ERROR)
        return self.__logger

    def add_console_handler(self, logging_level):
        """
        Console handler, logging level is fixed as INFO

        :return: logger
        """
        info_handler = logging.StreamHandler()
        info_handler.setLevel(logging_level)
        info_handler = self.setup(info_handler, LogFormatConst.CONSOLE_FORMAT.value)
        self.__logger.addHandler(info_handler)
        return self.__logger
