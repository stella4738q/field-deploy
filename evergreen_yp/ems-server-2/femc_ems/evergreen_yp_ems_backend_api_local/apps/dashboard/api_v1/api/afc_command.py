from __future__ import absolute_import, print_function

import glob
from flask import request
import os
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.CONFIG_ROOT_PATH.value]


class AFCCommand(Resource):
    """
    AFC命令下發
    """
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] AFC command status')
        try:
            case_code = request.args[ApiConst.CASE_CODE.value]

            system_status = None
            for f in glob.glob(os.path.join(f'{temp_folder}', case_code, 'system_*')):
                system_status = os.path.basename(f)
            message = system_status if system_status else ''
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] AFC command')
        try:
            payload = request.get_json()
            case_code = payload[ApiConst.CASE_CODE.value]
            command = payload[ApiConst.COMMAND.value]

            system_status = None
            for f in glob.glob(os.path.join(f'{temp_folder}', case_code, 'system_*')):
                system_status = os.path.basename(f)

            command_file_exist = glob.glob(os.path.join(f'{temp_folder}', case_code, 'command_*'))

            if system_status == 'system_stopped' or system_status == 'system_started' or \
                    system_status == 'system_testing' or system_status == 'system_test_stop' or \
                    system_status == 'system_error':
                if len(command_file_exist) > 0:
                    raise Exception('Command file is exist.')
                with open(os.path.join(f'{temp_folder}', case_code, command), 'w'):
                    print(f'change status to {command}')
            elif system_status is None:
                raise Exception('System is not running.')
            else:
                raise Exception('System is running.')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message}, 200, None
