# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import numpy as np
import pandas as pd
from flask import request, session, make_response, jsonify
from pyModbusTCP.client import ModbusClient

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from .permission_menu_item import get_admin_menu, get_user_menu, get_field_admin_menu
from . import Resource


class OperationMode(Resource):
    logger = Logger().create('Evergreen API - OperationMode', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('Operation Mode Update')
        rtn_data = ApiResponse()

        try:
            self.logger.info('check permission [modify-operation]')
            logger.info('check permission [query]')
            user_info: UserData = session[token_module.auth_session_key]
            if user_info.is_admin:
                user_menu = get_admin_menu()
            elif user_info.is_field_admin:
                user_menu = get_field_admin_menu()
            else:
                user_menu = get_user_menu(user_info.user_id)
            user_control_menu = list(filter(lambda x: x['code'] == 'P01', user_menu))
            if user_control_menu:
                user_control_menu = user_control_menu[0]['children']

            target_p = list(filter(lambda x: x['code'] == 'P01-07' and x['enable'] is True, user_control_menu))
            if not target_p:
                raise Exception('You dont have permission to access.')

            _mode = request.json.get('operation_mode', None)
            if _mode is None:
                raise Exception('mode is required.')

            operation_mode = self.dao.read_operation_mode()
            self.dao.update_operation_mode(int(_mode), user_info.user_name)
            self.dao.write_modbus_logs(user_info, f'operation_mode', _mode, old_value=operation_mode['mode'])

            modbus_dao = StorageFactory(config).get_dao_factory('modbus').get_dao()
            modbus_dao.client.write_single_register(0, _mode)
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)
