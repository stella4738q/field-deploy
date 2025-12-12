# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from apps.dashboard import token_module
from utility.token_module import token_required
from logging_utils.logger import Logger
from . import Resource


class SystemBidAmount(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('system bid amount')
        pd_res = None
        try:
            field_id = request.args[ApiConst.FIELD_ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dict_data = dao.get_total_bid_amount(field_id)

            pd_res = [dict_data]
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None