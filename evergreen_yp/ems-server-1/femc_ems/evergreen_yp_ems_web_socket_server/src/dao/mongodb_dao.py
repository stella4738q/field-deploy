import json
import os
from abc import ABC
from distutils.util import strtobool
from urllib import parse

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from .abstract_dao import AbstractDao
from ..constants.foler_and_file_const import FolderAndFileConst
from ..utility.logger import MyLogger


class AbstractMongoDBDao(AbstractDao, ABC):
    pass


class MongoDBDao(AbstractMongoDBDao):

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

    def __init__(self, host, user_name, password, database_name):
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        self.host = host
        self.user_name = user_name
        self.password = password
        self.database_name = database_name

    def get_connect(self):
        return self.__connect()

    def __connect(self):
        try:
            # self.logger.info('Create mongodb client')
            replacaset_list = self.host
            username = parse.quote_plus(self.user_name)
            pwd = parse.quote_plus(self.password)
            conn_str = f'mongodb://{username}:{pwd}@{replacaset_list}/?authSource=admin'
            client = MongoClient(conn_str)
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
        return client

    def create(self, data, **kwargs):
        if data is not None:
            client = self.__connect()
            # self.logger.info('get target database name')
            db = client[self.database_name]

            # self.logger.info('get target collection name')
            collection = kwargs.get('collection')
            collection = db[collection]
            try:
                # self.logger.info('insert data ...')
                if type(data) is list:
                    collection.insert_many(data)
                else:
                    if type(data) is not dict:
                        data = json.dumps(data)
                    collection.insert_one(data)
            except KeyError as e:
                self.logger.exception(repr(e))
                raise KeyError
            except Exception as e:
                self.logger.exception(repr(e))
                raise Exception
            finally:
                # self.logger.info('close mongodb client')
                client.close()

    def read(self, **kwargs):
        raise NotImplementedError

    # @slack_message(title='MongoDB DAO update method')
    def update(self, data, **kwargs):
        if data is not None:
            client = self.__connect()
            # self.logger.info('get target database name')
            db = client[self.database_name]

            # self.logger.info('get target collection name')
            collection = kwargs.get('collection')
            collection = db[collection]

            condition = kwargs.get('condition')
            try:
                # self.logger.info('insert data ...')
                if type(data) is list:
                    collection.update_many(condition, {'$set': data}, upsert=True)
                else:
                    if type(data) is not dict:
                        data = json.dumps(data)
                    collection.update_one(condition, {'$set': data}, upsert=True)
            except KeyError as e:
                self.logger.exception(repr(e))
                raise KeyError
            except Exception as e:
                self.logger.exception(repr(e))
                raise Exception
            finally:
                # self.logger.info('close mongodb client')
                client.close()

    # @slack_message(title='MongoDB DAO delete method')
    def delete(self, **kwargs):
        raise NotImplementedError
