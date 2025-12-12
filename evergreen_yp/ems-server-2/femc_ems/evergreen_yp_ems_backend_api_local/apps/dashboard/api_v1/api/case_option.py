# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g, session
import datetime
import pandas as pd
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc, NONE_LIST, TRUE_LIST, FALSE_LIST
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource
from .. import schemas


class CaseOption(Resource):
    logger = Logger().create('Local EMS API - resource by case Id', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get]')
        pd_res = []
        try:
            # check permission
            self.logger.info('check permission [query]')
            user_info: UserData = session[token_module.auth_session_key]
            field_list = [key for key in user_info.user_field_permission.keys()]
            pd_system_equipment = self.dao.get_system_equipment(field_id=field_list)
            case_ids = pd_system_equipment['case_id'].tolist() if not pd_system_equipment.empty else []
            case_ids = [case_id for case_id in case_ids if case_id is not None and case_id != 'None']

            permission_case_code = pd.DataFrame()
            if case_ids:
                permission_case_code = self.dao.get_cases(_id=case_ids)

            if not permission_case_code.empty:
                pd_cases = permission_case_code.rename(columns={'_id': ApiConst.CASE_ID.value})
                if ApiConst.PERFORMANCE_LEVEL.value in list(pd_cases.columns):
                    pd_cases = pd_cases.drop([ApiConst.PERFORMANCE_LEVEL.value], axis=1)
                pd_res = FeatureFunc.result_dict(self.logger, pd_cases)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
