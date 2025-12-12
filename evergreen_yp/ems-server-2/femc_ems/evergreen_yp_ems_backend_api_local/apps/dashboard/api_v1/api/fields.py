# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.geo_location import coordination
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class Fields(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] fields')
        pd_res = []
        try:
            logger.info('check permission [query]')
            allow_field = None
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin :
                allow_field = [key for key in user_info.user_field_permission.keys()]
                if allow_field is None:
                    allow_field = list()

            name = None
            code = None
            address = None
            type = None
            ip = None
            if ApiConst.CODE.value in request.args:
                code = request.args[ApiConst.CODE.value]
            if ApiConst.NAME.value in request.args:
                name = request.args[ApiConst.NAME.value]
            if ApiConst.ADDRESS.value in request.args:
                address = request.args[ApiConst.ADDRESS.value]
            if ApiConst.TYPE.value in request.args:
                type = request.args[ApiConst.TYPE.value]
            if ApiConst.IP.value in request.args:
                ip = str(request.args[ApiConst.IP.value])

            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_fields(code=code, ip=ip, name=name,  address=address,  type=type, allow_field=allow_field)
            pd_data = pd_data.replace({np.nan: None, 'nan': None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[post] fields')
        pd_res = []
        try:
            logger.info('check permission [operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin:
                raise Exception('You dont have permission to access.')

            payload = request.get_json()
            uid = payload[ApiConst.UID.value] if ApiConst.UID.value in payload else None
            code = payload[ApiConst.CODE.value] if ApiConst.CODE.value in payload else None
            name = payload[ApiConst.NAME.value] if ApiConst.NAME.value in payload else None
            address = payload[ApiConst.ADDRESS.value] if ApiConst.ADDRESS.value in payload else None
            type = payload[ApiConst.TYPE.value] if ApiConst.TYPE.value in payload else None
            ip = payload[ApiConst.IP.value] if ApiConst.IP.value in payload else None
            company_id = payload[ApiConst.COMPANY_ID.value] if ApiConst.COMPANY_ID.value in payload else None
            user_id = payload[ApiConst.USER_ID.value] if ApiConst.USER_ID.value in payload else None
            middle_page = payload[ApiConst.MIDDLE_PAGE.value] if ApiConst.MIDDLE_PAGE.value in payload else None

            if not address:
                geo_location = ""
            else:
                URL = "https://www.google.com/maps/place?q=" + address
                geo_location = coordination(URL)

            dao = StorageFactory(config).get_dao_factory().get_dao()
            if uid:
                logger.info('update field')
                pd_data = dao.update_field(uid, code, ip, name, address, geo_location, type, company_id, user_id, middle_page)
            else:
                logger.info('create field')
                if type is None or len(type) == 0:
                    raise ValueError('type is not none')
                pd_data = dao.create_field(uid, code, ip, name, address, geo_location, type, company_id, user_id, middle_page)

            pd_data = pd_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[delete] fields')
        try:
            logger.info('check permission [operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin:
                raise Exception('You dont have permission to access.')

            uid = request.get_json()[ApiConst.UID.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_field([uid])
            dao.delete_user_fields_by_field_id(uid)
            pd_data = dao.get_resources(field_id=uid)
            resources_id = [resource_dict[ApiConst.ID_.value] for resource_dict in
                            FeatureFunc.result_dict(logger, pd_data)]
            dao.delete_resources(resources_id)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message}, 200, None