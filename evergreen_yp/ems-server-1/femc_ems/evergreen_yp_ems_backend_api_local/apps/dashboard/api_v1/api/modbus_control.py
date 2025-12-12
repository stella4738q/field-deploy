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
from apps.dashboard.constant import ApiConst, SystemStatus, ConfigConstant
from .permission_menu_item import get_admin_menu, get_field_admin_menu, get_user_menu

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))


class ModbusControl(Resource):
    logger = Logger().create('Evergreen API - ModbusControl', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = dict()

        logger = Logger().create(self.__class__.__name__, level=logging_level, log_path=log_path)
        logger.info('[Post]ModbusControl')
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

            dao = StorageFactory(config).get_dao_factory().get_dao()
            eq_df = dao.get_control_equipment(code)
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
            unit_id = target['unit_id']
            brand = target['brand']
            name = target['name']

            client = ModbusClient(host=ip, port=int(port), unit_id=int(unit_id), timeout=5)
            controller = BrandControl(brand, client, customer).get_template()

            _mode = 0
            operation_mode = dao.read_operation_mode()
            if operation_mode['mode'] is not None:
                _mode = operation_mode['mode']

            if _mode == 1:
                raise Exception("目前非SCADA模式，不可操作")

            # write_modbus_log
            dao.write_modbus_logs(user_info, f'{name}:::{action}', set_value)

            if action.startswith("PCS"):
                target_p = list(filter(lambda x: x['code'] == 'P01-01' and x['enable'] is True, user_control_menu))
                if not target_p:
                    raise Exception('You dont have permission to access.')

                if action == "PCS_ON_OFF":
                    working_status = dao.get_working_status()
                    if working_status == SystemStatus.BLACK_START.value:
                        raise Exception("全黑啟動中，不可執行此作業")
                    controller.pcs_on_off(set_value)

                elif action == "PCS_SET_MODE":
                    controller.pcs_set_mode(set_value)

                elif action == "PCS_SET_POWER":
                    # 逆送電狀態檢查
                    working_status = dao.get_working_status()
                    if working_status == SystemStatus.REVERSE_POWER_MODE.value:
                        raise Exception("送電保護中，不可手動充放電")
                    elif working_status == SystemStatus.BLACK_START.value:
                        raise Exception("全黑啟動中，不可手動充放電")
                    # # 暫時註解
                    # elif working_status == SystemStatus.SR_CONTROL.value:
                    #     raise Exception("即時備轉服務中，不可手動充放電")
                    controller.pcs_set_power(set_value)
                    dao.upsert_working_status(SystemStatus.MANUAL.value)

                elif action == "PCS_SET_CC_CV":
                    controller.pcs_set_cc_cv(set_value)
                    dao.upsert_working_status(SystemStatus.MANUAL.value)

                elif action == "PCS_BLACK_START_ON_OFF":
                    controller.pcs_black_start_on_off(set_value)
                    if set_value:
                        dao.upsert_working_status(SystemStatus.BLACK_START.value)
                    else:
                        dao.upsert_working_status(SystemStatus.FREE.value)

                elif action == "PCS_FAULT_RESET":
                    working_status = dao.get_working_status()
                    if working_status == SystemStatus.BLACK_START.value:
                        raise Exception("全黑啟動中，不可執行此作業")
                    controller.pcs_fault_reset(set_value)

                elif action == "PCS_BLACK_START_FAULT_RESET":
                    controller.pcs_black_start_fault_reset()

            elif action.startswith("BMS"):
                if action.startswith("BMS_DCP"):
                    target_p = list(filter(lambda x: x['code'] == 'P01-02' and x['enable'] is True, user_control_menu))
                    if not target_p:
                        raise Exception('You dont have permission to access.')
                    if action == "BMS_DCP_ON_OFF":
                        if parameter is None:
                            raise Exception('請輸入DCP modbus address')
                        controller.dcp_on_off(set_value, parameter)
                else:
                    # BMS
                    target_p = list(filter(lambda x: x['code'] == 'P01-02' and x['enable'] is True, user_control_menu))
                    if not target_p:
                        raise Exception('You dont have permission to access.')
                    if action == "BMS_ON_OFF":
                        controller.bms_on_off(set_value)

                    elif action == "BMS_FAULT_RESET":
                        controller.bms_fault_reset(set_value)
                    elif action == "BMS_DC_SWITCH_ONOFF":
                        controller.bms_dc_switch_on_off(set_value)

            elif action.startswith("SUN"):
                target_p = list(filter(lambda x: x['code'] == 'P01-03' and x['enable'] is True, user_control_menu))
                if not target_p:
                    raise Exception('You dont have permission to access.')
                if action == "SUNCTL_ON_OFF":
                    # SunCtl 太陽能開關
                    controller.inverter_on_off(set_value)
                elif action == "SUNCTL_SET_POWER":
                    # SunCtl 設定輸出百分比
                    controller.inverter_set_power_percent(set_value)

            # FIRE
            elif action == "FIRE_MAIN_SWITCH_ON_OFF":
                dao.update_fire_main_status(set_value)
            elif action == "FIRE_ON_OFF":
                fire_main_switch = False
                df = dao.get_system_setting(key="fire_main_switch", is_system=False)
                if not df.empty:
                    fire_main_switch = df.iloc[0]['value']

                if fire_main_switch:
                    raise Exception("消防隔離開關已投入，請先切離")
                else:
                    controller.fire_on_off(set_value)

            # ACB
            elif action == "ACB_ON_OFF":
                controller.acb_on_off(set_value)

            # PUMP
            elif action == "PUMP_ON_OFF":
                if not parameter:
                    raise Exception("缺少參數: parameter")
                controller.pump_on_off(set_value, parameter)

            # SOL
            elif action == "SOL_ON_OFF":
                if not parameter:
                    raise Exception("缺少參數: parameter")
                controller.sol_on_off(set_value, parameter)

            # WATER
            elif action == "WATER_ON_OFF":
                if not parameter:
                    raise Exception("缺少參數: parameter")
                controller.water_on_off(set_value, parameter)

            # 通用(設定類取值)
            elif action == "GET_BLACK_START":
                rtn_data.Data = controller.get_black_start()

        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)
