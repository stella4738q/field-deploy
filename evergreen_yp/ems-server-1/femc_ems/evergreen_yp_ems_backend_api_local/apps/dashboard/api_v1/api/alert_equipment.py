from __future__ import absolute_import, print_function

from datetime import datetime

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class AlertEquipment(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('alert equipment')
        pd_res = []
        try:
            # check permission
            logger.info('check permission')
            user_info: UserData = session[token_module.auth_session_key]
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            if not user_info.is_admin:
                if field_id not in user_info.user_field_permission.keys():
                    raise Exception('you dont have permission to access.')

            start_time = request.args[ApiConst.START_TIME.value]
            end_time = request.args[ApiConst.END_TIME.value]

            sdate = datetime.strptime(start_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            edate = datetime.strptime(end_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_result = dao.get_alarm_equipment(sdate, edate, field_id)
            logger.debug('\nraw data: \n{}\n'.format(pd_result.head(3)))
            equipment_list = list(set(pd_result[ApiConst.EQUIPMENT_ID.value])) if not pd_result.empty else None

            pd_res = equipment_list
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None