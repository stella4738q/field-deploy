import base64
import copy
import json
import os
from distutils.util import strtobool
from abc import ABC

import numpy as np
import pandas as pd
import datetime
from bson import ObjectId

from src.components.batch_result import BatchResult
from src.dao.interface.abstract_dao import AbstractGenericDao
from src.dao.mongo.common import Mongo

from src.constants.foler_and_file_const import FolderAndFileConst
from src.utility.logger import MyLogger


def status_check(current, update, force=False):
    if current is None:
        return True

    if current == update:
        return False

    if force:
        return True
    else:
        return current == 0 or update < current


class MongoDao(AbstractGenericDao, ABC):

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def db_handler(self):
        return self._db_handler

    @db_handler.setter
    def db_handler(self, value):
        self._db_handler = value

    def __init__(self, config, logging_level='DEBUG'):
        self.config = config
        self.db_handler = Mongo(config)

        # init logger
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()

    def create(self, data, **kwargs):
        if data is not None:
            db, client = self.db_handler.connect()
            collection = kwargs.get('collection')
            collection = db[collection]
            try:
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
                client.close()

    def update(self, data, **kwargs):
        if data is not None:
            db, client = self.db_handler.connect()
            collection = kwargs.get('collection')
            collection = db[collection]

            condition = kwargs.get('condition')
            try:
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
                client.close()

    def delete(self, **kwargs):
        db, client = self.db_handler.connect()
        collection = kwargs.get('collection')
        collection = db[collection]
        condition = kwargs.get('condition')
        try:
            collection.delete_many(condition)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def write_log(self, result: BatchResult):
        post_data = result.__dict__

        db, client = self.db_handler.connect()
        try:
            db.batch_log.insert_one(post_data)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def insert_eci(self, data):
        db, client = self.db_handler.connect()
        try:
            db.essci.insert_one(data)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def get_eci_settings(self):
        db, client = self.db_handler.connect()
        try:
            post = {
                'key': {'$in': ['eci_warning_std', 'eci_threshold']}
            }
            cursor = db.system_settings.find(post)
            pd_data = pd.DataFrame(list(cursor))
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return pd_data

    def upsert_essci(self, condition, data):
        db, client = self.db_handler.connect()
        try:
            db.essci.update_one(condition, {'$set': data}, upsert=True)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def delete_essci(self, condition):
        db, client = self.db_handler.connect()
        try:
            db.essci.delete_many(condition)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def get_working_status(self):
        db, client = self.db_handler.connect()
        try:
            data = db.working_status.find_one()
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return data

    def upsert_working_status(self, status, force=False):
        db, client = self.db_handler.connect()
        try:
            # 先取回原本的狀態，狀態不一樣在變動
            _status = self.get_working_status()
            if _status is None or status_check(_status['system_status'], status, force):
                db.working_status.update_one(
                    {}, {'$set': {'system_status': int(status), 'update_time': datetime.datetime.now()}}, upsert=True)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def get_charge_schedule(self, week, current_time):
        """
        取得目前排程
        :param week:
        :param current_time:
        :return:
        """
        db, client = self.db_handler.connect()
        try:
            query = {
                'week': str(week)
            }
            cursor = db.charge_schedule.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                pd_data['start_time'] = pd.to_timedelta(pd_data['start_time'])
                pd_data['end_time'] = pd.to_timedelta(pd_data['end_time'])
                pd_data: pd.DataFrame = pd_data.query(f"start_time <= @current_time <= end_time")
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return pd_data

    def get_system_settings(self):
        db, client = self.db_handler.connect()
        try:
            cursor = db.system_settings.find({})
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return pd_data

    def get_electric_price(self, is_sum, price_level):
        db, client = self.db_handler.connect()
        try:
            query = {'is_summer': is_sum}
            if price_level is not None:
                query['price_level'] = price_level
            cursor = db.electric_price.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return pd_data

    def get_control_equipment(self, code, _id=None):
        db, client = self.db_handler.connect()
        try:
            post = {'code': code}
            if _id:
                post["_id"] = ObjectId(_id)
            cursor = db.equipments.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'field_id': str})
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return pd_data

    def upsert_electric_report(self, data_list):
        db, client = self.db_handler.connect()
        batch_size = 500
        try:
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                bulk_op = db.electric_report.initialize_ordered_bulk_op()
                for item in batch:
                    bulk_op.find({
                        'start_date': item['start_date'],
                        'end_date': item['end_date']
                    }).upsert().update(
                        {'$set': item})
                bulk_op.execute()
            client.close()
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
