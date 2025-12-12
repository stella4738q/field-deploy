# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst, ConfigConstant
from apps.dashboard.utils import TRUE_LIST, FALSE_LIST
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class GETNotifyrule(Resource):
    logger = Logger().create('Evergreen API - post_notify_rule', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        """
            code:

        """
        logger = Logger().create('Evergreen API - get_notify_rule', level=logging_level, log_path=log_path)
        logger.info('[get] notify_rule')
        pd_res = []

        try:
            name = None if request.args.get(ApiConst.NAME.value) == '' else request.args.get(ApiConst.NAME.value)
            code = None if request.args.get(ApiConst.CODE.value) == '' else request.args.get(ApiConst.CODE.value)
            _id = None if request.args.get(ApiConst.ID_.value) == '' else request.args.get(ApiConst.ID_.value)
            description = None if request.args.get(ApiConst.DESCRIPTION.value) == '' else request.args.get(ApiConst.DESCRIPTION.value)

            pd_data = self.dao.get_notify_rule(_id=_id, code=code, name=name, description=description)

            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE

        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] notify_rule')

        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            name = payload[ApiConst.NAME.value] if 'name' in payload else None
            code = payload[ApiConst.CODE.value] if 'code' in payload else None
            description = payload[ApiConst.DESCRIPTION.value] if 'description' in payload else None

            if _id:
                # check permission
                self.logger.info('check permission')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.NOTIFY_RULE_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update notify_rule')
                pd_data = self.dao.update_notify_rule(_id=_id, code=code, name=name, description=description)
            else:
                # check permission
                self.logger.info('check permission')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.NOTIFY_RULE_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                # check code沒有存在才新增
                pd_data = self.dao.get_notify_rule(code=code)
                if not pd_data.empty:
                    raise ValueError('Code exists.')

                self.logger.info('create notify_rule')
                pd_data = self.dao.create_notify_rule(_id=_id, code=code, name=name, description=description)

            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE

        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[delete] notify_rule')

        try:
            _id = request.args[ApiConst.ID_.value]

            # check permission
            self.logger.info('check permission')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.NOTIFY_RULE_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.dao.delete_notify_rule([_id])
            message = SUCCESS_MESSAGE

        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None
