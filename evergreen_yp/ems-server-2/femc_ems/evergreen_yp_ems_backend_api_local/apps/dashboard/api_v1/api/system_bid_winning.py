# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime

import numpy as np
import pandas as pd
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from apps.dashboard import token_module
from utility.token_module import token_required
from logging_utils.logger import Logger
from . import Resource


class SystemBidWinning(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('system bid winning')
        pd_res = []
        try:
            field_id = request.args[ApiConst.FIELD_ID.value]
            date_time = request.args[ApiConst.DATE_TIME.value]

            if not date_time:
                date_time = datetime.now().strftime("%Y%m%d%H%M%S")

            sdate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 00:00:00")
            edate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 23:59:59")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_winning(sdate, edate, field_id)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            if not pd_data.empty:
                pd_data['start_time'] = pd.to_datetime(pd_data["start_time"])
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None