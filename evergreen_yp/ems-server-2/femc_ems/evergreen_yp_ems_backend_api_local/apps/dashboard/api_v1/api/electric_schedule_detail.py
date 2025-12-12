# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import copy
import datetime

import numpy as np
import pandas as pd
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class ElectricScheduleDetail(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] electric schedule detail')
        pd_res = []
        try:
            parent_id = None
            _id = None
            week = None
            start_time = None
            end_time = None
            _type = None
            soc = None

            if ApiConst.PARENT_ID.value in request.args:
                parent_id = request.args[ApiConst.PARENT_ID.value]
            if parent_id is None:
                raise Exception('parent id is required.')

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
            pd_settings = self.dao.get_system_setting()

            charge_type = pd_settings[pd_settings[ApiConst.KEY.value] == 'charge_type']['value'].tolist()[0]
            max_soc = float(pd_settings[pd_settings[ApiConst.KEY.value] == 'max_soc']['value'].tolist()[0])
            min_soc = float(pd_settings[pd_settings[ApiConst.KEY.value] == 'min_soc']['value'].tolist()[0])

            # 緊急電量，不一定會有
            emergency_power = 0
            e_power = pd_settings.query('key == "emergency_power"')
            if not e_power.empty:
                emergency_power = float(e_power.iloc[0]['value'])

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
                (total_capacity * ((max_soc-min_soc) / 100) - emergency_power) / total_capacity * 100

            pd_rnt = dict()
            pd_rnt[ApiConst.UPPER_SOC.value] = max_soc
            pd_rnt[ApiConst.CHARGE_TYPE.value] = charge_type
            pd_rnt[ApiConst.EMERGENCY_POWER.value] = emergency_power
            pd_rnt[ApiConst.TOTAL_CAPACITY.value] = total_capacity if str(total_capacity) != 'nan' else 0
            pd_rnt[ApiConst.PROTECT_POWER.value] = min_soc
            pd_rnt[ApiConst.TOTAL_DISCHARGE.value] = \
                round(total_discharge, 2) if str(round(total_discharge, 2)) != 'nan' else 0

            # get schedule
            self.logger.info('get electric schedule detail')
            pd_data = self.dao.get_electric_schedule_detail(
                parent_id, _id=_id, week=week, start_time=start_time, end_time=end_time, _type=_type, soc=soc)

            if pd_data is None or pd_data.empty:
                pd_rnt[ApiConst.SCHEDULE.value] = []
                pd_res = [pd_rnt]
            else:
                if pd_data['week'].dtype != object:
                    pd_data['week'] = pd_data['week'].astype(str)

                # 離峰日排程
                holiday_df = pd_data.loc[pd_data['week'] == '7']
                today = datetime.datetime.today()
                week_monday = today - datetime.timedelta(days=today.weekday())

                # 找出本週內實際為台電假日的 weekday（1~7；週一=1）
                holiday_weekdays = []
                for d in range(7):
                    current_date = week_monday + datetime.timedelta(days=d)
                    if self.dao.check_today_is_taipower_holiday(current_date):
                        holiday_weekdays.append(str(current_date.weekday() + 1))

                if holiday_weekdays and not holiday_df.empty:
                    # 移除原對應資料
                    pd_data = pd_data.loc[~pd_data['week'].isin(holiday_weekdays)]

                    duplicated = []
                    for w in holiday_weekdays:
                        # 只改 week 欄位，其餘欄位原樣
                        tmp = holiday_df.copy(deep=False)
                        tmp = tmp.assign(week=w)
                        duplicated.append(tmp)

                    if duplicated:
                        pd_data = pd.concat([pd_data] + duplicated, ignore_index=True)

                pd_data = pd_data.replace({np.nan: None})
                pd_rnt[ApiConst.SCHEDULE.value] = pd_data.to_dict('records')
                pd_res = [pd_rnt]

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] electric schedule detail')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            week = payload[ApiConst.WEEK.value] if 'week' in payload else None
            start_time = payload[ApiConst.START_TIME.value] if 'start_time' in payload else None
            end_time = payload[ApiConst.END_TIME.value] if 'end_time' in payload else None
            _type = payload[ApiConst.TYPE.value] if 'type' in payload else None
            soc = payload[ApiConst.SOC.value] if 'soc' in payload else None
            kw = payload.get(ApiConst.KW.value, None)

            if _id:
                # check permission
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.ELECTRIC_SCHEDULE_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update electric schedule detail')
                pd_data = self.dao.update_electric_schedule_detail(_id, week, start_time, end_time, _type, soc, kw)
            else:
                parent_id = payload.get(ApiConst.PARENT_ID.value, None)
                if parent_id is None:
                    raise Exception('parent id is required.')

                # check permission
                self.logger.info('check permission [create-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.ELECTRIC_SCHEDULE_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create electric schedule detail')
                pd_data = self.dao.create_electric_schedule_detail(
                    parent_id, _id, week, start_time, end_time, _type, soc, kw)

            pd_data = pd_data.replace({np.nan: None})
            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] electric schedule detail')
        try:
            # check permission
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.ELECTRIC_SCHEDULE_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('delete electric schedule detail')
            _id = request.get_json()[ApiConst.ID.value]
            self.dao.delete_electric_schedule_detail([_id])
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None
