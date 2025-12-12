# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime

import numpy as np
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class SystemSchedulingBalanced(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('system scheduling balanced')
        pd_res = []
        try:
            field_id = request.args[ApiConst.FIELD_ID.value]
            bid_id = request.args[ApiConst.BID_ID.value]
            equipment_id = request.args[ApiConst.EQUIPMENT_ID.value]
            date_time = request.args[ApiConst.DATE_TIME.value]
            order = request.args[ApiConst.ORDER.value]

            if not date_time:
                date_time = datetime.now().strftime("%Y%m%d%H%M%S")

            sdate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 00:00:00")
            edate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 23:59:59")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_balanced(sdate, edate, field_id, equipment_id, bid_id, order)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    # def post(self):
    #     rtn_list = []
    #     try:
    #         # pd_data = pd.read_csv('/media/sf_VMShareFolder/data/historical.csv')
    #
    #         date_time = request.args[ApiConst.DATE_TIME.value]
    #         cabinet = request.args[ApiConst.CABINET.value]
    #         command = request.args[ApiConst.COMMAND.value]
    #
    #         message = SUCCESS_MESSAGE
    #     except Exception as e:
    #         message = repr(e)
    #
    #     return {'message': message}, 200, None