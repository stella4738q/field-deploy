# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class PermissionUserRole(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] permission user role')
        pd_res = []
        try:
            user_id = request.args[ApiConst.USER_ID.value] if ApiConst.USER_ID.value in request.args else None
            if not user_id:
                raise Exception("請輸入 'user_id' ")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_user_roles(user_id)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[post] permission user role')
        pd_res = []
        try:
            payload = request.get_json()
            user_id = payload[ApiConst.USER_ID.value]
            role_id = payload[ApiConst.ROLE_ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.create_user_roles(user_id, role_id)
            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[delete] permission user role')
        try:
            post_data = request.get_json()
            if not post_data:
                raise Exception("post data error.")
            id_list = post_data[ApiConst.ID_LIST.value] if ApiConst.ID_LIST.value in post_data.keys() else None
            user_id = post_data[ApiConst.USER_ID.value] if ApiConst.USER_ID.value in post_data.keys() else None
            field_id = post_data[ApiConst.FIELD_ID.value] if ApiConst.FIELD_ID.value in post_data.keys() else None

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_user_roles(id_list, user_id, field_id)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None