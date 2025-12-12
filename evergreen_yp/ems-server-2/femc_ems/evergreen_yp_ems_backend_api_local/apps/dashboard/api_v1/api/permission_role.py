# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import copy
import json

import numpy as np
from flask import request, make_response, jsonify, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class PermissionRole(Resource):

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] permission role')
        try:
            # 2024.06.06 角色權限修正
            # user_info: UserData = session[token_module.auth_session_key]
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            _id = request.args[ApiConst.ID.value]
            name = request.args[ApiConst.NAME.value]
            enable = request.args[ApiConst.ENABLE.value]
            fields = request.args[ApiConst.FIELDS.value] if ApiConst.FIELDS.value in request.args else None
            if not fields:
                fields = config[ConfigConstant.APP.value][ConfigConstant.FIELD_ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_roles(_id, name, enable if enable else None, fields)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[post] permission role')
        try:
            user_info: UserData = session[token_module.auth_session_key]

            # 2024.06.06 角色權限修正
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            payload = request.get_json()
            _id = payload[ApiConst.ID.value]
            name = payload[ApiConst.NAME.value]
            enable = payload[ApiConst.ENABLE.value]
            menu_items = payload.get(ApiConst.MENU_ITEMS.value, None)

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            if _id:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.PERMISSION_ROLE_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                logger.info('update permission role')
                pd_data = dao.update_role(_id, name, enable, menu_items)
            else:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.PERMISSION_ROLE_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                logger.info('create permission role')
                current_field = config[ConfigConstant.APP.value][ConfigConstant.FIELD_ID.value]
                if menu_items is None:
                    menu_item = copy.deepcopy(token_module.menu_serialized)
                else:
                    menu_item = copy.deepcopy(menu_items)
                    
                pd_data = dao.create_role(name, current_field, menu_item, enable if enable else 1)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def delete(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[delete] permission role')
        try:
            user_info: UserData = session[token_module.auth_session_key]

            # 2024.06.06 角色權限修正
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.PERMISSION_ROLE_DELETE.value]:
                raise Exception('You dont have permission to access.')

            _id = request.get_json()[ApiConst.ID.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_role([_id])
            dao.delete_user_roles_by_role_id(_id)
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
