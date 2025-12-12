# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, make_response, jsonify, session
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from utility.api_response import ApiResponse

from . import Resource


class PermissionUserField(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] permission user field')
        rtn_list = []
        try:
            user_id = request.args[ApiConst.USER_ID.value] if ApiConst.USER_ID.value in request.args else None
            if not user_id:
                raise Exception("請輸入 'user_id' ")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_user_fields(user_id)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            rtn_list = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': rtn_list}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[post] permission user field')
        pd_res = []
        try:
            payload = request.get_json()
            user_id = payload[ApiConst.USER_ID.value]
            field_id = payload[ApiConst.FIELD_ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.create_user_fields(user_id, field_id)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return  {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[delete] permission user field')
        try:
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                raise Exception('You dont have permission to access.')

            payload = request.get_json()
            _id = payload[ApiConst._ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_user_fields([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None