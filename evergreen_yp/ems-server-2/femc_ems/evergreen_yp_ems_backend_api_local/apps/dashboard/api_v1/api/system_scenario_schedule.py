# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session
from datetime import datetime
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.geo_location import coordination
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class SystemScenarioSchedule(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system scenario schedule')
        pd_res = []
        try:
            _id = None
            case_id = None
            scenario_id = None
            start_time = None
            end_time = None
            repeat = None
            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.CASE_ID.value in request.args:
                case_id = request.args[ApiConst.CASE_ID.value]
            if ApiConst.SCENARIO_ID.value in request.args:
                scenario_id = request.args[ApiConst.SCENARIO_ID.value]
            if ApiConst.START_TIME.value in request.args:
                start_time = request.args[ApiConst.START_TIME.value]
                start_time = datetime.strptime(start_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            if ApiConst.END_TIME.value in request.args:
                end_time = request.args[ApiConst.END_TIME.value]
                end_time = datetime.strptime(end_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            if ApiConst.REPEAT.value in request.args:
                repeat = request.args[ApiConst.REPEAT.value]

            self.logger.info('get scenario schedule')
            pd_data = self.dao.get_scenario_schedule(_id=_id, case_id=case_id, scenario_id=scenario_id,
                                                     start_time=start_time, end_time=end_time, repeat=repeat)
            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] system scenario schedule')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            case_id = payload[ApiConst.CASE_ID.value] if 'case_id' in payload else None
            scenario_id = payload[ApiConst.SCENARIO_ID.value] if 'scenario_id' in payload else None
            start_time = payload[ApiConst.START_TIME.value] if 'start_time' in payload else None
            end_time = payload[ApiConst.END_TIME.value] if 'end_time' in payload else None
            repeat = payload[ApiConst.REPEAT.value] if 'repeat' in payload else None

            if _id:
                # check permission
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_SCENARIO_SCHEDULE_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update scenario schedule')
                pd_data = self.dao.update_scenario_schedule(_id=_id, case_id=case_id, scenario_id=scenario_id,
                                                            start_time=start_time, end_time=end_time, repeat=repeat)
            else:
                # check permission
                self.logger.info('check permission [create-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_SCENARIO_SCHEDULE_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create scenario schedule')
                pd_data = self.dao.create_scenario_schedule(_id=_id, case_id=case_id, scenario_id=scenario_id,
                                                            start_time=start_time, end_time=end_time, repeat=repeat)

            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] system scenario schedule')
        try:
            # check permission
            self.logger.info('check permission [create-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_SCENARIO_SCHEDULE_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('delete scenario schedule')
            _id = request.get_json()[ApiConst.ID.value]
            self.dao.delete_scenario_schedule([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None
