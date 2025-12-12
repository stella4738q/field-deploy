# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class AlertHistoricalThinjs(Resource):

    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('alert historical thinjs')
        pd_res = []
        try:
            field_id = config[ConfigConstant.APP.value][ConfigConstant.FIELD_ID.value]
            equipment_id = request.args[ApiConst.EQUIPMENT_ID.value] if ApiConst.EQUIPMENT_ID.value in request.args else None
            start_time = request.args[ApiConst.START_TIME.value]
            end_time = request.args[ApiConst.END_TIME.value]
            title = request.args[ApiConst.TITLE.value] if ApiConst.TITLE.value in request.args else None
            code = request.args[ApiConst.CODE.value] if ApiConst.CODE.value in request.args else None
            message = request.args[ApiConst.MESSAGE.value] if ApiConst.MESSAGE.value in request.args else None
            level = request.args[ApiConst.LEVEL.value] if ApiConst.LEVEL.value in request.args else None
            order_field = request.args[ApiConst.ORDER_FIELD.value] \
                if ApiConst.ORDER_FIELD.value in request.args.keys() else ApiConst.TIME.value
            order_type = request.args[ApiConst.ORDER_TYPE.value] \
                if ApiConst.ORDER_TYPE.value in request.args.keys() else ApiConst.ASC.value
            page = request.args[ApiConst.PAGE.value] if ApiConst.PAGE.value in request.args.keys() else 1
            limit = request.args[ApiConst.LIMIT.value] if ApiConst.LIMIT.value in request.args.keys() else 10
            offset = (int(page) - 1) * int(limit)

            sdate = datetime.strptime(start_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            edate = datetime.strptime(end_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            result_dict = dao.get_alarm_historical(sdate, edate, field_id, equipment_id, title, code, message, level,
                                                   order_field, order_type, int(limit), offset)
            if not result_dict['data'].empty:
                result_dict['data'] = result_dict['data'].replace({np.nan: None})
                result_dict['data'] = result_dict['data'].dropna(subset=['done_time'])
                if result_dict['data'].empty:
                    result_dict['total_count'] = 0
                    logger.debug('\nraw data: \n{}\n'.format(result_dict['data'].head(3)))

            result_dict['data'] = result_dict['data'].to_dict('records')
            pd_res = result_dict
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None