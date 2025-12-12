# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from dashboard_lib.constant import ConfigConstant
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource
from apps.dashboard.api_v1.utils import modbus_type


class ModbusAccessData(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[get] modbus access data')
        res = []
        try:
            event_type = request.args[ApiConst.TYPE.value]

            # mapping event type
            start_address = modbus_type(event_type)

            # get data
            dao = StorageFactory(config).get_dao_factory(using_db=ConfigConstant.MODBUS.value).get_dao()
            res = dao.read(func_code=3, start_address=start_address, quantity=1)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': res}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[post] modbus access data')
        try:
            payload = request.get_json()
            event_type = payload[ApiConst.TYPE.value]
            status_value = payload[ApiConst.DATA.value]

            # mapping event type
            start_address = modbus_type(event_type)

            # write / update data
            dao = StorageFactory(config).get_dao_factory(using_db=ConfigConstant.MODBUS.value).get_dao()
            dao.update(func_code=6, start_address=start_address, data=status_value, quantity=1)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None