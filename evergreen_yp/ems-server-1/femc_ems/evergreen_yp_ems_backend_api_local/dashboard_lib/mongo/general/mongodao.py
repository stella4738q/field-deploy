import datetime
import hashlib
import logging
import random
import re

import itertools
import json
import uuid
from abc import ABC

import numpy as np
import pandas
import pandas as pd
import pymongo
from bson import ObjectId

from dashboard_lib.constant import ConfigConstant
from dashboard_lib.interface.abstract_dao import AbstractGenericDao
from dashboard_lib.mongo.common import Mongo
import copy
# from datetime import datetime
from logging_utils import Logger


def fn_check_account_exist(db, account):
    post = {'account': account}
    cursor = db.users.find(post)
    pd_data = pd.DataFrame(list(cursor))
    if not pd_data.empty:
        return True
    return False


def generate_password():
    key = ['AaBbCcDdEeFfGgHhiJjKkLMmNnPpQqRrSsTtUuVvWwXxYyZz0123456789']
    new_pad = random.sample(key[0], 8)
    new_pad = ''.join(new_pad)
    return new_pad


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

    def __init__(self, config):
        self.config = config
        self.db_handler = Mongo(config)

        # init logger
        setting_config = config[ConfigConstant.APP.value]
        log_path = setting_config[ConfigConstant.LOG_PATH.value]
        self.logger = Logger().create('TokenModule', level=logging.INFO, log_path=log_path)

    # Fields
    def get_fields(self, _id=None, code=None, ip=None, name=None, address=None, geo_location=None, type=None, **kwargs):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code:
            post["code"] = code
        if ip:
            post["ip"] = ip
        if name:
            post["name"] = name
        if address:
            post["address"] = {'$regex': address, '$options': '$i'}
        if geo_location:
            post["geo_location"] = geo_location
        if type:
            post["type"] = type

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(uid) for uid in allow_field]
            post['_id'] = {"$in": allow_field}

        db, client = self.db_handler.connect()
        cursor = db.fields.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str, 'company_id': np.str, 'user_id': np.str})
        client.close()
        return pd_data

    def get_fields_many(self, _id_list=None, code_list=None):
        post = {}
        if _id_list:
            post["_id"] = {"$in": list(map(ObjectId, _id_list))}
        if code_list:
            post["code"] = {"$in": code_list}
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.fields.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'company_id': np.str, 'user_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_field(self, _id=None, code=None, ip=None, name=None, address=None, geo_location=None, type=None, company_id=None, user_id=None, middle_page=None):
        post = {
        }
        if _id:
            post["_id"] = ObjectId(_id)
        if code is not None:
            post["code"] = code
        if ip is not None:
            post["ip"] = ip
        if name is not None:
            post["name"] = name
        if address is not None:
            post["address"] = address
        if geo_location is not None:
            post["geo_location"] = geo_location
        if type is not None:
            post["type"] = type
        if company_id is not None:
            post["company_id"] = ObjectId(company_id) if company_id else ""
        if user_id is not None:
            post["user_id"] = ObjectId(user_id) if user_id else ""
        if middle_page is not None:
            post["middle_page"] = middle_page

        db, client = self.db_handler.connect()
        db.fields.insert_one(post)
        cursor = db.fields.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
            if 'company_id' in pd_data.columns:
                pd_data = pd_data.astype({'company_id': np.str})
            if 'user_id' in pd_data.columns:
                pd_data = pd_data.astype({'user_id': np.str})

        client.close()
        return pd_data

    def update_field(self, _id, code=None, ip=None, name=None, address=None, geo_location=None, type=None, company_id=None, user_id=None, middle_page=None):
        post = {"$set": {}}
        if code is not None:
            post["$set"]["code"] = code
        if ip is not None:
            post["$set"]["ip"] = ip
        if name is not None:
            post["$set"]["name"] = name
        if address is not None:
            post["$set"]["address"] = address
        if geo_location:
            post["$set"]["geo_location"] = geo_location
        if type is not None:
            post["$set"]["type"] = type
        if company_id is not None:
            post["$set"]["company_id"] = ObjectId(company_id) if company_id else ""
        if user_id is not None:
            post["$set"]["user_id"] = ObjectId(user_id) if user_id else ""
        if middle_page is not None:
            post["$set"]["middle_page"] = middle_page

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.fields.update_one(query, post)

        cursor = db.fields.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
            if 'company_id' in pd_data.columns:
                pd_data = pd_data.astype({'company_id': np.str})
            if 'user_id' in pd_data.columns:
                pd_data = pd_data.astype({'user_id': np.str})

        client.close()
        return pd_data

    def delete_field(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.fields.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    # SBSPM
    def get_SBSPM(self, sdate: str, edate: str, field_id=None, case_id=None):
        post = {
            "iso_date": {
                "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S'),
                "$lte": datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            }
        }
        if field_id:
            post["field_id"] = ObjectId(field_id)
        if case_id is not None:
            if type(case_id) is list:
                case_id_list = [ObjectId(case) for case in case_id]
                post["case_id"] = {"$in": case_id_list}
            else:
                post["case_id"] = ObjectId(case_id)

        db, client = self.db_handler.connect()
        cursor = db.sbspm.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})

        client.close()
        return pd_data

    def get_SBSPM_local(self, sdate: str, edate: str, field_id=None):
        post = {
            "time": {
                "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S'),
                "$lte": datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            },
            "field_id": field_id
        }

        db, client = self.db_handler.connect()
        cursor = db.sbspm.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})

        client.close()
        return pd_data

    # winning
    def get_winning(self, sdate: str, edate: str, field_id):
        post = {
            "start_time": {
                "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S'),
                "$lte": datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            },
            "field_id": field_id
        }

        db, client = self.db_handler.connect()
        cursor = db.bids_schedule.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})

        client.close()
        return pd_data

    # balanced
    def get_balanced(self, sdate: str, edate: str, field_id, equipment_id=None, bid_id=None, order=None):
        post = {
            "schedule_stime": {
                "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S'),
                "$lte": datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            },
            "field_id": field_id
        }
        if equipment_id:
            post["equipment_id"] = equipment_id

        if bid_id:
            post["bid_id"] = bid_id

        if order:
            post["order"] = order

        db, client = self.db_handler.connect()
        cursor = db.schedule.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})

        client.close()
        return pd_data

    # alarm real time
    def get_alarm_real_time(self, field_id, equipment_id=None, code=None):
        post = {}
        if field_id:
            post["field_id"] = field_id

        if equipment_id:
            post["equipment_id"] = equipment_id

        if code:
            post["level"] = code

        db, client = self.db_handler.connect()
        cursor = db.alarm.find(post)
        pd_data = pd.DataFrame(list(cursor))

        df = pd.DataFrame({})
        if not pd_data.empty:
            df = pd_data[pd_data['done_time'].isnull()]
            df = df.sort_values(['time'], ascending=False).groupby('equipment_id').first().reset_index()
            df = df.astype({'_id': np.str})

        client.close()
        return df

    def get_alarm_history(self, sdate: str, field_id, message=None):
        post = {
            "time": {"$gte": sdate},
            "field_id": field_id
        }
        if message:
            post["message"] = {'$regex': message, '$options': '$i'}

        db, client = self.db_handler.connect()
        cursor = db.alarm.find(post)
        pd_data = pd.DataFrame(list(cursor))

        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        return pd_data

    # alarm historical
    def get_alarm_historical(self, sdate: str, edate: str, field_id, equipment_id=None, title=None,
                             code=None, message=None, level=None, order_field='time', order_type='asc', limit=10, offset=0,done=False,
                             checked=None, check_user=None):
        if done:
            post = {
                "field_id": field_id,
                "done_time": None
            }
        else:
            post = {
                "field_id": field_id,
                "done_time": {"$ne": None}
            }
        if sdate:
            if 'time' not in post.keys():
                post['time'] = dict()
            post['time']['$gte'] = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
        if edate:
            if 'time' not in post.keys():
                post['time'] = dict()
            post['time']['$lte'] = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
        if equipment_id:
            post["equipment_id"] = equipment_id
        if title:
            post["title"] = title
        if code:
            post["code"] = code
        if message:
            post["message"] = message
        if level is not None:
            post['level'] = level
        if checked:
            if checked == 'false' or checked == 'False':
                post['checked'] = {"$ne": True}
            elif checked == 'true' or checked == 'True':
                post['checked'] = True
        if check_user:
            post['check_username'] = {'$regex': check_user, '$options': 'i'}

        db, client = self.db_handler.connect()
        total_count = db.alarm.find(post).count()
        cursor = db.alarm.find(post).sort(order_field, 1 if order_type == 'asc' else -1) \
            .skip(offset).limit(limit)
        pd_data = pd.DataFrame(list(cursor))

        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        return {
            'total_count': total_count,
            'data': pd_data
        }

    # alarm historical export
    def get_alarm_historical_export(self, sdate: str, edate: str, field_id, equipment_id=None, title=None,
                                    code=None, message=None, level=None, checked=None, check_user=None):
        post = {
            "field_id": field_id,
            "done_time": {"$ne": None}
        }
        if sdate:
            if 'time' not in post.keys():
                post['time'] = dict()
            post['time']['$gte'] = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
        if edate:
            if 'time' not in post.keys():
                post['time'] = dict()
            post['time']['$lte'] = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
        if equipment_id:
            post["equipment_id"] = equipment_id
        if title:
            post["title"] = title
        if code:
            post["code"] = code
        if message:
            post["message"] = message
        if level:
            post["level"] = level
        if checked:
            if checked == 'false' or checked == 'False':
                post['checked'] = {"$ne": True}
            elif checked == 'true' or checked == 'True':
                post['checked'] = True
        if check_user:
            post['check_username'] = {'$regex': check_user, '$options': 'i'}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.alarm.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_alarm_check(self, id_list, username):
        db, client = self.db_handler.connect()
        message = None
        try:
            id_list = [ObjectId(_id) for _id in id_list]
            condition = {'_id': {'$in': id_list}}
            data = {'checked': True, 'check_username': username, 'check_datetime': datetime.datetime.now()}
            db.alarm.update_many(condition, {'$set': data})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return message

    # alarm equipment
    def get_alarm_equipment(self, field_id):
        post = {
            "field_id": field_id
        }

        db, client = self.db_handler.connect()
        cursor = db.alarm.distinct("equipment_id", post)
        if cursor:
            sorted_equipment_ids = sorted(cursor)
        else:
            sorted_equipment_ids = list()
        return sorted_equipment_ids

    # 取得歷史得標金額總計
    def get_total_bid_amount(self, field_id):
        db, client = self.db_handler.connect()
        rtn_data = {
            'today_amount': 0,
            'total_amount': 0
        }
        now = datetime.datetime.now()
        sdate = now.strftime('%Y-%m-%d 00:00:00')
        today_post = {
            "start_time": {
                "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d 00:00:00')
            },
            "field_id": field_id,
        }
        early_post = {
            "start_time": {
                "$lt": datetime.datetime.strptime(sdate, '%Y-%m-%d 00:00:00')
            },
            "field_id": field_id,
        }
        cursor = db.bids_schedule.find(today_post)
        today_data = pd.DataFrame(list(cursor))
        if today_data.shape[0] > 0:
            rtn_data['today_amount'] = np.sum(today_data['bid_amount'])

        cursor = db.bids_schedule.find(early_post)
        early_data = pd.DataFrame(list(cursor))
        if early_data.shape[0] > 0:
            rtn_data['total_amount'] = np.sum(early_data['actual_bid_amount'])
        return rtn_data

    # Company About
    def get_company(self, _id=None, name=None, is_main=None):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if name:
            post['name'] = {'$regex': name, '$options': '$i'}
        if is_main is not None:
            post['is_main'] = is_main
        db, client = self.db_handler.connect()
        cursor = db.company.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_company(self, name, address, telephone, fax, contact, contact_telephone, no):
        db, client = self.db_handler.connect()
        post = dict()
        post['name'] = name
        if address is not None:
            post['address'] = address
        if telephone is not None:
            post['telephone'] = telephone
        if fax is not None:
            post['fax'] = fax
        if contact is not None:
            post['contact'] = contact
        if contact_telephone is not None:
            post['contact_telephone'] = contact_telephone
        if no is not None:
            post['no'] = no

        db.company.insert_one(post)
        cursor = db.company.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def update_company(self, _id, name, address, telephone, fax, contact, contact_telephone, no):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if address is not None:
            post["$set"]["address"] = address
        if telephone is not None:
            post["$set"]["telephone"] = telephone
        if fax is not None:
            post["$set"]["fax"] = fax
        if contact is not None:
            post["$set"]["contact"] = contact
        if contact_telephone is not None:
            post["$set"]["contact_telephone"] = contact_telephone
        if no is not None:
            post["$set"]["no"] = no
        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.company.update_one(query, post)

        cursor = db.company.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_company(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.company.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    # User About
    def get_users(self, _id=None, name=None, email=None, mobile=None, is_admin=None,
                  account=None, enable=None, company=None):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if name:
            post['name'] = {'$regex': name, '$options': '$i'}
        if email:
            post['email'] = {'$regex': email, '$options': '$i'}
        if mobile:
            post['mobile'] = {'$regex': mobile, '$options': '$i'}
        if is_admin is not None:
            post['is_admin'] = is_admin
        if company is not None:
            post['company'] = company
        if account:
            post['account'] = {'$regex': account}
        if enable is not None:
            post['enable'] = enable

        db, client = self.db_handler.connect()
        cursor = db.users.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_user(self, name, email, account, password, company, is_admin=0, is_field_admin=0, enable=1, mobile=None):
        db, client = self.db_handler.connect()
        if fn_check_account_exist(db, account):
            raise Exception('Account exist, please retry.')

        salt = uuid.uuid4().hex
        password = password + '_gp_' + salt
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        post = {
            'name': name,
            'email': email,
            'account': account,
            'password': hashed_password,
            'salt': salt,
            'company': company,
            'mobile': mobile,
            'enable_two_factor': False,
            'iv': None,
            'two_factor_secret_key': None,
            'temp_iv': None,
            'temp_two_factor_secret_key': None,
            'is_cloud_syn': False
        }
        if is_admin is not None:
            post['is_admin'] = is_admin
        if is_field_admin is not None:
            post['is_field_admin'] = is_field_admin
        if enable is not None:
            post['enable'] = enable

        db.users.insert_one(post)
        cursor = db.users.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def update_user(self, _id, name=None, email=None, mobile=None, is_admin=None, is_field_admin=None,
                    enable=None, company=None):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if email is not None:
            post["$set"]["email"] = email
        if mobile is not None:
            post["$set"]["mobile"] = mobile
        if is_admin is not None:
            post["$set"]["is_admin"] = is_admin
        if is_field_admin is not None:
            post["$set"]["is_field_admin"] = is_field_admin
        if enable is not None:
            post["$set"]["enable"] = enable
        post["$set"]["company"] = company

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.users.update_one(query, post)

        cursor = db.users.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_user(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.users.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    # AuthCode
    # 0000: Login Success
    # E000: User is not exist
    # E001: Account is not exist
    # E002: Password Error
    def user_login(self, account, password):
        post = {'account': account, 'enable': 1}
        db, client = self.db_handler.connect()
        cursor = db.users.find_one(post)
        if not cursor:
            self.logger.error(f'Function: user_login, Account: {account}, AuthCode:E001')
            return {
                'Success': False,
                'AuthCode': 'E001',
                'Msg': 'Login Fail'
            }

        salt = cursor['salt']
        password = password + '_gp_' + salt
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        if hashed_password != cursor['password']:
            self.logger.error(f'Function: user_login, Account: {account}, AuthCode:E002')
            return {
                'Success': False,
                'AuthCode': 'E002',
                'Msg': 'Login Fail'
            }
        else:
            login_info_id = None
            return {
                'Success': True,
                'AuthCode': '0000',
                'UserInfo': {
                    "id": str(cursor['_id']),
                    "name": cursor['name'],
                    "company": cursor['company'] if 'company' in cursor and cursor['company'] else None,
                    "enable_otp": cursor['enable_two_factor'],
                    "login_info_id": login_info_id,
                    "is_admin": bool(cursor['is_admin'])
                }
            }

    def reset_password(self, user_id, new_password=None):
        query = {'_id': ObjectId(user_id)}
        db, client = self.db_handler.connect()
        cursor = db.users.find_one(query)
        if not cursor:
            self.logger.error(f'Function: reset_password, UserId: {user_id}, AuthCode:E000')
            return {
                'Success': False,
                'AuthCode': 'E000',
                'Msg': 'System error'
            }

        salt = uuid.uuid4().hex
        pwd = new_password if new_password is not None else generate_password()
        password = pwd + '_gp_' + salt
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()

        post = {"$set": {}}
        post["$set"]["password"] = hashed_password
        post["$set"]["salt"] = salt

        db.users.update_one(query, post)
        return {
            'Success': True,
            'NewPassword': pwd
        }

    def change_password(self, user_id, old_password, new_password):
        query = {'_id': ObjectId(user_id)}
        db, client = self.db_handler.connect()
        cursor = db.users.find_one(query)
        if not cursor:
            self.logger.error(f'Function: change_password, UserId: {user_id}, AuthCode:E000')
            return {
                'Success': False,
                'AuthCode': 'E000',
                'Msg': 'System error'
            }

        salt = cursor['salt']
        password = old_password + '_gp_' + salt
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        if hashed_password != cursor['password']:
            self.logger.error(f'Function: change_password, UserId: {user_id}, AuthCode:E002')
            return {
                'Success': False,
                'AuthCode': 'E002',
                'Msg': 'Login Fail'
            }

        salt = uuid.uuid4().hex
        password = new_password + '_gp_' + salt
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()

        post = {"$set": {}}
        post["$set"]["password"] = hashed_password
        post["$set"]["salt"] = salt

        db.users.update_one(query, post)
        return {
            'Success': True,
            'Msg': 'Update Success'
        }

    # User Fields About
    def get_user_fields(self, user_id):
        db, client = self.db_handler.connect()
        cursor = db.user_fields.aggregate([
            {"$match": {"user_id": user_id}},
            {"$addFields": {"field_obj_id": {"$toObjectId": "$field_id"}}},
            {"$lookup": {
                "from": "fields",
                "localField": "field_obj_id",
                "foreignField": "_id",
                "as": "fields"
            }},
            {"$project": {
                "_id": 1,
                "user_id": 1,
                "field_id": 1,
                "fields.name": 1,
                "fields.address": 1
            }}
        ])
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def get_user_fields_without_join(self, user_id=None, field_id=None):
        db, client = self.db_handler.connect()
        post = {}
        if user_id:
            post['user_id'] = str(user_id)
        if field_id:
            post['field_id'] = str(field_id)

        cursor = db.user_fields.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_user_fields(self, user_id, field_id):
        post = {
            'user_id': user_id,
            'field_id': field_id
        }

        db, client = self.db_handler.connect()
        db.user_fields.insert_one(post)
        cursor = db.user_fields.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_user_fields(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.user_fields.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    def delete_user_fields_by_user_id(self, id_list):
        db, client = self.db_handler.connect()

        db.user_fields.delete_many({'user_id': {'$in': id_list}})

        client.close()
        return None

    # Role About
    def get_roles(self, _id=None, name=None, enable=None, fields=None):
        post = {}
        if _id:
            post['_id'] = _id
        if name:
            post['name'] = {'$regex': name, '$options': '$i'}
        if enable is not None:
            post['enable'] = enable
        if type(fields) is str:
            post['field_id'] = fields
        elif type(fields) is list:
            post['field_id'] = {'$in': fields}

        db, client = self.db_handler.connect()
        cursor = db.roles.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_role(self, name, field_id, menu_item, enable=1):
        post = {'name': name, "field_id": field_id, "permission": menu_item}
        if enable is not None:
            post['enable'] = enable

        db, client = self.db_handler.connect()
        db.roles.insert_one(post)
        cursor = db.roles.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def update_role(self, _id, name=None, enable=None, menu_items=None):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if enable is not None:
            post["$set"]["enable"] = enable
        if menu_items is not None:
            post["$set"]["permission"] = menu_items

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.roles.update_one(query, post)

        cursor = db.roles.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_role(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.roles.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    # User Roles About
    def get_user_roles(self, user_id):
        db, client = self.db_handler.connect()
        cursor = db.user_roles.aggregate([
            {"$match": {"user_id": user_id}},
            {"$addFields": {"role_id_object": {"$toObjectId": "$role_id"}}},
            {"$lookup": {
                "from": "roles",
                "let": {"role_id": "$role_id_object"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {
                                        "$eq": ["$_id", "$$role_id"]
                                    },
                                    {
                                        "$eq": ["$enable", 1]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "as": "roles"
            }},
            {"$project": {
                "_id": 1,
                "user_id": 1,
                "role_id": 1,
                "roles.name": 1
            }}
        ])
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def get_user_roles_by_field(self, user_id, field_id):
        db, client = self.db_handler.connect()
        cursor = db.user_roles.aggregate([
            {"$match": {"user_id": user_id}},
            {"$addFields": {"role_id_object": {"$toObjectId": "$role_id"}}},
            {"$lookup": {
                "from": "roles",
                "let": {"role_id": "$role_id_object"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {
                                        "$eq": ["$_id", "$$role_id"]
                                    },
                                    {
                                        "$eq": ["$enable", 1]
                                    },
                                    {
                                        "$eq": ["$field_id", field_id]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "as": "roles"
            }},
            {"$project": {
                "_id": 1,
                "user_id": 1,
                "role_id": 1,
                "roles.permission": 1
            }}
        ])
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_user_roles(self, user_id, role_id):
        post = {
            'user_id': user_id,
            'role_id': role_id
        }
        db, client = self.db_handler.connect()
        db.user_roles.insert_one(post)
        cursor = db.user_roles.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_user_roles(self, id_list, user_id=None, field_id=None):
        db, client = self.db_handler.connect()

        if id_list is not None:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.user_roles.delete_many({'_id': {'$in': delete_list}})

        if user_id is not None and field_id is not None:
            # get field role
            curser = db.roles.find({"field_id": field_id})
            role_df = pd.DataFrame(list(curser))
            role_id_list = list()
            if not role_df.empty:
                role_id_list = role_df['_id'].tolist()

            if role_id_list:
                del_filter = {
                    "user_id": user_id,
                    "role_id": {
                        "$in":  [str(uid) for uid in role_id_list]
                    }
                }
                db.user_roles.delete_many(del_filter)
        else:
            raise Exception("post data is empty.")

        try:
            client.close()
        except Exception:
            pass
        return None

    def delete_user_roles_by_role_id(self, role_id):
        db, client = self.db_handler.connect()
        db.user_roles.delete_many({'role_id': role_id})
        client.close()
        return None

    def delete_user_roles_by_user_id(self, user_id):
        db, client = self.db_handler.connect()
        db.user_roles.delete_many({'user_id': {'$in': user_id}})
        client.close()
        return None

    def delete_user_fields_by_field_id(self, field_id):
        db, client = self.db_handler.connect()
        db.user_fields.delete_many({'field_id': field_id})
        client.close()
        return None

    # cases
    def get_cases(self, _id=None, code=None, service=None, status=None, performance_level=None, company_id=None):
        post = {}
        if _id is not None:
            if type(_id) is list:
                case_id_list = [ObjectId(id) for id in _id]
                post["_id"] = {"$in": case_id_list}
            else:
                post["_id"] = ObjectId(_id)
        if code is not None:
            if type(code) is list:
                code_id_list = [code_id for code_id in code]
                post["code"] = {"$in": code_id_list}
            else:
                post["code"] = code
        if (company_id is not None) and (company_id != ""):
            post["company_id"] = ObjectId(company_id)
        if service:
            post["service"] = service
        if status is not None:
            post["status"] = status
        if performance_level:
            post["performance_level"] = performance_level
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.cases.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'company_id': np.str, 'user_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def get_cases_many(self, _id_list=None, code_list=None, service_list=None, status_list=None, performance_level_list=None, name_list= None):
        post = {}
        if _id_list is not None:
            post["_id"] = {"$in": list(map(ObjectId, _id_list))}
        if code_list is not None:
            post["code"] = {"$in": code_list}
        if service_list:
            post["service"] = {"$in": service_list}
        if status_list:
            post["status"] = {"$in": status_list}
        if performance_level_list:
            post["performance_level"] = {"$in": performance_level_list}
        if name_list:
            post["name"] = {"$in": name_list}
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.cases.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'company_id': np.str, 'user_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_cases(self, _id=None, code=None, service=None, status=None, performance_level=None, company_id=None, user_id=None, name=None, communication=None, implement=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code:
            post["code"] = code
        if service:
            post["service"] = service
        if status is not None:
            post["status"] = status
        if performance_level is not None:
            post["performance_level"] = performance_level
        if company_id is not None:
            post["company_id"] = ObjectId(company_id) if company_id else ""
        if user_id is not None:
            post["user_id"] = ObjectId(user_id) if user_id else ""
        if name:
            post["name"] = name
        if communication:
            post["communication"] = communication
        if implement:
            post["implement"] = implement

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.cases.insert_one(post)
            cursor = db.cases.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
                if 'company_id' in pd_data.columns:
                    pd_data = pd_data.astype({'company_id': np.str})
                if 'user_id' in pd_data.columns:
                    pd_data = pd_data.astype({'user_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_cases(self, _id, code=None, service=None, status=None, performance_level=None, company_id=None, user_id=None, name=None, communication=None, implement=None):
        post = {"$set": {}}
        if code is not None:
            post["$set"]["code"] = code
        if service:
            post["$set"]["service"] = service
        if status is not None:
            post["$set"]["status"] = status
        if performance_level is not None:
            post["$set"]["performance_level"] = performance_level
        if company_id is not None:
            post["$set"]["company_id"] = ObjectId(company_id) if company_id else ""
        if user_id is not None:
            post["$set"]["user_id"] = ObjectId(user_id) if user_id else ""
        if name:
            post["$set"]["name"] = name
        if communication:
            post["$set"]["communication"] = communication
        if implement:
            post["$set"]["implement"] = implement

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.cases.update_one(query, post)

            cursor = db.cases.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
                if 'company_id' in pd_data.columns:
                    pd_data = pd_data.astype({'company_id': np.str})
                if 'user_id' in pd_data.columns:
                    pd_data = pd_data.astype({'user_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_cases(self, id_list):
        db, client = self.db_handler.connect()

        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))
            db.cases.delete_many({'_id': {'$in': delete_list}})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # resources
    def get_resources(self, _id=None, code=None, equipment_type=None, name=None, capacity=None, communication=None,
                      implement=None, field_id=None, case_id=None, **kwargs):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code:
            post["code"] = code
        if equipment_type:
            post["equipment_type"] = equipment_type
        if name:
            post["name"] = {'$regex': name, '$options': '$i'}
        if capacity:
            post["capacity"] = capacity
        if communication:
            post["communication"] = communication
        if implement:
            post["implement"] = implement
        if field_id is not None:
            if type(field_id) is list:
                field_id_list = [ObjectId(field) for field in field_id]
                post["field_id"] = {"$in": field_id_list}
            else:
                post["field_id"] = ObjectId(field_id)
        if case_id is not None:
            if type(case_id) is list:
                case_id_list = [ObjectId(case) for case in case_id]
                post["case_id"] = {"$in": case_id_list}
            else:
                post["case_id"] = ObjectId(case_id)

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(uid) for uid in allow_field]
            post['field_id'] = {"$in": allow_field}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.resources.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def get_resources_many(self, _id_list=None, code_list=None, field_id_list=None, case_id_list=None):
        post = {}
        if _id_list:
            post["_id"] = {"$in": list(map(ObjectId, _id_list))}
        if code_list is not None:
            post["code"] = {"$in": code_list}
        if field_id_list:
            post["field_id"] = {"$in": list(map(ObjectId, field_id_list))}
        if case_id_list is not None:
            post["case_id"] = {"$in": list(map(ObjectId, case_id_list))}
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.resources.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_resources(self, _id=None, code=None, equipment_type=None, name=None, capacity=None, communication=None, implement=None, field_id=None, case_id=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code:
            post["code"] = code
        if equipment_type:
            post["equipment_type"] = equipment_type
        if name:
            post["name"] = name
        if capacity:
            post["capacity"] = capacity
        if communication:
            post["communication"] = communication
        if implement:
            post["implement"] = implement
        if field_id:
            post["field_id"] = ObjectId(field_id)
        if case_id:
            post["case_id"] = ObjectId(case_id)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.resources.insert_one(post)
            cursor = db.resources.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_resources(self, _id, code=None, equipment_type=None, name=None, capacity=None, communication=None, implement=None, field_id=None, case_id=None):
        post = {"$set": {}}
        if code:
            post["$set"]["code"] = code
        if equipment_type:
            post["$set"]["equipment_type"] = equipment_type
        if name:
            post["$set"]["name"] = name
        if capacity is not None:
            post["$set"]["capacity"] = capacity
        if communication:
            post["$set"]["communication"] = communication
        if implement:
            post["$set"]["implement"] = implement
        if field_id:
            post["$set"]["field_id"] = ObjectId(field_id)
        if case_id:
            post["$set"]["case_id"] = ObjectId(case_id)

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.resources.update_one(query, post)

            cursor = db.resources.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str, 'case_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_resources(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.resources.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    def single_sign_on(self, user_id, field_id):
        post = {'user_id': user_id, 'field_id': field_id}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.user_fields.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    # Announcement
    def get_announcement(self, _id=None, start_time=None, end_time=None, fields=None, content=None, file=None,
                         minetype=None, filename=None, createon=None, **kwargs):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if start_time and end_time:
            post["eventon"] = {
                    "$gte": start_time,
                    "$lte": end_time
            }
        if createon:
            post["createon"] = createon
        if fields:
            post["fields"] = fields
        if content:
            post["content"] = {'$regex': content}
        if file:
            post["file"] = file
        if minetype:
            post["minetype"] = minetype
        if filename:
            post["filename"] = filename

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [uid for uid in allow_field]
            post['fields'] = {"$in": allow_field}

        db, client = self.db_handler.connect()
        cursor = db.announcement.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str, 'fields': np.str})
        client.close()
        return pd_data

    def create_announcement(self, _id=None, createon=None, eventon=None, fields=None, content=None, file=None,
                            minetype=None, filename=None, field_name=None):
        post = {}
        post["_id"] = ObjectId(_id)
        post["fields"] = fields
        post["content"] = content
        post["file"] = file
        post["minetype"] = minetype
        post["filename"] = filename
        post["createon"] = createon
        post["eventon"] = eventon
        post["field_name"] = field_name

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.announcement.insert_one(post)
            cursor = db.announcement.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_announcement(self, _id,  createon=None, eventon=None, fields=None, content=None, file=None,
                            minetype=None, filename=None, field_name=None):
        post = {"$set": {}}
        if createon:
            post["$set"]["createon"] = createon
        if eventon:
            post["$set"]["eventon"] = eventon
        if fields:
            post["$set"]["fields"] = fields
        if content:
            post["$set"]["content"] = content

        post["$set"]["file"] = file
        post["$set"]["minetype"] = minetype
        post["$set"]["filename"] = filename
        post["$set"]["field_name"] = field_name

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.announcement.update_one(query, post)

        cursor = db.announcement.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})

        client.close()
        return pd_data

    def delete_announcement(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.announcement.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    def get_implement_report_replenish_many(
            self, _id_list=None, case_id_list=None, case_code_list=None, service_list=None, date_time_list=None,
            time_list=None):
        post = {}
        if _id_list:
            post["_id"] = {"$in": list(map(ObjectId, _id_list))}
        if case_id_list is not None:
            post["case_id"] = {"$in": list(map(ObjectId, case_id_list))}
        if case_code_list:
            post["case_code"] = {"$in": case_code_list}
        if service_list:
            post["service"] = {"$in": service_list}
        if date_time_list:
            post["datetime"] = {"$in": date_time_list}
        if time_list:
            post["time"] = {"$in": time_list}
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.implement_report_replenish.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'case_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    # get solar execution
    def get_solar_execution(self, _id=None, equipment=None, sdate=None, edate=None, power=None):
        post = {}
        if sdate:
            post = {
                "datetime": {
                    "$gte": datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S'),
                    "$lte": datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
                }
            }
        if _id:
            post["_id"] = ObjectId(_id)
        if equipment:
            post["equipment"] = equipment
        if power:
            post["power"] = power

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.solar_execution.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def get_user_permission(self, user_id):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            curser = db.user_roles.find({'user_id': user_id})
            pd_data = pd.DataFrame(list(curser))
            if not pd_data.empty:
                role_id_list = pd_data['role_id'].tolist()
                curser = db.role_permission.find({'role_id': {'$in': role_id_list}})
                pd_data = pd.DataFrame(list(curser))
                if not pd_data.empty:
                    pd_data.drop('_id', inplace=True, axis=1)
                    pd_data.drop('role_id', inplace=True, axis=1)
                    pd_data = pd_data.groupby('api_name').aggregate('max')
                    pd_data = pd_data.reset_index(drop=False)
        except Exception as e:
            self.logger.error(repr(e))
        finally:
            client.close()
        return pd_data

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

    def read(self, criteria, **kwargs):
        db, client = self.db_handler.connect()
        sort = kwargs.get('sort')
        limit = kwargs.get('limit')
        collection = kwargs.get('collection')
        collection = db[collection]
        rtn_data = None
        try:
            if sort and limit is not None:
                rtn_data = collection.find(criteria).sort(sort).limit(limit)
            elif sort and limit is None:
                rtn_data = collection.find(criteria).sort(sort)
            elif not sort and limit is not None:
                rtn_data = collection.find(criteria).limit(limit)
            else:
                rtn_data = collection.find(criteria)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            # self.logger.info('close mongodb client')
            client.close()
            return rtn_data

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

    # System setting
    def get_system_setting(self, _id=None, key=None, value=None, is_system=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if key:
            post["key"] = key
        if value:
            post["value"] = value
        if is_system is not None:
            post["is_system"] = is_system

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.system_settings.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_system_setting(self, _id, value=None):
        post = {"$set": {}}
        db, client = self.db_handler.connect()
        try:
            if value is not None:
                post["$set"]["value"] = value
            query = {'_id': ObjectId(_id)}

            db.system_settings.update_one(query, post)
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()

    def get_pcs_setting(self, _id=None, equipment_type=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if equipment_type:
            post["equipment_type"] = equipment_type

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.equipments.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    # Custom protect setting
    def get_custom_protect(self, _id=None, key=None, value=None):
        post = {}

        if _id:
            post['_id'] = {'$in': [ObjectId(_id)]}
        if key:
            post["key"] = key
        if value:
            post["value"] = value

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.custom_protect.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return pd_data

    def update_custom_protect(self, _id, value=None):
        post = {"$set": {}}
        db, client = self.db_handler.connect()

        try:
            if value is not None:
                post["$set"]["value"] = float(value)

            query = {'_id': ObjectId(_id)}
            db.custom_protect.update_one(query, post)
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()

    # electric_schedule
    def get_electric_schedule(self, _id=None, name=None, memo=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if name is not None:
            post["name"] = {'$regex': name, '$options': '$i'}
        if memo is not None:
            post["memo"] = {'$regex': memo, '$options': '$i'}

        db, client = self.db_handler.connect()
        cursor = db.electric_schedule.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def create_electric_schedule(self, _id=None, name=None, memo=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        post["name"] = name
        post["memo"] = memo

        db, client = self.db_handler.connect()
        db.electric_schedule.insert_one(post)
        cursor = db.electric_schedule.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def update_electric_schedule(self, _id, name=None, memo=None):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if memo is not None:
            post["$set"]["memo"] = memo

        query = {'_id': ObjectId(_id)}
        db, client = self.db_handler.connect()
        db.electric_schedule.update_one(query, post)
        cursor = db.electric_schedule.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_electric_schedule(self, id_list):
        db, client = self.db_handler.connect()
        delete_list = list(map(ObjectId, id_list))
        if delete_list:
            db.electric_schedule.delete_many({'_id': {'$in': delete_list}})
            client.close()
        return None

    # electric_schedule_detail
    def get_electric_schedule_detail(
            self, parent_id, _id=None, week=None, start_time=None, end_time=None, _type=None, soc=None):
        post = {'parent_id': parent_id}
        if _id:
            post["_id"] = ObjectId(_id)
        if week:
            post["week"] = week
        if start_time:
            post["start_time"] = {
                    "$gte": start_time,
            }
        if end_time:
            post["end_time"] = {
                    "$lte": end_time
            }
        if _type:
            post["type"] = _type
        if soc:
            post["soc"] = soc

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.electric_schedule_detail.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_electric_schedule_detail(
            self, parent_id, _id=None, week=None, start_time=None, end_time=None, _type=None, soc=None, kw=None):
        post = {'parent_id': parent_id}
        if _id:
            post["_id"] = ObjectId(_id)
        post["week"] = week
        post["start_time"] = start_time
        post["end_time"] = end_time
        post["type"] = _type
        post["soc"] = soc
        post["kw"] = kw

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.electric_schedule_detail.insert_one(post)
            cursor = db.electric_schedule_detail.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_electric_schedule_detail(
            self, _id, week=None, start_time=None, end_time=None, _type=None, soc=None, kw=None):
        post = {"$set": {}}
        if week:
            post["$set"]["week"] = week
        if start_time:
            post["$set"]["start_time"] = start_time
        if end_time:
            post["$set"]["end_time"] = end_time
        if _type is not None:
            post["$set"]["type"] = int(_type)
        if soc is not None:
            post["$set"]["soc"] = int(soc)
        if kw is not None:
            post["$set"]["kw"] = int(kw)
        else:
            post["$set"]["kw"] = None

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.electric_schedule_detail.update_one(query, post)

        cursor = db.electric_schedule_detail.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_electric_schedule_detail(self, id_list):
        db, client = self.db_handler.connect()
        delete_list = list(map(ObjectId, id_list))
        if delete_list:
            db.electric_schedule_detail.delete_many({'_id': {'$in': delete_list}})
            client.close()
        return None

    def delete_electric_schedule_detail_by_parent(self, parent_id):
        db, client = self.db_handler.connect()
        db.electric_schedule_detail.delete_many({'parent_id': parent_id})
        client.close()
        return None

    # Electric setting
    def get_electric_setting(self, _id=None, version=None, enable=None, volt_type=None, time_step=None, json_data=None,
                             set_value=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if version:
            post["version"] = int(version)
        if enable:
            post["enable"] = int(enable)
        if volt_type:
            post["volt_type"] = volt_type
        if time_step:
            post["time_step"] = time_step
        if json_data:
            post["json_data"] = json_data
        if set_value:
            post["set"] = int(set_value)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.electric_settings.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_electric_setting(self, _id):
        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.electric_settings.update_many({'set': 1}, {'$set': {'set': 0}})
        db.electric_settings.update_many(query, {'$set': {'set': 1}})

        cursor = db.electric_settings.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def update_electric_price(self, df):
        try:
            db, client = self.db_handler.connect()
            records = json.loads(df.T.to_json()).values()
            for row in records:
                row['week'] = row['week']
                row['is_summer'] = int(row['is_summer'])
                row['start_time'] = row['start_time']
                row['end_time'] = row['end_time']
                row['price'] = np.float64(row['price'])
            db.electric_price.insert_many(records)
            return 'Success'
        except Exception as e:
            return str(e)

    def del_electric_price(self):
        db, client = self.db_handler.connect()
        try:
            db.electric_price.delete_many({})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    def get_electric_report(self, start_date=None, end_date=None):
        post = {
            "start_date": {
                "$gte": datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S'),
            },
            "end_date": {
                "$lte": datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S'),
            }
        }
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.electric_report.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    # Step scenario
    def get_step_scenario(self, _id=None, code=None, name=None, step_second=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code:
            post["code"] = code
        if name:
            post["name"] = name
        if step_second:
            post["step_second"] = int(step_second)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.step_scenario.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_step_scenario(self, _id=None, code=None, name=None, data=None, step_second=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        post["code"] = code
        post["name"] = name
        post["data"] = data
        post["step_second"] = int(step_second)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.step_scenario.insert_one(post)
            cursor = db.step_scenario.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_step_scenario(self, _id=None, code=None, name=None, data=None, step_second=None):
        post = {"$set": {}}
        if code:
            post["$set"]["code"] = code
        if name:
            post["$set"]["name"] = name
        if data:
            post["$set"]["data"] = data
        if step_second:
            post["$set"]["step_second"] = int(step_second)

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.step_scenario.update_one(query, post)

        cursor = db.step_scenario.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_step_scenario(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.step_scenario.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    # System resource
    def get_system_equipment(self, _id=None, parent_id=None, case_id=None, field_id=None, code=None,
                             equipment_type=None, name=None, brand=None, ip=None, port=None, capacity=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if parent_id:
            post["parent_id"] = parent_id
        if case_id:
            post["case_id"] = ObjectId(case_id)
        if field_id:
            if type(field_id) is list:
                field_id_list = [ObjectId(field) for field in field_id]
                post["field_id"] = {"$in": field_id_list}
            else:
                post["field_id"] = ObjectId(field_id)
        if code:
            post["code"] = code
        if equipment_type:
            post["equipment_type"] = int(equipment_type)
        if name:
            post["name"] = name
        if brand:
            post["brand"] = brand
        if ip:
            post["ip"] = ip
        if port:
            post["port"] = port
        if capacity:
            post["capacity"] = capacity

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.equipments.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'parent_id': np.str, 'case_id': np.str, 'field_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_system_equipment(self, _id=None, parent_id=None, case_id=None, field_id=None, code=None,
                                equipment_type=None, name=None, brand=None, ip=None, port=None, capacity=None,
                                base_address=None, unit_id=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        post["parent_id"] = parent_id
        post["case_id"] = ObjectId(case_id)
        post["field_id"] = ObjectId(field_id)
        post["code"] = code
        if equipment_type is not None:
            post["equipment_type"] = int(equipment_type)
        post["name"] = name
        post["brand"] = brand
        post["ip"] = ip
        if port:
            post["port"] = int(port)
        post["capacity"] = capacity
        if base_address:
            post["base_address"] = int(base_address)
        if unit_id:
            post["unit_id"] = int(unit_id)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.equipments.insert_one(post)
            cursor = db.equipments.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'parent_id': np.str, 'case_id': np.str, 'field_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_system_equipment(self, _id=None, parent_id=None, case_id=None, field_id=None, code=None,
                                equipment_type=None, name=None, brand=None, ip=None, port=None, capacity=None,
                                unit_id=None):
        post = {"$set": {}}
        if parent_id:
            post["$set"]["parent_id"] = parent_id
        if case_id:
            post["$set"]["case_id"] = ObjectId(case_id)
        if field_id:
            post["$set"]["field_id"] = ObjectId(field_id)
        if code:
            post["$set"]["code"] = code
        if equipment_type:
            post["$set"]["equipment_type"] = int(equipment_type)
        if name:
            post["$set"]["name"] = name
        if brand:
            post["$set"]["brand"] = brand
        if ip:
            post["$set"]["ip"] = ip
        if port:
            post["$set"]["port"] = int(port)
        if capacity:
            post["$set"]["capacity"] = int(capacity)
        if unit_id:
            post["$set"]["unit_id"] = int(unit_id)

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.equipments.update_one(query, post)

        cursor = db.equipments.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str, 'parent_id': np.str, 'case_id': np.str, 'field_id': np.str})
        client.close()
        return pd_data

    def delete_system_equipment(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.equipments.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    def get_local_cases(self, _id=None, code=None, service=None, service_code=None):
        post = {}
        if _id is not None:
            if type(_id) is list:
                case_id_list = [ObjectId(id) for id in _id]
                post["_id"] = {"$in": case_id_list}
            else:
                post["_id"] = ObjectId(_id)
        if code is not None:
            if type(code) is list:
                code_id_list = [code_id for code_id in code]
                post["code"] = {"$in": code_id_list}
            else:
                post["code"] = code
        if service:
            post["service"] = service
        if service_code is not None:
            post["service_code"] = service_code

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.cases.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_local_equipments(self, df):
        try:
            db, client = self.db_handler.connect()
            records = json.loads(df.T.to_json()).values()
            for row in records:
                row['_id'] = ObjectId(row['_id'])
                row['parent_id'] = row['parent_id']
                row['case_id'] = row['case_id']
                row['field_id'] = row['field_id']
                row['code'] = row['code']
                row['equipment_type'] = int(row['equipment_type'])
                row['name'] = row['name']
                row['brand'] = row['brand']
                row['ip'] = row['ip']
                row['port'] = None if row['port'] == '' else int(row['port'])
                row['capacity'] = None if row['capacity'] == '' else np.float(row['capacity'])
            db.equipments.insert_many(records)
            return 'Success'
        except Exception as e:
            return str(e)

    def del_local_equipment(self):
        db, client = self.db_handler.connect()
        try:
            db.equipments.delete_many({})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # scenario schedule
    def get_scenario_schedule(self, _id=None, case_id=None, scenario_id=None, start_time=None, end_time=None,
                              repeat=None):
        post = {
        }
        if start_time:
            post["start_time"] =  {"$gte": datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')}

        if end_time:
            post["end_time"] =  {"$lte": datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')}

        if _id:
            post["_id"] = ObjectId(_id)
        if case_id:
            post["case_id"] = case_id
        if scenario_id:
            post["scenario_id"] = scenario_id
        if repeat:
            post["repeat"] = bool(repeat)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.scenario_schedule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_scenario_schedule(self, _id=None, case_id=None, scenario_id=None, start_time=None, end_time=None,
                                 repeat=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        post["case_id"] = case_id
        post["scenario_id"] = scenario_id
        post["start_time"] = datetime.datetime.strptime(start_time, "%Y%m%d%H%M%S")
        post["end_time"] = datetime.datetime.strptime(end_time, "%Y%m%d%H%M%S")
        post["repeat"] = bool(repeat)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.scenario_schedule.insert_one(post)
            cursor = db.scenario_schedule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_scenario_schedule(self, _id=None, case_id=None, scenario_id=None, start_time=None, end_time=None,
                                 repeat=None):
        post = {"$set": {}}
        if case_id:
            post["$set"]["case_id"] = case_id
        if scenario_id:
            post["$set"]["scenario_id"] = scenario_id
        if start_time:
            post["$set"]["start_time"] = datetime.datetime.strptime(start_time, "%Y%m%d%H%M%S")
        if end_time:
            post["$set"]["end_time"] = datetime.datetime.strptime(end_time, "%Y%m%d%H%M%S")
        if repeat is not None:
            post["$set"]["repeat"] = bool(repeat)

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        db.scenario_schedule.update_one(query, post)

        cursor = db.scenario_schedule.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def delete_scenario_schedule(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.scenario_schedule.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None

    def get_control_equipment(self, code, _id=None):
        post = {'code': code}
        if _id:
            post["_id"] = ObjectId(_id)
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.equipments.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str, 'field_id': np.str})
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return pd_data

    def get_essci(self, essci_key=None):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            post_data = {}
            if essci_key:
                post_data['essci_key'] = essci_key
            cursor = db.essci.find(post_data).sort('data_time', -1).limit(120)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.sort_values('data_time', ascending=True)
                pd_data = pd_data.astype({'_id': str})
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return pd_data

    def mod_lc_control_state(self, action, status=None, msg=None):
        db, client = self.db_handler.connect()
        data = None
        try:
            if action == 'get':
                data = db.lc_control_state.find_one()
                data['_id'] = str(data['_id'])
            elif action == 'delete':
                db.lc_control_state.remove({})
            elif action == 'upsert':
                db.lc_control_state.update(
                    {}, {'$set': {'datetime': datetime.datetime.now(), 'status': status, 'message': msg}}, upsert=True)
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return data

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
        return data['system_status'] if data is not None else None

    def upsert_working_status(self, status):
        db, client = self.db_handler.connect()
        try:
            # 先取回原本的狀態，狀態不一樣在變動
            _status = self.get_working_status()
            if _status is None or _status != status:
                db.working_status.update_one(
                    {}, {'$set': {'system_status': status, 'update_time': datetime.datetime.now()}}, upsert=True)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def get_meter_export(self, start_date, end_date):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            post_data = {
                'execute_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            cursor = db.meter_export.find(post_data)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.sort_values('execute_date', ascending=True)
                pd_data = pd_data.astype({'_id': str})
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return pd_data

    def write_modbus_logs(self, user_info, collection, value, old_value=None):
        post = {
            "date": datetime.datetime.now(),
            "collection": collection,
            "action": 'update',
            "old_value": old_value,
            "new_value": value,
            "modified_on": datetime.datetime.now(),
            "modified_by": user_info.user_id,
            "modified_name": user_info.user_name
        }

        db, client = self.db_handler.connect()
        try:
            db.system_logs.insert_one(post)
        except Exception as e:
            message = repr(e)
        finally:
            client.close()

    def update_fire_main_status(self, value):
        db, client = self.db_handler.connect()
        try:
            criteria = {
                "key": "fire_main_switch",
                "is_system": False
            }
            db.system_settings.update(criteria, {"$set": {"value": value}}, upsert=True)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()

    def get_taipower_holidays(self, year):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            post_data = {
                'year': str(year)
            }
            cursor = db.taipower_holidays.find(post_data)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return pd_data

    def delete_taipower_holidays(self, year):
        db, client = self.db_handler.connect()
        db.taipower_holidays.delete_many({'year': str(year)})
        client.close()
        return None

    def create_taipower_holidays(self, year, date_list):
        post = dict()
        post["year"] = str(year)
        post["holidays"] = date_list

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.taipower_holidays.insert_one(post)
            cursor = db.scenario_schedule.find({'year': year})
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def check_today_is_taipower_holiday(self, current_date: datetime.datetime):
        db, client = self.db_handler.connect()
        try:
            post_data = {
                'year': str(current_date.year)
            }
            cursor = db.taipower_holidays.find(post_data)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                cd = datetime.datetime.strftime(current_date, '%Y-%m-%d')
                holidays = pd_data.iloc[0]['holidays']
                return cd in holidays
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return False

    def get_electricity_price(self, _id=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.electricity_settings.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            self.logger.error(e)
        finally:
            client.close()
        return pd_data

    def update_electricity_price(self, _id, is_set=None, data=None):
        post = {"$set": {}}
        if is_set is not None:
            post["$set"]["is_set"] = int(is_set)
        if data is not None:
            post["$set"]["data"] = data
        query = {'_id': ObjectId(_id)}
        db, client = self.db_handler.connect()
        db.electricity_settings.update_one(query, post)

        cursor = db.electricity_settings.find(query)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': np.str})
        client.close()
        return pd_data

    def clear_electricity_price_set(self):
        query = {}
        post = {'$set': {'is_set': int(0)}}
        db, client = self.db_handler.connect()
        db.electricity_settings.update_many(query, post)
        client.close()

    # Notify_token
    def get_notify_token(self, _id=None, name=None, token=None, **kwargs):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if name:
            post["name"] = {'$regex': name, '$options': '$i'}
        if token:
            post["token"] = token

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.line_notify_token.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'name': str, 'token': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_notify_token(self, _id=None, name=None, token=None, **kwargs):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if name is not None:
            post["name"] = name
        if token is not None:
            post["token"] = token

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(_id) for _id in allow_field]
            post['_id'] = {"$in": allow_field}

        try:
            db.line_notify_token.insert_one(post)
            cursor = db.line_notify_token.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'token' in pd_data.columns:
                    pd_data = pd_data.astype({'token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_notify_token(self, _id=None, name=None, token=None, **kwargs):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if token is not None:
            post["$set"]["token"] = token

        query = {'_id': ObjectId(_id)}

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(_id) for _id in allow_field]
            post['_id'] = {"$in": allow_field}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.line_notify_token.update(query, post)

            cursor = db.line_notify_token.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'token' in pd_data.columns:
                    pd_data = pd_data.astype({'token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_notify_token(self, id_list):
        db, client = self.db_handler.connect()

        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.line_notify_token.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # notify_rule
    def get_notify_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if code:
            post["code"] = code
        if name is not None:
            post["name"] = {'$regex': name, '$options': '$i'}
        if description:
            post["description"] = description

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.line_notify_rule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'name': str, 'code': str, 'description': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_notify_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code is not None:
            post["code"] = code
        if name is not None:
            post["name"] = name
        if description is not None:
            post["description"] = description

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.line_notify_rule.insert_one(post)

            cursor = db.line_notify_rule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'code' in pd_data.columns:
                    pd_data = pd_data.astype({'code': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'description' in pd_data.columns:
                    pd_data = pd_data.astype({'description': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_notify_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {"$set": {}}

        if code is not None:
            post["$set"]["code"] = code
        if name is not None:
            post["$set"]["name"] = name
        if description is not None:
            post["$set"]["description"] = description

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        # pd_data = pd.DataFrame()
        try:
            db.line_notify_rule.update_one(query, post)

            cursor = db.line_notify_rule.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'code' in pd_data.columns:
                    pd_data = pd_data.astype({'code': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'description' in pd_data.columns:
                    pd_data = pd_data.astype({'description': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_notify_rule(self, id_list):
        db, client = self.db_handler.connect()

        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.line_notify_rule.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # notify_setting
    def get_notify_setting(self, _id=None, notify_rule=None, notify_token=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()

        try:
            cursor = db.line_notify_setting.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'notify_rule' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_rule': str})
                if 'notify_token' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_notify_setting(self, _id=None, notify_rule=None, notify_token=None):

        post = {}
        if _id:
            post["_id"] = ObjectId(_id)

        if notify_rule is not None:
            post["notify_rule"] = ObjectId(notify_rule)

        if notify_token is not None:
            post["notify_token"] = ObjectId(notify_token)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.line_notify_setting.insert_one(post)
            cursor = db.line_notify_setting.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'notify_rule' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_rule': str})
                if 'notify_token' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_notify_setting(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))
            db.line_notify_setting.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # Notify_log
    def get_notify_log(self, _id=None, sdate=str, edate=str, notify_rule=None, notify_token=None,
                       notify_setting=None, success=None, message=None, fail_message=None, **kwargs):
        post = {}
        if sdate and edate:
            if isinstance(sdate, str):
                sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
            if isinstance(edate, str):
                edate = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            post = {
                "datetime": {
                    "$gte": sdate,
                    "$lte": edate
                }
            }
        if notify_setting is not None:
            if type(notify_setting) is list:
                notify_id_list = [ObjectId(uid) for uid in notify_setting]
                post['notify_setting'] = {'$in': notify_id_list}
            else:
                post['notify_setting'] = {'$in': [ObjectId(notify_setting)]}
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)
        if success is not None:
            post["success"] = success
        if message:
            post["message"] = message
        if fail_message:
            post["fail_message"] = fail_message

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.line_notify_log.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'datetime': str})
                if 'notify_setting' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_setting': str})
                if 'fail_message' in pd_data.columns:
                    pd_data = pd_data.astype({'fail_message': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_notify_log(self, _id=None, date_time=None, notify_setting=None, notify_rule=None, notify_token=None, subject=None, message=None, success=None, fail_message=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if date_time:
            if isinstance(date_time, str):
                post["datetime"] = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
            else:
                post["datetime"] = date_time
        if notify_setting:
            post["notify_setting"] = ObjectId(notify_setting)
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)
        if subject:
            post["subject"] = subject
        if message:
            post["message"] = message
        if success is not None:
            post["success"] = success
        if fail_message:
            post["fail_message"] = fail_message

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.notify_log.insert_one(post)
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def read_operation_mode(self):
        operation_mode = None
        db, client = self.db_handler.connect()
        try:
            operation_mode = db.operation_mode.find_one()
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return operation_mode

    def update_operation_mode(self, operation_mode, operator):
        db, client = self.db_handler.connect()
        try:
            db.operation_mode.update_many({}, {'$set': {
                'mode': int(operation_mode),
                'update_user': operator,
                'update_time': datetime.datetime.now()
            }})

            operation_mode = db.operation_mode.find_one()
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return operation_mode

    def get_electric_price(self, is_sum, price_level):
        db, client = self.db_handler.connect()
        try:
            query = {'is_summer': is_sum}
            if price_level is not None:
                if isinstance(price_level, list):
                    query['price_level'] = {'$in': price_level}
                else:
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

    def get_async_export_data(self, user_id, equipment_id):
        post = {
            "creator.id": user_id
        }
        if type(equipment_id) is list:
            post['equipment_id'] = {'$in': equipment_id}
        else:
            post['equipment_id'] = equipment_id
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.export_data_async.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'datetime': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_async_export_data(self, equipment_id, start_date, end_date, creator):
        db, client = self.db_handler.connect()
        inserted_id = None
        try:
            post = {
                "equipment_id": equipment_id,
                "start_date": start_date,
                "end_date": end_date,
                "creator": creator,
                "export_data": None,
                "process_done": False,
                "process_msg": None
            }
            result = db.export_data_async.insert_one(post)
            inserted_id = result.inserted_id
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return inserted_id

    def update_async_export_data(self, _id, export_data, process_done, process_msg):
        db, client = self.db_handler.connect()
        try:
            db.export_data_async.update_one({'_id': _id}, {'$set': {
                'export_data': export_data,
                'process_done': process_done,
                'process_msg': process_msg
            }})
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()

    def delete_async_export(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))
            db.export_data_async.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    def get_power_control_settings(self):
        db, client = self.db_handler.connect()
        try:
            cursor = db.power_control_settings.find().sort('start_time', 1)
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

    def create_power_control_settings(self, start_time, end_time, kw):
        post = dict()
        post["start_time"] = str(start_time)
        post["end_time"] = str(end_time)
        post["kw"] = int(kw)
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            result = db.power_control_settings.insert_one(post)
            inserted_id = result.inserted_id
            cursor = db.power_control_settings.find({"_id": inserted_id})
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            print(str(e))
        finally:
            client.close()
        return pd_data

    def update_power_control_settings(self, _id, start_time, end_time, kw):
        db, client = self.db_handler.connect()
        pd_data = None
        try:
            db.power_control_settings.update_many({"_id": ObjectId(_id)}, {'$set': {
                'start_time': str(start_time),
                'end_time': str(end_time),
                'kw': int(kw)
            }})

            cursor = db.power_control_settings.find({"_id": ObjectId(_id)})
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': np.str})
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return pd_data

    def delete_power_control_settings(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))
            db.power_control_settings.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    def get_daily_report(
            self, year=None, month=None, day=None, start_date=None, end_date=None,
            order_field='date_time', order_type='asc', limit=10, offset=0, need_data_list=0):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if month is not None:
                post['month'] = month
            if day is not None:
                post['day'] = day
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            total_count = db.report_daily.find(post).count()
            if not need_data_list:
                cursor = db.report_daily \
                    .find(post, {'data_list': 0}).sort(order_field, 1 if order_type == 'asc' else -1).skip(
                    offset).limit(limit)
            else:
                cursor = db.report_daily \
                    .find(post).sort(order_field, 1 if order_type == 'asc' else -1)

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
        return {
            'total_count': total_count,
            'data': pd_data
        }

    def get_monthly_report(
            self, year=None, month=None, start_date=None, end_date=None,
            order_field='date_time', order_type='asc', limit=10, offset=0, need_data_list=0):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if month is not None:
                post['month'] = month
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            total_count = db.report_monthly.find(post).count()
            if not need_data_list:
                cursor = db.report_monthly \
                    .find(post, {'data_list': 0}).sort(order_field, 1 if order_type == 'asc' else -1).skip(
                    offset).limit(limit)
            else:
                cursor = db.report_monthly \
                    .find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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
        return {
            'total_count': total_count,
            'data': pd_data
        }

    def get_yearly_report(
            self, year=None, start_date=None, end_date=None,
            order_field='date_time', order_type='asc', limit=10, offset=0, need_data_list=0):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            total_count = db.report_yearly.find(post).count()
            if not need_data_list:
                cursor = db.report_yearly \
                    .find(post, {'data_list': 0}).sort(order_field, 1 if order_type == 'asc' else -1).skip(
                    offset).limit(limit)
            else:
                cursor = db.report_yearly \
                    .find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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
        return {
            'total_count': total_count,
            'data': pd_data
        }

    def export_daily_report(self, year, month, day):
        db, client = self.db_handler.connect()
        try:
            post = {
                'year': year,
                'month': month,
                'day': day
            }
            cursor = db.report_daily.find(post)
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

    def export_monthly_report(self, year, month):
        db, client = self.db_handler.connect()
        try:
            post = {
                'year': year,
                'month': month
            }
            cursor = db.report_monthly.find(post)
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

    def export_yearly_report(self, year):
        db, client = self.db_handler.connect()
        try:
            post = {
                'year': year,
            }
            cursor = db.report_yearly.find(post)
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

    def get_daily_report_sun(self, year=None, month=None, day=None, start_date=None, end_date=None,
                             order_field='date_time', order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if month is not None:
                post['month'] = month
            if day is not None:
                post['day'] = day
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_daily_sun.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_monthly_report_sun(self, year=None, start_month=None, end_month=None, start_date=None, end_date=None,
                               order_field='date_time', order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if start_month is not None:
                if 'month' not in post:
                    post['month'] = dict()
                post['month']['$gte'] = start_month
            if end_month is not None:
                if 'month' not in post:
                    post['month'] = dict()
                post['month']['$lte'] = end_month
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_monthly_sun.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_yearly_report_sun(self, year=None, start_date=None, end_date=None, order_field='date_time',
                              order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_yearly_sun.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_inverter(self, start_date=None, end_date=None, equipment_id=None, **kwargs):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if start_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$gte'] = start_date
            if end_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$lte'] = end_date
            if equipment_id is not None:
                post['equipment_id'] = equipment_id

            # 取得filter
            _filter = kwargs.get('filter', None)
            if _filter is not None:
                post.update(_filter)

            cursor = db.inverter.find(
                post, {'_id': -1, 'data_time': 1, 'equipment_id': 1, 'energy_total_kwh': 1, 'energy_today_kwh': 1,
                       'total_active_power': 1})\
                .sort('data_time', 1)
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

    def get_dcu(self, start_date=None, end_date=None, equipment_id=None, need_inverter=False, **kwargs):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if start_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$gte'] = start_date
            if end_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$lte'] = end_date
            if equipment_id is not None:
                post['equipment_id'] = equipment_id

            # 取得filter
            _filter: dict = kwargs.get('filter', {})
            if _filter is not None:
                post.update(_filter)

            find_col = {'_id': -1, 'data_time': 1, 'equipment_id': 1, 'ac_energy_kwh': 1}
            if need_inverter:
                find_col.update({'inverter_list': 1})

            cursor = db.dcu.find(post, find_col).sort('data_time', 1)
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

    def get_solar_exposure(self, start_date=None, end_date=None, **kwargs):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if start_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$gte'] = start_date
            if end_date is not None:
                if 'data_time' not in post:
                    post['data_time'] = dict()
                post['data_time']['$lte'] = end_date

            # 取得filter
            _filter = kwargs.get('filter', None)
            if _filter is not None:
                post.update(_filter)

            cursor = db.solar_exposure.find(
                post, {'_id': -1, 'data_time': 1, 'solar_exposure': 1})\
                .sort('data_time', 1)
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

    def get_diff_co2_coefficient(self):
        db, client = self.db_handler.connect()
        try:
            cursor = db.diff_co2_coefficient.find().sort('end_date', 1)
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

    def get_ems_daily_report(self, year=None, month=None, day=None, start_date=None, end_date=None,
                             order_field='date_time', order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if month is not None:
                post['month'] = month
            if day is not None:
                post['day'] = day
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_daily.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_ems_monthly_report(self, year=None, start_month=None, end_month=None, start_date=None, end_date=None,
                               order_field='date_time', order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if start_month is not None:
                if 'month' not in post:
                    post['month'] = dict()
                post['month']['$gte'] = start_month
            if end_month is not None:
                if 'month' not in post:
                    post['month'] = dict()
                post['month']['$lte'] = end_month
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_monthly.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_ems_yearly_report(self, year=None, start_date=None, end_date=None, order_field='date_time',
                              order_type='asc'):
        db, client = self.db_handler.connect()
        try:
            post = dict()
            if year is not None:
                post['year'] = year
            if start_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$gte'] = start_date
            if end_date is not None:
                if 'date_time' not in post:
                    post['date_time'] = dict()
                post['date_time']['$lte'] = end_date

            cursor = db.report_yearly.find(post).sort(order_field, 1 if order_type == 'asc' else -1)
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

    def get_won_bids(self, case_id):
        db, client = self.db_handler.connect()
        try:
            now = datetime.datetime.now()
            target_date = now.strftime('%Y%m%d')
            ctime = now.strftime('%H')
            criteria = {'status': 'close', 'case_id': case_id, 'datetime': target_date, 'time': ctime}
            target = db.cases_info.find_one(criteria)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return target

    def get_bid_abandon(self, case_id):
        db, client = self.db_handler.connect()
        try:
            current_time = datetime.datetime.now()
            criteria = {
                'case_id': case_id,
                'start_datetime': {"$lte": current_time},
                'end_datetime': {"$gte": current_time}
            }
            target = db.bid_abandon_transfer.find_one(criteria)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return target

    def get_case_dispatching(self, case_id) -> dict:
        rtn_data = {
            'dispatching': None,
            'recovering': None
        }
        db, client = self.db_handler.connect()
        try:
            current_time = datetime.datetime.now()
            criteria = {
                'case_id': case_id,
                '$or': [
                    {'mqtt_start_time': {"$lt": current_time}, 'mqtt_end_time': None},
                    {'mqtt_start_time': {"$lt": current_time}, 'mqtt_end_time': {"$gt": current_time}}
                ]
            }
            rtn_data['dispatching'] = db.case_dispatching.find_one(criteria)

            criteria = {
                'case_id': case_id,
                'mqtt_end_time': {"$lt": current_time},
                'recover_until_time': {"$gte": current_time}
            }
            rtn_data['recovering'] = db.case_dispatching.find_one(criteria)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return rtn_data

    def get_case(self):
        db, client = self.db_handler.connect()
        try:
            cursor = db.cases.find()
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

    def get_cbl(self, case_id):
        db, client = self.db_handler.connect()
        try:
            collection = f'sbspm_{case_id}'
            cursor = db[collection].find().sort('iso_date', -1)
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

    def token_update_user_otp(self, _id, iv=None, two_factor_secret_key=None, enable_two_factor=None,
                              temp_iv=None, temp_two_factor_secret_key=None):
        db, client = self.db_handler.connect()
        message = ''
        try:
            post = {"$set": {}}
            if iv is not None:
                post["$set"]["iv"] = iv if iv != '' else None
            if two_factor_secret_key is not None:
                post["$set"]["two_factor_secret_key"] = two_factor_secret_key if two_factor_secret_key != '' else None
            if enable_two_factor is not None:
                post["$set"]["enable_two_factor"] = enable_two_factor

            post["$set"]["temp_iv"] = temp_iv
            post["$set"]["temp_two_factor_secret_key"] = temp_two_factor_secret_key

            query = {'_id': ObjectId(_id)}
            db.users.update_one(query, post)
        except Exception as e:
            message = str(e)
            self.logger.error(str(e))
        finally:
            client.close()
        return message

    # Femc_msg_token
    def get_femc_msg_token(self, _id=None, name=None, token=None, **kwargs):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if name:
            post["name"] = {'$regex': name, '$options': '$i'}
        if token:
            post["token"] = token

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.femc_msg_token.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'name': str, 'token': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_femc_msg_token(self, _id=None, name=None, token=None, **kwargs):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if name is not None:
            post["name"] = name
        if token is not None:
            post["token"] = token

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(_id) for _id in allow_field]
            post['_id'] = {"$in": allow_field}

        try:
            db.femc_msg_token.insert_one(post)
            cursor = db.get_femc_msg_token.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'token' in pd_data.columns:
                    pd_data = pd_data.astype({'token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_femc_msg_token(self, _id=None, name=None, token=None, **kwargs):
        post = {"$set": {}}
        if name is not None:
            post["$set"]["name"] = name
        if token is not None:
            post["$set"]["token"] = token

        query = {'_id': ObjectId(_id)}

        allow_field = kwargs.get('allow_field')
        if allow_field is not None:
            allow_field = [ObjectId(_id) for _id in allow_field]
            post['_id'] = {"$in": allow_field}

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.femc_msg_token.update(query, post)

            cursor = db.get_femc_msg_token.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'token' in pd_data.columns:
                    pd_data = pd_data.astype({'token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_femc_msg_token(self, id_list):
        db, client = self.db_handler.connect()

        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.femc_msg_token.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # notify_rule
    def get_femc_msg_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}
        if code:
            post["code"] = code
        if name is not None:
            post["name"] = {'$regex': name, '$options': '$i'}
        if description:
            post["description"] = description

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.femc_msg_rule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'name': str, 'code': str, 'description': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_femc_msg_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if code is not None:
            post["code"] = code
        if name is not None:
            post["name"] = name
        if description is not None:
            post["description"] = description

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.femc_msg_rule.insert_one(post)

            cursor = db.femc_msg_rule.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'code' in pd_data.columns:
                    pd_data = pd_data.astype({'code': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'description' in pd_data.columns:
                    pd_data = pd_data.astype({'description': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def update_femc_msg_rule(self, _id=None, code=None, name=None, description=None, **kwargs):
        post = {"$set": {}}

        if code is not None:
            post["$set"]["code"] = code
        if name is not None:
            post["$set"]["name"] = name
        if description is not None:
            post["$set"]["description"] = description

        query = {'_id': ObjectId(_id)}

        db, client = self.db_handler.connect()
        try:
            db.femc_msg_rule.update_one(query, post)

            cursor = db.femc_msg_rule.find(query)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'code' in pd_data.columns:
                    pd_data = pd_data.astype({'code': str})
                if 'name' in pd_data.columns:
                    pd_data = pd_data.astype({'name': str})
                if 'description' in pd_data.columns:
                    pd_data = pd_data.astype({'description': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_femc_msg_rule(self, id_list):
        db, client = self.db_handler.connect()

        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))

            db.femc_msg_rule.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # notify_setting
    def get_femc_msg_setting(self, _id=None, notify_rule=None, notify_token=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()

        try:
            cursor = db.femc_msg_setting.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'notify_rule' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_rule': str})
                if 'notify_token' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_femc_msg_setting(self, _id=None, notify_rule=None, notify_token=None):

        post = {}
        if _id:
            post["_id"] = ObjectId(_id)

        if notify_rule is not None:
            post["notify_rule"] = ObjectId(notify_rule)

        if notify_token is not None:
            post["notify_token"] = ObjectId(notify_token)

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.femc_msg_setting.insert_one(post)
            cursor = db.femc_msg_setting.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str})
                if 'notify_rule' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_rule': str})
                if 'notify_token' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_token': str})
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def delete_femc_msg_setting(self, id_list):
        db, client = self.db_handler.connect()
        try:
            delete_list = []
            for _id in id_list:
                delete_list.append(ObjectId(_id))
            db.femc_msg_setting.delete_many({'_id': {'$in': delete_list}})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return None

    # Notify_log
    def get_femc_msg_log(self, _id=None, sdate=str, edate=str, notify_rule=None, notify_token=None,
                       notify_setting=None, success=None, message=None, fail_message=None, **kwargs):
        post = {}
        if sdate and edate:
            if isinstance(sdate, str):
                sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
            if isinstance(edate, str):
                edate = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
            post = {
                "datetime": {
                    "$gte": sdate,
                    "$lte": edate
                }
            }
        if notify_setting is not None:
            if type(notify_setting) is list:
                notify_id_list = [ObjectId(uid) for uid in notify_setting]
                post['notify_setting'] = {'$in': notify_id_list}
            else:
                post['notify_setting'] = {'$in': [ObjectId(notify_setting)]}
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)
        if success is not None:
            post["success"] = success
        if message:
            post["message"] = message
        if fail_message:
            post["fail_message"] = fail_message

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            cursor = db.femc_msg_log.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'datetime': str})
                if 'notify_setting' in pd_data.columns:
                    pd_data = pd_data.astype({'notify_setting': str})
                if 'fail_message' in pd_data.columns:
                    pd_data = pd_data.astype({'fail_message': str})
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def create_femc_msg_log(self, _id=None, date_time=None, notify_setting=None, notify_rule=None, notify_token=None, subject=None, message=None, success=None, fail_message=None):
        post = {}
        if _id:
            post["_id"] = ObjectId(_id)
        if date_time:
            if isinstance(date_time, str):
                post["datetime"] = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
            else:
                post["datetime"] = date_time
        if notify_setting:
            post["notify_setting"] = ObjectId(notify_setting)
        if notify_rule:
            post["notify_rule"] = ObjectId(notify_rule)
        if notify_token:
            post["notify_token"] = ObjectId(notify_token)
        if subject:
            post["subject"] = subject
        if message:
            post["message"] = message
        if success is not None:
            post["success"] = success
        if fail_message:
            post["fail_message"] = fail_message

        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()
        try:
            db.femc_msg_log.insert_one(post)
            message = ''
        except Exception as e:
            message = repr(e)
        finally:
            client.close()
        return pd_data

    def get_electricity_settings(self):
        db, client = self.db_handler.connect()
        try:
            post = {
                "is_set": int(1)
            }
            record = db.electricity_settings.find_one(post)
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            client.close()
        return record

    # Login Info
    def get_login_info(self, _id=None, login_account=None, ip_address=None):
        db, client = self.db_handler.connect()
        pd_data = pd.DataFrame()

        post = {}
        if _id:
            if type(_id) is list:
                _id_list = [ObjectId(uid) for uid in _id]
                post['_id'] = {'$in': _id_list}
            else:
                post['_id'] = {'$in': [ObjectId(_id)]}

        if login_account:
            post['login_account'] = {'$regex': login_account, '$options': '$i'}
        if ip_address:
            post['ip_address'] = {'$regex': ip_address, '$options': '$i'}

        try:
            cursor = db.login_info.find(post)
            pd_data = pd.DataFrame(list(cursor))
            if not pd_data.empty:
                pd_data = pd_data.astype({'_id': str, 'login_account': str, 'ip_address': str})
        except Exception as e:
            self.logger.error(str(e))
        finally:
            client.close()
        return pd_data

    def create_login_info(self, _id, account=None, ip_address=None, token=None):
        db, client = self.db_handler.connect()
        post = {
            '_id': ObjectId(_id),
            'login_account': account,
            'ip_address': ip_address,
            'token': token,
            'login_time': datetime.datetime.now()
        }
        db.login_info.insert_one(post)

        cursor = db.login_info.find(post)
        pd_data = pd.DataFrame(list(cursor))
        if not pd_data.empty:
            pd_data = pd_data.astype({'_id': str})
        client.close()
        return pd_data

    def delete_login_info(self, id_list):
        db, client = self.db_handler.connect()

        delete_list = []
        for _id in id_list:
            delete_list.append(ObjectId(_id))

        db.login_info.delete_many({'_id': {'$in': delete_list}})

        client.close()
        return None
