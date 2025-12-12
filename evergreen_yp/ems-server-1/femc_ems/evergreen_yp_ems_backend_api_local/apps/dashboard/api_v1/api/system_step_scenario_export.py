from __future__ import absolute_import, print_function

import os
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.CONFIG_ROOT_PATH.value]


class SystemStepScenarioExport(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] system step scenario export')
        try:
            payload = request.get_json()
            code = payload[ApiConst.CODE.value] if 'code' in payload else None
            case_code = payload[ApiConst.CASE_CODE.value] if 'case_code' in payload else None

            self.logger.info('get step scenario')
            step_data = None
            pd_data = self.dao.get_step_scenario(code=code)
            if not pd_data.empty:
                step_data = pd_data[ApiConst.DATA.value][0]

            config_temp_path = os.path.join(f'{temp_folder}', case_code, 'step_scenario_data.txt')

            with open(config_temp_path, "w") as output:
                output.write(str(step_data))

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
