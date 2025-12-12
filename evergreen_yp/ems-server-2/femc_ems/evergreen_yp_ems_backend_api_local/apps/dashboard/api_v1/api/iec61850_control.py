# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os

import sys

from flask import request, make_response, jsonify, session
from apps.dashboard import config, log_path, logging_level
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.iec61850.iec61850_dao import IEC61850Dao
from dashboard_lib.modbus_template import BrandControl, IECControl
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource
from apps.dashboard.constant import ApiConst, SystemStatus
from .permission_menu_item import get_admin_menu, get_field_admin_menu, get_user_menu

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))


class IEC61850Control(Resource):
    logger = Logger().create('Evergreen API - IEC61850Control', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = dict()

        logger = Logger().create(self.__class__.__name__, level=logging_level, log_path=log_path)
        logger.info('[Post]IEC61850Control')
        try:
            # check permission
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

            payload = request.get_json()

            """
            EquipmentType:
            PCS
            FIRE
            ACB
            VCB
            ...
            
            Action
            PCS: 
              V PCS_ON_OFF: True:On / False:Off /
              V PCS_SET_MODE: on-grid / off-grid / pq-mode-on / pq-mode-off
              V PCS_FAULT_RESET: True:Rest_Fault / False:Do nothing
              V PCS_SET_POWER: 直接下功率, 50kw = 50, -100kw = -100
            BMS:
              V BMS_ON_OFF: True:all dc dc on / False: all dc dc off
              V BMS_FAULT_RESET: True:Rest_Fault / False:Do nothing
            SUN:
              V SUNCTL_ON_OFF: True:On / False:Off
            RACK:
            FIRE:
              V FIRE_MAIN_SWITCH_ON_OFF: True:On / False:Off (消防總開關)
              V FIRE_ON_OFF: True:On / False:Off
            ACB:
              V ACB_ON_OFF: True:On / False:Off
            共用:
              V GET_BLACK_START 不用參數，取得全黑啟動設定
            ...
            """
            customer = payload[ApiConst.CUSTOMER.value]
            code = payload[ApiConst.CODE.value]
            equipment_id = payload[ApiConst.EQUIPMENT_ID.value]
            action = payload[ApiConst.ACTION.value]
            set_value = payload[ApiConst.VALUE.value] if ApiConst.VALUE.value in payload else None
            parameter = payload.get('parameter')

            if action is None or code is None:
                raise Exception('action or equipment is required')

            code = str(code).upper()

            eq_df = self.dao.get_control_equipment(code)
            if eq_df.empty:
                raise Exception(f'can not found equipment code equal [{code}]')

            if len(eq_df) == 1:
                target = eq_df.iloc[0]
            else:
                temp_df = eq_df.query(f"_id == '{equipment_id}' or name == '{str(equipment_id).upper()}'")
                if temp_df.empty:
                    raise Exception(f'can not found equipment id equal [{equipment_id}]')
                target = temp_df.iloc[0]

            equipment_id = target['_id']
            ip = target['ip']
            port = target['port']
            brand = target['brand']
            name = target['name']

            client = IEC61850Dao(config=config, uri=ip, port=int(port))
            controller = IECControl(brand, client, customer).get_template()

            _mode = 0
            operation_mode = self.dao.read_operation_mode()
            if operation_mode['mode'] is not None:
                _mode = operation_mode['mode']

            if _mode == 1:
                raise Exception("目前非SCADA模式，不可操作")

            # write_modbus_log
            self.dao.write_modbus_logs(user_info, f'{name}:::{action}', set_value)

            # VCB
            if action == "VCB_ON_OFF":
                controller.cb_on_off(set_value)

        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)
