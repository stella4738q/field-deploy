# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime
import json
import numpy as np
from flask import request
import urllib3
import requests
import time
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, FileExtension
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class GetPostData(Resource):

    def post(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('get post data')
        res = ''
        try:
            payload = request.get_json()
            url = payload[ApiConst.URL.value]
            post_parameter = payload[ApiConst.PARAMETER.value]
            post_response = requests.post(url, json=post_parameter)
            res = post_response.content
            res = res.decode("utf-8-sig")
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': res}, 200, None