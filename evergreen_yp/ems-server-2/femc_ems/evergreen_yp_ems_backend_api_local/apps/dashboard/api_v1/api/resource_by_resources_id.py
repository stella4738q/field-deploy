# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g, session
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource
from .. import schemas


class ResourceByResourcesId(Resource):
    logger = Logger().create('Local EMS API - resource by resources Id', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get]')
        pd_res = []
        try:
            resources_id = request.args.get(ApiConst.RESOURCES_ID.value)
            code = request.args.get(ApiConst.CODE.value)
            equipment_type = request.args.get(ApiConst.EQUIPMENT_TYPE.value)
            name = request.args.get(ApiConst.NAME.value)
            capacity = request.args.get(ApiConst.CAPACITY.value)
            communication = request.args.get(ApiConst.COMMUNICATION.value)
            implement = request.args.get(ApiConst.IMPLEMENT.value)
            field_id = request.args.get(ApiConst.FIELD_ID.value)
            case_id = request.args.get(ApiConst.CASE_ID.value)

            pd_data = self.dao.get_resources(
                _id=resources_id, code=code, equipment_type=equipment_type, name=name, capacity=capacity,
                communication=communication, implement=implement, field_id=field_id, case_id=case_id)
            pd_res = FeatureFunc.result_dict(self.logger, pd_data)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post]')
        pd_res = []
        try:
            payload = request.get_json()
            resources_id = payload[ApiConst.RESOURCES_ID.value]
            code = payload[ApiConst.CODE.value]
            equipment_type = payload[ApiConst.EQUIPMENT_TYPE.value]
            name = payload[ApiConst.NAME.value]
            capacity = payload[ApiConst.CAPACITY.value]
            communication = payload[ApiConst.COMMUNICATION.value]
            implement = payload[ApiConst.IMPLEMENT.value]
            field_id = payload[ApiConst.FIELD_ID.value]
            case_id = payload[ApiConst.CASE_ID.value]

            if resources_id:
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                if not user_info.is_admin and not user_info.is_field_admin:
                    allow_field = user_info.user_field_permission.keys()
                    if len(user_info.user_field_permission) == 0 or \
                            field_id not in allow_field or \
                            not user_info.user_field_permission[field_id][
                                PermissionConst.RESOURCE_BY_RESOURCEID_POST_UPDATE.value]:
                        raise Exception('You dont have permission to access.')

                self.logger.info('update resource')
                pd_data = self.dao.update_resources(
                    _id=resources_id, code=code, equipment_type=equipment_type, name=name, capacity=capacity,
                    communication=communication, implement=implement, field_id=field_id, case_id=case_id)
            else:
                self.logger.info('check permission [add-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                if not user_info.is_admin and not user_info.is_field_admin:
                    allow_field = user_info.user_field_permission.keys()
                    if len(user_info.user_field_permission) == 0 or \
                            field_id not in allow_field or \
                            not user_info.user_field_permission[field_id][
                                PermissionConst.RESOURCE_BY_RESOURCEID_POST_CREATE.value]:
                        raise Exception('You dont have permission to access.')

                self.logger.info('create resource')
                pd_data = self.dao.create_resources(
                    _id=resources_id, code=code, equipment_type=equipment_type, name=name, capacity=capacity,
                    communication=communication, implement=implement, field_id=field_id, case_id=case_id)
            pd_res = FeatureFunc.result_dict(self.logger, pd_data)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete]')
        pd_res = []
        try:
            resources_id = request.get_json()[ApiConst.RESOURCES_ID.value]

            field_id = self.dao.get_resources(_id=resources_id)['field_id'].tolist()[0]
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) == 0 or \
                        field_id not in allow_field or \
                        not user_info.user_field_permission[field_id][
                            PermissionConst.RESOURCE_BY_RESOURCEID_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

            self.dao.delete_resources([resources_id])
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
