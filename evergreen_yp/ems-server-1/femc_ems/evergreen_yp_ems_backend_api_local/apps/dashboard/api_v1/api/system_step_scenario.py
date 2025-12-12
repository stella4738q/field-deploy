# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class SystemStepScenario(Resource):
    """
    步階腳本設定
    """
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system step scenario')
        pd_res = []
        try:
            _id = None
            code = None
            name = None
            step_second = None
            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.CODE.value in request.args:
                code = request.args[ApiConst.CODE.value]
            if ApiConst.NAME.value in request.args:
                name = request.args[ApiConst.NAME.value]
            if ApiConst.STEP_SECOND.value in request.args:
                step_second = request.args[ApiConst.STEP_SECOND.value]

            self.logger.info('get step scenario')
            pd_data = self.dao.get_step_scenario(_id=_id, code=code, name=name, step_second=step_second)
            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] system step scenario')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            code = payload[ApiConst.CODE.value] if 'code' in payload else None
            name = payload[ApiConst.NAME.value] if 'name' in payload else None
            data = payload[ApiConst.DATA.value] if 'data' in payload else None
            step_second = payload[ApiConst.STEP_SECOND.value] if 'step_second' in payload else None

            if _id:
                # check permission
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_STEP_SCENARIO_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update step scenario')
                pd_data = self.dao.update_step_scenario(_id=_id, code=code, name=name, data=data,
                                                        step_second=step_second)
            else:
                # check permission
                self.logger.info('check permission [create-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.SYSTEM_STEP_SCENARIO_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create step scenario')
                pd_data = self.dao.create_step_scenario(_id=_id, code=code, name=name, data=data,
                                                        step_second=step_second)

            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] system step scenario')
        try:
            # check permission
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_STEP_SCENARIO_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('delete step scenario')
            _id = request.get_json()[ApiConst.ID_.value]
            self.dao.delete_step_scenario([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None
