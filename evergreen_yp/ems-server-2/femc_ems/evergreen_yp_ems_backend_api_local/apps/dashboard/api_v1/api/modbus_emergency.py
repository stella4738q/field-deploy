# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import time

import sys

from flask import request, make_response, jsonify, session
from pyModbusTCP.client import ModbusClient

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.modbus_template import BrandControl
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource
from .permission_menu_item import get_admin_menu, get_user_menu, get_field_admin_menu

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))


class ModbusEmergency(Resource):
    logger = Logger().create('Evergreen API - Modbus Emergency', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = dict()

        logger = Logger().create(self.__class__.__name__, level=logging_level, log_path=log_path)
        logger.info('[Post] Modbus Emergency')
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

            target_p = list(filter(lambda x: x['code'] == 'P01-06' and x['enable'] is True, user_control_menu))
            if not target_p:
                raise Exception('You dont have permission to access.')

            payload = request.get_json()

            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            action = payload[ApiConst.ACTION.value]

            if field_id is None:
                raise Exception(f'can not found field_id equal [{field_id}]')

            # PCS Controller
            code = 'PCS'
            dao = StorageFactory(config).get_dao_factory().get_dao()
            eq_df = dao.get_control_equipment(code)
            if eq_df.empty:
                raise Exception(f'can not found equipment code equal [{code}]')

            target = eq_df.iloc[0]

            ip = target['ip']
            port = target['port']
            unit_id = target['unit_id']
            brand = target['brand']
            equipment_id = target['name']

            client = ModbusClient(host=ip, port=int(port), unit_id=int(unit_id), timeout=5)
            pcs_controller = BrandControl(brand, client, 'advanced', equipment_id).get_template()

            # BMS Controller
            code = 'BMS'
            dao = StorageFactory(config).get_dao_factory().get_dao()
            eq_df = dao.get_control_equipment(code)
            if eq_df.empty:
                raise Exception(f'can not found equipment code equal [{code}]')

            bms_list = list()
            for idx, row in eq_df.iterrows():
                target = row

                ip = target['ip']
                port = target['port']
                unit_id = target['unit_id']
                brand = target['brand']
                equipment_id = target['name']

                client = ModbusClient(host=ip, port=int(port), unit_id=int(unit_id), timeout=5)
                bms_controller = BrandControl(brand, client, 'advanced', equipment_id).get_template()
                bms_list.append(bms_controller)

            if action == "EMERGENCY_ON_OFF":
                # write_modbus_log
                dao.write_modbus_logs(user_info, f'EMERGENCY:::PCS_ON_OFF', True)

                # step1:PCS功率歸零、關閉
                pcs_controller.pcs_on_off(False)

                time.sleep(3)

                # step2:BMS下高壓指令
                for bms_controller in bms_list:
                    dao.write_modbus_logs(user_info, f'EMERGENCY:::BMS_ON_OFF:::{bms_controller.equipment_id}', True)
                    bms_controller.bms_on_off(False)

        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)
