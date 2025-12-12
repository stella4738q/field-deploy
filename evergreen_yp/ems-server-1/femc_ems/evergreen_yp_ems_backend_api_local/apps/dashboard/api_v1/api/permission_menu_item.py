# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import copy
from flask import make_response, jsonify, session

from apps.dashboard import config, log_path, logging_level, token_module
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


def get_admin_menu():
    def recursive(items):
        for menu in items:
            menu['enable'] = True
            children = menu['children']
            if len(children) > 0:
                recursive(children)
            api_list = menu['api_list']
            for api in api_list:
                api['enable'] = True

    menu_items = copy.deepcopy(token_module.menu_serialized)
    recursive(menu_items)
    return menu_items


def get_field_admin_menu():
    def recursive(items):
        for menu in items:
            menu['enable'] = True
            children = menu['children']
            if len(children) > 0:
                recursive(children)
            api_list = menu['api_list']
            for api in api_list:
                # 案場資訊不可新增、修改、刪除
                if api['code'] not in ['p_00019', 'p_00020', 'p_00021']:
                    api['enable'] = True

    menu_items = copy.deepcopy(token_module.menu_serialized)
    recursive(menu_items)
    return menu_items


def get_user_menu(user_id):
    def process_menu(role_df, basic_menu):
        if role_df.empty:
            return
        for row, data in role_df.iterrows():
            role: list = data['roles']
            if role:
                role_menu = role[0]['permission']
                recursive(role_menu, basic_menu)

    def recursive(items, basic_menu):
        for menu in items:
            targets = [x for x in basic_menu if x['code'] == menu['code']]
            basic_children = list()
            if len(targets) > 0:
                target = targets[0]
                if not target['enable']:
                    target['enable'] = menu['enable']

                target['api_list'] = list()
                api_list = menu['api_list']
                if menu['api_list']:
                    for api in api_list:
                        # 案場資訊不可新增、修改、刪除
                        if api['code'] not in ['p_00019', 'p_00020', 'p_00021']:
                            found = list(filter(lambda x: x['code'] == api['code'], target['api_list']))
                            if not found:
                                if api['enable'] is True:
                                    target['api_list'].append(api)
                            elif not found[0]['enable'] and api['enable'] is True:
                                found[0]['enable'] = api['enable']

                basic_children = target['children']
            children = menu['children']
            if len(children) > 0:
                recursive(children, basic_children)

    menu_items = copy.deepcopy(token_module.menu_serialized)

    # Get User Field
    user_fields = token_module.dao.get_user_fields(user_id=user_id)
    if not user_fields.empty:
        fields = user_fields['field_id'].tolist()
        # get permission by role
        for field in fields:
            _api = copy.deepcopy(token_module.api_list)
            # Get User Filed Role
            user_roles = token_module.dao.get_user_roles_by_field(user_id=user_id, field_id=field)
            process_menu(user_roles, menu_items)
    return menu_items


class PermissionMenuItem(Resource):
    """
    登入後，前端取得功能清單使用
    """

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('get menu item')
        response_data = ApiResponse()
        try:
            user_info: UserData = session[token_module.auth_session_key]
            if user_info.is_admin:
                response_data.Data = get_admin_menu()
            elif user_info.is_field_admin:
                response_data.Data = get_field_admin_menu()
            else:
                response_data.Data = get_user_menu(user_info.user_id)
        except Exception as e:
            response_data.Success = False
            response_data.Msg = str(e)
        return make_response(jsonify(response_data.serialized), 200)
