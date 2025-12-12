# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required
from . import Resource


class PermissionUserChangePassword(Resource):

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('permission user change password')
        response_data = {
            'Success': True,
            'Message': ''
        }
        try:
            payload = request.get_json()
            user_id = payload[ApiConst.USER_ID.value]
            old_password = payload[ApiConst.OLD_PASSWORD.value]
            new_password = payload[ApiConst.NEW_PASSWORD.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            rtn_msg = dao.change_password(user_id, old_password, new_password)

            if rtn_msg:
                response_data['Success'] = rtn_msg['Success']
                response_data['Message'] = rtn_msg['Msg']

        except Exception as e:
            response_data = {
                'Success': False,
                'Message': e
            }

        return response_data, 200, None