from __future__ import absolute_import, print_function

import configparser
import json
import os
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from logging_utils.logger import Logger
from utility.token_module import token_required
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.CONFIG_ROOT_PATH.value]


class AFCMonitor(Resource):
    """
    AFC設定檔操作
    """
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('AFC monitor')
        file_dict = {}
        return_settings = {
            "config": None,
            "config_temp": None
        }

        try:
            case_code = request.args[ApiConst.CASE_CODE.value]

            dir_path = os.path.join(f'{temp_folder}', case_code)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            config_file = open('configs/afc_default_config.json')
            config_file = json.load(config_file)
            for i in range(2):
                if i == 0:
                    # current_settings
                    path = os.path.join(dir_path, 'config.ini')
                    if os.path.isfile(path):
                        _config = configparser.ConfigParser()
                        _config.read(path)
                        for item in _config.sections():
                            info = dict(_config.items(item))
                            file_dict[item] = info
                    else:
                        file_dict = config_file
                    return_settings['config'] = file_dict
                elif i == 1:
                    # temp_settings
                    path = os.path.join(dir_path, 'config_temp.ini')
                    if os.path.isfile(path):
                        _config = configparser.ConfigParser()
                        _config.read(path)
                        for item in _config.sections():
                            info = dict(_config.items(item))
                            file_dict[item] = info
                        return_settings['config_temp'] = file_dict
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': return_settings}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] AFC monitor')
        try:
            payload = request.get_json()
            case_code = payload[ApiConst.CASE_CODE.value]
            data = payload[ApiConst.DATA.value]
            config_object = configparser.ConfigParser()
            for key, value in data.items():
                config_object[key] = value

            dir_path = os.path.join(f'{temp_folder}', case_code)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            path = os.path.join(dir_path, 'config_temp.ini')
            with open(path, 'w') as configfile:
                config_object.write(configfile)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
