# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import os
import struct
import threading
from typing import List

import time

import sys

from flask import request, make_response, jsonify, session
from apps.dashboard import config, log_path, logging_level
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.modbus_template import BrandControl
from logging_utils.logger import Logger
from apps.dashboard import token_module
from pyModbusTCP.client import ModbusClient
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))


class ModbusControlCheck(Resource):

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = dict()

        logger = Logger().create(self.__class__.__name__, level=logging_level, log_path=log_path)
        logger.info('[Post]ModbusControl')
        try:
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                raise Exception('You dont have permission to access.')

            force_reset = request.args.get(ApiConst.FORCE_RESET.value) \
                if ApiConst.FORCE_RESET.value in request.args else False

            dao = StorageFactory(config).get_dao_factory().get_dao()
            if force_reset == '1':
                if not user_info.is_admin:
                    raise Exception('You dont have permission to access.')
                dao.mod_lc_control_state(action='delete')

            rtn_data.Data = dao.mod_lc_control_state(action='get')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
