import os
from distutils.util import strtobool
import pandas as pd
import cx_Oracle

from src.constants.config_const import DataBaseConfigConst
from src.constants.foler_and_file_const import FolderAndFileConst

from src.utility.logger import MyLogger


class OracleDao:

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
            username = self.config[DataBaseConfigConst.USERNAME.value]
            password = self.config[DataBaseConfigConst.PASSWORD.value]
            ip = self.config[DataBaseConfigConst.URI.value]
            port = self.config[DataBaseConfigConst.PORT.value]
            conn_str = f'{username}/{password}@{ip}:{port}'
            client = cx_Oracle.connect(conn_str)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError(e)
        except Exception as e:
            self.logger.error('Exception happened when connect to oracledb.')
            self.logger.exception(repr(e))
            raise Exception(e)
        return client

    def execute(self, sql_stmt):
        self.logger.info('run sql statement')
        success = True
        msg = None

        conn = self.connect()
        pd_data = None
        try:
            pd_data = pd.read_sql(sql_stmt, conn)
            conn.commit()
        except Exception as ex:
            msg = """ Exception: {} \n sql: {}""".format(ex, sql_stmt)
            self.logger.error(msg)
            success = False
        finally:
            if conn is not None:
                self.logger.info('close connection')
                conn.close()
            if not success:
                raise Exception(msg)
        return pd_data

