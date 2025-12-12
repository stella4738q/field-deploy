# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class SystemStorageSetting(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system storage setting')
        pd_res = []
        try:
            _id = None
            key = None
            value = None
            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.KEY.value in request.args:
                key = request.args[ApiConst.KEY.value]
            if ApiConst.VALUE.value in request.args:
                value = request.args[ApiConst.VALUE.value]

            # get system setting
            self.logger.info('get soc, charge type, emergency power data')
            pd_data = self.dao.get_system_setting(_id=_id, key=key, value=value)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] system storage setting')
        try:
            # check permission
            self.logger.info('check permission [modify-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()

            payload = request.get_json()
            is_notify_time_settings = payload.get(ApiConst.TYPE.value, None)
            if is_notify_time_settings and str(is_notify_time_settings).lower() == 'notify_time_settings':
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.FEMC_NOTIFY_SETTING_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')
            else:
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][PermissionConst.SYSTEM_STORAGE_SETTING_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

            payload = request.get_json()
            data_list = payload[ApiConst.DATA.value]

            for data in data_list:
                _id = data[ApiConst.ID_.value]
                value = data[ApiConst.VALUE.value]
                self.logger.info('update soc, charge type, emergency power data')
                self.dao.update_system_setting(_id, value)
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
