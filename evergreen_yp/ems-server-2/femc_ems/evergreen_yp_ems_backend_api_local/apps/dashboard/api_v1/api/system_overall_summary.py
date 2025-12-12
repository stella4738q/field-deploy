# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session
from datetime import datetime
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from flask import request, make_response, jsonify
from . import Resource


class SystemOverallSummary(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[get] system overall summary')
        response_data = {
            'success': True,
            'message': '',
            ApiConst.DATA.value: {}
        }
        try:
            # check permission
            allow_field = None
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin:
                allow_field = [key for key in user_info.user_field_permission.keys()]
                if allow_field is None:
                    allow_field = list()

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            # get field type
            pd_field = dao.get_fields()
            field_type_list = pd_field[ApiConst.TYPE.value].tolist() if not pd_field.empty else []
            field_type = dict((item, field_type_list.count(item)) for item in set(field_type_list) if item != '' and (not isinstance(item, float) or not np.isnan(item)))

            # get resource equipment type
            solar_count = 0
            storage_count = 0
            pd_resource = dao.get_resources(allow_field=allow_field)
            equipment_type_list = pd_resource[ApiConst.EQUIPMENT_TYPE.value].tolist() if not pd_resource.empty else []
            for item in equipment_type_list:
                if item == 4:
                    solar_count = solar_count + 1
                else:
                    storage_count = storage_count + 1

            # get power today
            date_time = datetime.now().strftime("%Y%m%d%H%M%S")
            sdate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 00:00:00")
            edate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 23:59:59")
            pd_solar_execution = dao.get_solar_execution(sdate=sdate, edate=edate)
            today_power = pd_solar_execution[ApiConst.POWER.value].sum() / 1000 if not pd_solar_execution.empty else 0

            # get power history
            pd_solar = dao.get_solar_execution()
            power_history = pd_solar[ApiConst.POWER.value].sum() / 1000 if not pd_solar.empty else 0

            # get cumulative revenue
            cumulative_revenue = round(power_history * 3.2, 2)

            response_data[ApiConst.DATA.value][ApiConst.FIELD.value] = field_type
            response_data[ApiConst.DATA.value][ApiConst.CAPACITY.value] = {ApiConst.SOLAR.value: round(solar_count, 2),
                                                                           ApiConst.STORAGE.value: round(storage_count, 2)}
            response_data[ApiConst.DATA.value][ApiConst.GEN_POWER_TODAY.value] = round(today_power, 2)
            response_data[ApiConst.DATA.value][ApiConst.GEN_POWER_HISTORY.value] = round(power_history, 2)
            response_data[ApiConst.DATA.value][ApiConst.CUMULATIVE_REVENUE.value] = round(cumulative_revenue, 2)

        except Exception as e:
            response_data = {
                'success': False,
                'message': str(e),
                ApiConst.DATA.value: {}
            }
        return make_response(jsonify(response_data), 200)
