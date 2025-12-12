# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.gmail_oauth_client import SMTP_GmailOAuthClient
from utility.smtp import SMTP
from utility.token_module import token_required, UserData
from . import Resource


class PermissionUserReset(Resource):

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('permission user reset')
        response_data = {
            'Success': True,
            'NewPassword': '',
            'Message': ''
        }
        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.PERMISSION_USER_RESET.value]:
                raise Exception('You dont have permission to access.')

            payload = request.get_json()
            user_id = payload[ApiConst.USER_ID.value]
            new_password = payload[ApiConst.NEW_PASSWORD.value] if ApiConst.NEW_PASSWORD.value in payload else None

            dao = StorageFactory(config).get_dao_factory().get_dao()
            rtn_msg = dao.reset_password(user_id, new_password)

            response_data['Success'] = rtn_msg['Success']
            response_data['NewPassword'] = rtn_msg['NewPassword']

        except Exception as e:
            response_data = {
                'Success': False,
                'Message': str(e),
                'NewPassword': ''
            }
        return response_data, 200, None
