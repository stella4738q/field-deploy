from __future__ import absolute_import, print_function

import glob
import os

from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from logging_utils.logger import Logger
from utility.token_module import token_required
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.CONFIG_ROOT_PATH.value]


class AFCMonitorExport(Resource):
    """
    AFC設定檔暫存轉正式
    """
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] AFC monitor export')
        try:
            payload = request.get_json()
            case_code = payload[ApiConst.CASE_CODE.value]

            config_temp = glob.glob(os.path.join(f'{temp_folder}', case_code, 'config_temp.ini'))

            if len(config_temp) > 0:
                os.rename(config_temp[0], os.path.join(f'{temp_folder}', case_code, 'config.ini'))
            else:
                raise Exception('First, create config.ini file.')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
