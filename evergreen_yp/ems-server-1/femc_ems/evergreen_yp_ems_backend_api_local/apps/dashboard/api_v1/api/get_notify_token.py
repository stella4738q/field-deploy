# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import numpy as np
from flask import request, session
from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource

class GETNotifytoken(Resource):
    logger = Logger().create('Evergreen API - notify token', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] notify_token')
        pd_res = []

        try:
            # check permission
            self.logger.info('check permission')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.NOTIFY_TOKEN_GET.value]:
                raise Exception('You dont have permission to access.')

            _id = None if request.args.get(ApiConst.ID_.value) == '' else request.args.get(ApiConst.ID_.value)
            name = None if request.args.get(ApiConst.NAME.value) == '' else request.args.get(ApiConst.NAME.value)
            token = None if request.args.get(ApiConst.TOKEN.value) == '' else request.args.get(ApiConst.TOKEN.value)

            self.dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = self.dao.get_notify_token(_id=_id, name=name, token=token)

            pd_data = pd_data.replace({np.nan: None, 'nan': None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] notify_token')
        pd_res = []

        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID_.value] if '_id' in payload else None
            name = payload[ApiConst.NAME.value] if 'name' in payload else None
            token = payload[ApiConst.TOKEN.value] if 'token' in payload else None

            pd_notify_token = self.dao.get_notify_token(_id=_id)
            pd_notify_token = pd_notify_token['_id'].tolist() if not pd_notify_token.empty else []
            # 判斷id是否已存在db裡
            if _id in pd_notify_token:

                # check permission
                self.logger.info('check permission')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.NOTIFY_TOKEN_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update notify_token')
                pd_data = self.dao.update_notify_token(_id=_id, name=name, token=token)
            else:
                # check permission
                self.logger.info('check permission')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.NOTIFY_TOKEN_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create notify_token')
                pd_data = self.dao.create_notify_token(_id=_id, name=name, token=token)

            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] notify_token')
        user_info: UserData = session[token_module.auth_session_key]

        try:
            # check permission
            self.logger.info('check permission [modify-operation]')
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.NOTIFY_TOKEN_DELETE.value]:
                raise Exception('You dont have permission to access.')

            _id = request.get_json()[ApiConst.ID_.value]
            self.dao.delete_notify_token([_id])
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
