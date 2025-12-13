import os
from distutils.util import strtobool
import pandas as pd
import pymssql

from src.constants.config_const import DataBaseConfigConst
from src.constants.foler_and_file_const import FolderAndFileConst

from src.utility.logger import MyLogger


class MssqlDao:

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def __init__(self, config, logging_level='DEBUG'):
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        self.config = config

    def connect(self):
        try:
            server = self.config[DataBaseConfigConst.URI.value]
            port = self.config[DataBaseConfigConst.PORT.value]
            username = self.config[DataBaseConfigConst.USERNAME.value]
            password = self.config[DataBaseConfigConst.PASSWORD.value]
            database = self.config[DataBaseConfigConst.DATABASE_NAME.value]
            client = pymssql.connect(server=server, port=port, user=username, password=password, database=database,
                                     tds_version="7.0")
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError(e)
        except Exception as e:
            self.logger.error('Exception happened when connect to mssqldb.')
            self.logger.exception(repr(e))
            raise Exception(e)
        return client
