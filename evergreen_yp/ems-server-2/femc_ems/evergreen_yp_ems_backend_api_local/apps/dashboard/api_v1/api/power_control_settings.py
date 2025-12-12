# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import numpy as np
from flask import request, session, make_response, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class PowerControlSettings(Resource):
    """
        利用設定檔中
        抑低用電 細部排成
    """
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] permission role')
        try:
            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_power_control_settings()
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
            payload = request.get_json()
            _id = payload.get(ApiConst._ID.value, None)
            start_time = payload[ApiConst.START_TIME.value]
            end_time = payload[ApiConst.END_TIME.value]
            kw = payload[ApiConst.KW.value]

            if start_time is None:
                raise Exception("開始時間為必填")
            if end_time is None:
                raise Exception("結束時間為必填")
            if kw is None:
                raise Exception("目標功率為必填")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            if _id:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_STORAGE_SETTING_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')
                pd_data = dao.update_power_control_settings(_id, start_time, end_time, kw)
            else:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_STORAGE_SETTING_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')
                pd_data = dao.create_power_control_settings(start_time, end_time, kw)
            if not pd_data.empty:
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
        logger.info('[delete] power control settings')
        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_STORAGE_SETTING_POST_UPDATE.value]:
                raise Exception('You dont have permission to access.')

            _id = request.get_json()[ApiConst.ID.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_power_control_settings([_id])
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
