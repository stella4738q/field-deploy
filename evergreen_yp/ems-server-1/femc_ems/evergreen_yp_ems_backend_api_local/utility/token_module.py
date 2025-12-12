import copy
import datetime
import distutils.util
import json
import logging
import jwt
import pandas as pd
from typing import List
from functools import wraps
from flask import request, session, jsonify, make_response

from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils import Logger
from utility.api_response import ApiResponse


class UserData:
    def __init__(self, user_id='', user_name='', company=None, is_admin=False, is_field_admin=False,
                 login_info_id=None):
        self.user_id = str(user_id)
        self.user_name = user_name
        self.is_admin = True if is_admin else False
        self.is_field_admin = True if is_field_admin else False
        self.company = company
        self.user_field_permission: dict = dict()
        self.login_info_id = login_info_id


class MenuItem:
    def __init__(self, code, name, icon, route, enable, tag):
        self.code = code
        self.name = name
        self.icon = icon
        self.route = route
        self.enable = enable
        self.tag = tag
        self.children: List[MenuItem] = list()
        self.api_list: List[ApiItem] = list()


class ApiItem:
    def __init__(self, code, category, method, note, key, description, enable=False):
        self.code = code
        self.category = category
        self.method = method
        self.note = note
        self.key = key
        self.description = description
        self.enable = enable


class FieldKey:
    def __init__(self, field_id, field_key, auth_security_key):
        self.field_id = field_id
        self.field_key = field_key
        self.auth_security_key = auth_security_key


class TokenModule:
    def __init__(self, config):
        self._config = config
        setting_config = config[ConfigConstant.APP.value]

        # init logger
        log_path = setting_config[ConfigConstant.LOG_PATH.value]
        self.logger = Logger().create('TokenModule', level=logging.INFO, log_path=log_path)

        # Auth
        self.auth_header = setting_config[ConfigConstant.REQUEST_HEADER.value]
        self.auth_security_key = setting_config[ConfigConstant.SECRET_KEY.value]
        self.auth_session_key = setting_config[ConfigConstant.SESSION_KEY.value]
        self.api_auth_enable = distutils.util.strtobool(setting_config[ConfigConstant.AUTH_ENABLE.value])
        self.api_auth_life = int(setting_config[ConfigConstant.AUTH_LIFE.value])
        self.single_login = setting_config[ConfigConstant.SINGLE_LOGIN.value]

        # Dao
        self.dao = StorageFactory(config).get_dao_factory().get_dao()

        # ApiList & Menu
        self.__init_api_list__()
        self.__init_menu_list__()
        self.__init_field_key__()

    def __init_api_list__(self):
        self.api_list: List[ApiItem] = list()
        try:
            file_path = 'configs/api_list.csv'
            df = pd.read_csv(file_path)
            if not df.empty:
                self.api_list = [
                    ApiItem(data.code, data.category, data.method, data.note, data.key, data.description)
                    for data in df.itertuples()
                ]

        except Exception as e:
            self.logger.error(repr(e))
            raise Exception(e)

    def __init_menu_list__(self):
        try:
            self.menu_items: List[MenuItem] = list()
            file_path = 'configs/menu_item.json'
            with open(file_path, 'r', encoding="utf-8") as f:
                menus = json.loads(f.read())
                menu_items = menus['menu_items']
            if menu_items:
                self.menu_serialized: list = menu_items
                self.menu_items = self.__menu_parser__(menu_items)
        except Exception as e:
            self.logger.error(repr(e))
            raise Exception(e)

    def __menu_parser__(self, menus, join_target: MenuItem = None):
        rtn_data: List[MenuItem] = list()

        for menu in menus:
            menu_item = MenuItem(menu['code'], menu['name'], menu['icon'], menu['route'], menu['enable'],
                                 menu['tag'])
            api_list = menu['api_list']
            if len(api_list) > 0:
                menu_item.api_list = [
                    ApiItem(api['code'], api['category'], api['method'], api['note'], api['key'],
                            api['description'], api['enable'])
                    for api in api_list
                ]

            children = menu['children']
            if len(children) > 0:
                self.__menu_parser__(children, menu_item)
                if join_target is not None:
                    join_target.children.append(menu_item)
                else:
                    rtn_data.append(menu_item)
            elif join_target is not None:
                join_target.children.append(menu_item)
            else:
                rtn_data.append(menu_item)
        return rtn_data

    def __init_field_key__(self):
        try:
            self.field_key_list: List[FieldKey] = list()
            file_path = 'configs/field_key.json'
            with open(file_path, 'r', encoding="utf-8") as f:
                fields = json.loads(f.read())
                field_keys = fields['field_keys']
            if field_keys:
                self.field_key_list = [
                    FieldKey(field['field_id'], field['field_key'], field['auth_key'])
                    for field in field_keys
                ]
        except Exception as e:
            self.logger.error(repr(e))
            raise Exception(e)


def token_required(token_module: TokenModule):
    def out_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            result = ApiResponse()
            user_info = UserData()
            token = None
            if token_module.auth_header.capitalize() in request.headers:
                token = request.headers[token_module.auth_header.capitalize()]
            if not token:
                if token_module.api_auth_enable:
                    result.Success = False
                    result.Message = 'Token not found'
                    return make_response(jsonify(result.serialized), 403)
                session[token_module.auth_session_key] = user_info
                return f(*args, **kwargs)
            else:
                try:
                    # token check
                    if token.startswith('batch'):
                        _token = token.split('__')
                        field_id = _token[1]
                        real_token = _token[2]
                        target = [data for data in token_module.field_key_list if data.field_id == field_id]
                        if len(target) > 0:
                            target = target[0]
                            data = jwt.decode(real_token, target.auth_security_key, verify=False,
                                              options={'verify_signature': False}, algorithms='HS256')
                            if data['field_key'] != target.field_key:
                                raise Exception("You dont have permission to access.")

                            # as admin
                            _api = copy.deepcopy(token_module.api_list)
                            permission_list: List[ApiItem] = list()
                            for item in _api:
                                item.enable = True
                                permission_list.append(item)

                            # set user_info
                            user_info.is_admin = True
                            user_info.user_id = target.field_id

                            # all fields
                            user_fields = token_module.dao.get_fields()
                            if not user_fields.empty:
                                fields = user_fields['_id'].tolist()
                                for field in fields:
                                    user_info.user_field_permission[field] = \
                                        dict((x.key, x.enable) for x in permission_list)
                    else:
                        data = jwt.decode(token, token_module.auth_security_key, verify=False,
                                          options={'verify_signature': False}, algorithms='HS256')
                        exp_data = datetime.datetime.fromtimestamp(data["exp_date"])
                        if token_module.api_auth_enable:
                            if datetime.datetime.utcnow() > exp_data:
                                raise Exception('Token is expired.')

                        user_id = data['id']
                        df = token_module.dao.get_users(_id=user_id)
                        if not df.empty:
                            user = df.iloc[0]
                            user_info = UserData(
                                user_id=user['_id'], user_name=user['name'], is_admin=user['is_admin'], is_field_admin=user['is_field_admin'],
                                company=user['company'])

                            if user_info.is_admin:
                                # all permission
                                _api = copy.deepcopy(token_module.api_list)
                                permission_list: List[ApiItem] = list()
                                for item in _api:
                                    item.enable = True
                                    permission_list.append(item)

                                # all fields
                                user_fields = token_module.dao.get_fields()
                                if not user_fields.empty:
                                    fields = user_fields['_id'].tolist()
                                    for field in fields:
                                        user_info.user_field_permission[field] = \
                                            dict((x.key, x.enable) for x in permission_list)
                            else:
                                # 1. 先check single_login is True 才繼續
                                # 2. check user login_info id 是否有效
                                if str(token_module.single_login).lower() == "true":
                                    df_login = token_module.dao.get_login_info(_id=data['login_info_id'])
                                    if df_login.empty:
                                        raise Exception('E003: 已在其他地方登入，請重新登入')

                                # Get User Field
                                user_fields = token_module.dao.get_user_fields(user_id=user['_id'])
                                if not user_fields.empty:
                                    fields = user_fields['field_id'].tolist()
                                    if user_info.is_field_admin:
                                        # all permission
                                        _api = copy.deepcopy(token_module.api_list)
                                        permission_list: List[ApiItem] = list()
                                        for item in _api:
                                            item.enable = True
                                            permission_list.append(item)

                                        for field in fields:
                                            user_info.user_field_permission[field] = \
                                                dict((x.key, x.enable) for x in permission_list)
                                    else:
                                        # get permission by role
                                        for field in fields:
                                            _api = copy.deepcopy(token_module.api_list)
                                            # Get User Filed Role
                                            user_roles = token_module.dao.get_user_roles_by_field(
                                                user_id=user['_id'], field_id=field)
                                            permission_list = get_role_menu_api_list(user_roles, _api)
                                            user_info.user_field_permission[field] = \
                                                dict((x.key, x.enable) for x in permission_list)
                    session[token_module.auth_session_key] = user_info
                except Exception as e:
                    session[token_module.auth_session_key] = user_info
                    token_module.logger.error(e)
                    result.Success = False
                    result.Message = f'Auth error: {str(e)}'
                    if 'Signature has expired' == str(e):
                        result.Message = 'Token is expired.'
                    return make_response(jsonify(result.serialized), 403)
                return f(*args, **kwargs)

        return decorator

    return out_decorator


def get_role_menu_api_list(role_df: pd.DataFrame, api_list):
    rtn_data = api_list
    if role_df.empty:
        return rtn_data

    for row, data in role_df.iterrows():
        role: list = data['roles']
        if role:
            role_menu = role[0]['permission']
            parser_data(role_menu, rtn_data)
    return rtn_data


def parser_data(role_menu, rtn_data):
    for item in role_menu:
        if item['enable']:
            if len(item['children']) > 0:
                rtn_data = parser_data(item['children'], rtn_data)
            if len(item['api_list']) > 0:
                enable_api_list = [api['key'] for api in item['api_list'] if api['enable']]
                for x in [x for x in rtn_data if x.key in enable_api_list]:
                    x.enable = True
    return rtn_data
