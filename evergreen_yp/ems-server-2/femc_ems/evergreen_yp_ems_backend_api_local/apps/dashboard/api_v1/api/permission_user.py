# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session, make_response, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class PermissionUser(Resource):
    """
    使用者新增、修改、刪除
    """

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] permission user')
        try:
            user_info: UserData = session[token_module.auth_session_key]

            # 2024.06.06 使用者權限修正
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            _id = request.args[ApiConst.ID.value]
            name = request.args[ApiConst.NAME.value]
            email = request.args[ApiConst.EMAIL.value]
            mobile = request.args[ApiConst.MOBILE.value]
            is_admin = 0  # request.args.get(ApiConst.IS_ADMIN.value, False)
            account = request.args[ApiConst.ACCOUNT.value]
            enable = request.args[ApiConst.ENABLE.value]

            company = user_info.company if not user_info.is_admin else None

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_users(_id, name, email, mobile, is_admin, account,
                                    enable if enable else None, company=company)
            if not pd_data.empty:
                del pd_data['password']
                del pd_data['salt']

                if not user_info.is_admin:
                    del pd_data['is_admin']
                    del pd_data['is_field_admin']
                    del pd_data['company']

                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[post] permission user')
        try:
            user_info: UserData = session[token_module.auth_session_key]

            # 2024.06.06 使用者權限修正
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            payload = request.get_json()
            _id = payload.get(ApiConst.ID.value, None)
            name = payload.get(ApiConst.NAME.value)
            email = payload.get(ApiConst.EMAIL.value, None)
            mobile = payload.get(ApiConst.MOBILE.value, None)
            is_admin = payload.get(ApiConst.IS_ADMIN.value, False)
            account = payload.get(ApiConst.ACCOUNT.value)
            password = payload.get(ApiConst.PASSWORD.value)
            enable = payload.get(ApiConst.ENABLE.value)

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()

            if user_info.is_admin:
                # 如系統管理員，可額外輸入是否為案場管理員
                is_field_admin = payload[ApiConst.IS_FIELD_ADMIN.value] \
                    if ApiConst.IS_FIELD_ADMIN.value in payload else False
            else:
                is_field_admin = None

            if _id:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.PERMISSION_USER_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                logger.info('update permission user')
                pd_data = dao.update_user(_id, name, email, mobile, is_admin, is_field_admin, enable)
            else:
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.PERMISSION_USER_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                logger.info('create permission user')

                # get company
                company = None
                company_df = dao.get_company(is_main=True)
                if not company_df.empty:
                    company = company_df.iloc[0]['_id']
                pd_data = dao.create_user(name, email, account, password, company, is_admin if is_admin else 0,
                                          is_field_admin if is_field_admin else 0, enable if enable else 1, mobile)

            if not pd_data.empty:
                del pd_data['password']
                del pd_data['salt']

                if not user_info.is_admin:
                    del pd_data['is_admin']
                    del pd_data['is_field_admin']
                    del pd_data['company']

                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def delete(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
        logger.info('[delete] permission user')
        try:
            user_info: UserData = session[token_module.auth_session_key]

            # 2024.06.06 使用者權限修正
            # if not user_info.is_admin and not user_info.is_field_admin:
            #     raise Exception('You dont have permission to access.')

            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.PERMISSION_USER_DELETE.value]:
                raise Exception('You dont have permission to access.')

            _id = request.get_json()[ApiConst.ID.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_user([_id])

            # 刪除時，自動刪除user_field、user_role
            dao.delete_user_fields_by_user_id([_id])
            dao.delete_user_roles_by_user_id([_id])
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
