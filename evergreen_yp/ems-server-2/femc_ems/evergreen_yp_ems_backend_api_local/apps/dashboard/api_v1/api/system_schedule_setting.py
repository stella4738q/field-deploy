# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class SystemScheduleSetting(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system schedule setting')
        pd_res = []
        try:
            _id = None
            week = None
            start_time = None
            end_time = None
            _type = None
            soc = None

            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.WEEK.value in request.args:
                week = request.args[ApiConst.WEEK.value]
            if ApiConst.START_TIME.value in request.args:
                start_time = request.args[ApiConst.START_TIME.value]
            if ApiConst.END_TIME.value in request.args:
                end_time = request.args[ApiConst.END_TIME.value]
            if ApiConst.TYPE.value in request.args:
                _type = request.args[ApiConst.TYPE.value]
            if ApiConst.SOC.value in request.args:
                soc = request.args[ApiConst.SOC.value]

            # get upper soc, charge type, emergency power
            self.logger.info('get soc, charge type, emergency power value')
            pd_system_setting = self.dao.get_system_setting()

            upper_soc = float(pd_system_setting[pd_system_setting[ApiConst.KEY.value] == ApiConst.SOC.value]['value'].tolist()[0])
            charge_type = pd_system_setting[pd_system_setting[ApiConst.KEY.value] == ApiConst.CHARGE_TYPE.value]['value'].tolist()[0]
            emergency_power = np.float(pd_system_setting[pd_system_setting[ApiConst.KEY.value] == ApiConst.EMERGENCY_POWER.value]['value'].tolist()[0])
            protect_power = np.float(pd_system_setting[pd_system_setting[ApiConst.KEY.value] == ApiConst.PROTECT_POWER.value]['value'].tolist()[0])

            # get total capacity
            self.logger.info('get total capacity')
            equipment_type = EquipmentType.BMS.value
            pd_pcs_data = self.dao.get_pcs_setting(equipment_type=equipment_type)
            total_capacity = 0
            if not pd_pcs_data.empty:
                pd_pcs_data = pd_pcs_data.replace({"": np.nan})
                capacity_list = [float(capacity) if capacity else 0 for capacity in list(pd_pcs_data['capacity'])]
                total_capacity = sum(capacity_list) / 1000

            if total_capacity == 0:
                raise Exception("錯誤: 最大可放電量未設定")

            # calculate total discharge
            self.logger.info('calculate total discharge')
            #  (總案場容量 * ((SOC上限 - SOC下限) / 100) - 緊急發電量) / 總案場容量 * 100
            total_discharge = \
                (total_capacity * ((upper_soc-protect_power) / 100) - emergency_power) / total_capacity * 100

            pd_rnt = dict()
            pd_rnt[ApiConst.UPPER_SOC.value] = upper_soc
            pd_rnt[ApiConst.CHARGE_TYPE.value] = charge_type
            pd_rnt[ApiConst.EMERGENCY_POWER.value] = emergency_power
            pd_rnt[ApiConst.TOTAL_CAPACITY.value] = total_capacity if str(total_capacity) != 'nan' else 0
            pd_rnt[ApiConst.PROTECT_POWER.value] = protect_power
            pd_rnt[ApiConst.TOTAL_DISCHARGE.value] = \
                round(total_discharge, 2) if str(round(total_discharge, 2)) != 'nan' else 0

            # get schedule
            self.logger.info('get charge schedule')
            pd_data = self.dao.get_schedule_setting(_id=_id, week=week, start_time=start_time, end_time=end_time,
                                                    _type=_type, soc=soc)
            pd_data = pd_data.replace({np.nan: None})
            pd_rnt[ApiConst.SCHEDULE.value] = pd_data.to_dict('records')
            pd_res = [pd_rnt]

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] system schedule setting')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            week = payload[ApiConst.WEEK.value] if 'week' in payload else None
            start_time = payload[ApiConst.START_TIME.value] if 'start_time' in payload else None
            end_time = payload[ApiConst.END_TIME.value] if 'end_time' in payload else None
            _type = payload[ApiConst.TYPE.value] if 'type' in payload else None
            soc = payload[ApiConst.SOC.value] if 'soc' in payload else None


            if _id:
                # check permission
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_SCHEDULE_SETTING_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update charge schedule')
                pd_data = self.dao.update_schedule_setting(_id, week, start_time, end_time, _type, soc)
            else:
                # check permission
                self.logger.info('check permission [create-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_SCHEDULE_SETTING_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create charge schedule')
                pd_data = self.dao.create_schedule_setting(_id, week, start_time, end_time, _type, soc)

            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] system schedule setting')
        try:
            # check permission
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_SCHEDULE_SETTING_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('delete charge schedule')
            _id = request.get_json()[ApiConst.ID.value]
            self.dao.delete_schedule_setting([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None