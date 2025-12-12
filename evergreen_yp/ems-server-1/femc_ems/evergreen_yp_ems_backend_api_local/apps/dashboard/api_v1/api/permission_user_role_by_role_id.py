# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class PermissionUserRoleByRoleId(Resource):

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('permission user role by role id')
        try:
            role_id = request.get_jon()[ApiConst.ROLE_ID.value]

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_user_roles_by_role_id(role_id)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None