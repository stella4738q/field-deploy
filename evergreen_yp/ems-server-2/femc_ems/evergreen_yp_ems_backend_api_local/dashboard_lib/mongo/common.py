import copy
import datetime
from urllib import parse

import pymongo
from flask import session
from pymongo import MongoClient, monitoring

from dashboard_lib.constant import ConfigConstant


class CommandLogger(monitoring.CommandListener):
    def __init__(self, conn_str, db_name):
        self.client = MongoClient(conn_str)
        self.db = self.client[db_name]
        self.log_collection = 'system_logs'

    def started(self, event):
        if session:
            user_info = session['user_info']
            if event.command_name == 'insert':
                collection = event.command['insert']
                docs = event.command.get('documents', [])
                for new_item in docs:
                    _new = copy.deepcopy(new_item)
                    _new['_id'] = str(new_item['_id'])
                    self.write_log(event.command_name, collection, user_info, None, _new)
            elif event.command_name == 'update':
                # 在更新操作開始前記錄相關信息
                collection = event.command['update']
                docs = event.command.get('updates', [])
                for item in docs:
                    update_set = item['u']['$set']
                    target_id = item['q']['_id']
                    if type(target_id) is dict and '$in' in target_id.keys():
                        for _id in target_id['$in']:
                            ori_data = self.db[collection].find_one({"_id": target_id})
                            if ori_data:
                                ori_data['_id'] = str(ori_data['_id'])
                                self.write_log(event.command_name, collection, user_info, ori_data, update_set)
                    else:
                        ori_data = self.db[collection].find_one({"_id": target_id})
                        if ori_data:
                            ori_data['_id'] = str(ori_data['_id'])
                            self.write_log(event.command_name, collection, user_info, ori_data, update_set)
            elif event.command_name == 'delete':
                # 在刪除操作開始前記錄相關信息
                collection = event.command['delete']
                docs = event.command.get('deletes', [])
                for item in docs:
                    target_id = item['q']['_id']
                    if type(target_id) is dict and '$in' in target_id.keys():
                        for _id in target_id['$in']:
                            ori_data = self.db[collection].find_one({"_id": _id})
                            if ori_data:
                                ori_data['_id'] = str(ori_data['_id'])
                                self.write_log(event.command_name, collection, user_info, ori_data, None)
                    else:
                        ori_data = self.db[collection].find_one({"_id": target_id})
                        if ori_data:
                            ori_data['_id'] = str(ori_data['_id'])
                            self.write_log(event.command_name, collection, user_info, ori_data, None)

    def succeeded(self, event):
        pass

    def failed(self, event):
        pass

    def write_log(self, action, collection, user_info, old_value, new_value):
        if collection != self.log_collection:
            self.db[self.log_collection].insert_one({
                "date": datetime.datetime.now(),
                "collection": collection,
                "action": action,
                "old_value": old_value,
                "new_value": new_value,
                "modified_on": datetime.datetime.now(),
                "modified_by": user_info.user_id,
                "modified_name": user_info.user_name
            })


class Mongo:
    STORAGE = ConfigConstant.MONGODB.value

    def __init__(self, config):
        self.config = config

    def connect(self):
        db_config = self.config[ConfigConstant.STORAGE.value][ConfigConstant.DATABASE.value][self.STORAGE][ConfigConstant.LOCALDB.value]
        database_name = db_config[ConfigConstant.DATABASE_NAME.value]
        replacaset = db_config[ConfigConstant.REPLICASET.value]
        if replacaset is not None and replacaset != '':
            replacaset_list = db_config[ConfigConstant.REPLICASET_LIST.value]
            username = parse.quote_plus(db_config[ConfigConstant.USERNAME.value])
            pwd = parse.quote_plus(db_config[ConfigConstant.PWD.value])
            conn_str = f'mongodb://{username}:{pwd}@{replacaset_list}/?authSource=admin'
            client = pymongo.MongoClient(conn_str, event_listeners=[CommandLogger(conn_str, database_name)])
        else:
            username = parse.quote_plus(db_config[ConfigConstant.USERNAME.value])
            pwd = parse.quote_plus(db_config[ConfigConstant.PWD.value])
            conn_str = 'mongodb://{0}:{1}@{2}:{3}'.format(
                username, pwd, db_config[ConfigConstant.URI.value], db_config[ConfigConstant.PORT.value])
            client = pymongo.MongoClient(conn_str, event_listeners=[CommandLogger(conn_str, database_name)])
        db = client[database_name]
        return db, client
