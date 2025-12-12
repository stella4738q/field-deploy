# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class SystemDropdown(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system dropdown')
        message = SUCCESS_MESSAGE
        pd_res = list()
        try:
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            args = request.args
            dropdown_type = args.get(ApiConst.DROPDOWN_TYPE.value, None)
            if dropdown_type:
                self.logger.debug(f'dropdown_type: {dropdown_type}')
                if dropdown_type.lower() == 'alarm_equipments':
                    equipments = self.dao.get_alarm_equipment(field_id=field_id)
                    if equipments:
                        pd_res = [{
                            "id": eq,
                            "name": eq
                        } for eq in equipments]
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
