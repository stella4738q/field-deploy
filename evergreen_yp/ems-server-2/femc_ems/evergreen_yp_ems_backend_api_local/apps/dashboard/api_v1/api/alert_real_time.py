# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class AlertRealTime(Resource):
    """
    即時報警
    """

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('alert real time')
        pd_res = []
        try:
            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_alarm_real_time(None, None, None)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None