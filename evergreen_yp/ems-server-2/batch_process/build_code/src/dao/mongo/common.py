import os
from distutils.util import strtobool
from urllib import parse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from src.constants.config_const import DataBaseConfigConst
from src.constants.foler_and_file_const import FolderAndFileConst
from src.utility.logger import MyLogger


class Mongo:
    def __init__(self, config, logging_level='DEBUG'):
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        self.config = config

    def connect(self):
        try:
            replacaset = self.config[DataBaseConfigConst.REPLICASET.value]
            if replacaset is not None and replacaset != '':
                replacaset_list = self.config[DataBaseConfigConst.REPLICASET_LIST.value]
                username = parse.quote_plus(self.config[DataBaseConfigConst.USERNAME.value])
                pwd = parse.quote_plus(self.config[DataBaseConfigConst.PASSWORD.value])
                conn_str = f'mongodb://{username}:{pwd}@{replacaset_list}/?authSource=admin'
                client = MongoClient(conn_str)
            else:
                username = parse.quote_plus(self.config[DataBaseConfigConst.USERNAME.value])
                pwd = parse.quote_plus(self.config[DataBaseConfigConst.PASSWORD.value])
                client = MongoClient('mongodb://{0}:{1}@{2}:{3}'.format(
                    username, pwd, self.config[DataBaseConfigConst.URI.value],
                    self.config[DataBaseConfigConst.PORT.value]))
            database_name = self.config[DataBaseConfigConst.DATABASE_NAME.value]
            db = client[database_name]
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except ConnectionFailure as e:
            self.logger.exception(repr(e))
            raise ConnectionFailure
        except Exception as e:
            self.logger.error('Exception happened when connect to mongodb.')
            self.logger.exception(repr(e))
            raise Exception
        return db, client

