# -*- coding: utf-8 -*-

from dashboard_lib.geo_location import coordination

from flask import request
from apps.dashboard import log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class GeoLocation(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('geo location')
        res = []
        try:
            address = request.args[ApiConst.ADDRESS.value]
            URL = "https://www.google.com/maps/place?q=" + address
            res = coordination(URL)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': res}, 200, None