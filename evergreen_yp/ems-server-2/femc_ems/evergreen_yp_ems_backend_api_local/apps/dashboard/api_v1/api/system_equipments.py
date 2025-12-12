# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class SystemEquipments(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system equipments')
        pd_res = []
        try:
            """
            equipment_type
            0: AIR, 3: RELAY, 4: PCS, 5: BMS, 6: RACK, 7: METER, 8:UPS, 9:IO 
            """
            _id = None
            parent_id = None
            case_id = None
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            code = None
            equipment_type = None
            name = None
            brand = None
            ip = None
            port = None
            capacity = None

            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.PARENT_ID.value in request.args:
                parent_id = request.args[ApiConst.PARENT_ID.value]
            if ApiConst.CASE_ID.value in request.args:
                case_id = request.args[ApiConst.CASE_ID.value]
            if ApiConst.CODE.value in request.args:
                code = request.args[ApiConst.CODE.value]
            if ApiConst.EQUIPMENT_TYPE.value in request.args:
                equipment_type = request.args[ApiConst.EQUIPMENT_TYPE.value]
            if ApiConst.NAME.value in request.args:
                name = request.args[ApiConst.NAME.value]
            if ApiConst.BRAND.value in request.args:
                brand = request.args[ApiConst.BRAND.value]
            if ApiConst.IP.value in request.args:
                ip = request.args[ApiConst.IP.value]
            if ApiConst.PORT.value in request.args:
                port = request.args[ApiConst.PORT.value]
            if ApiConst.CAPACITY.value in request.args:
                capacity = request.args[ApiConst.CAPACITY.value]

            self.logger.info('get equipments')
            pd_data = self.dao.get_system_equipment(_id=_id, parent_id=parent_id, case_id=case_id, field_id=field_id,
                                                    code=code, equipment_type=equipment_type, name=name,
                                                    brand=brand, ip=ip, port=port, capacity=capacity)
            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        """
        案場僅可修改設備，不可新增
        期初會將設備資料建立
        :return:
        """
        self.logger.info('[post] system equipments')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload.get(ApiConst.ID_.value, None)
            if not _id:
                raise Exception('設備ID為必要欄位')

            case_id = payload.get(ApiConst.CASE_ID.value, None)
            parent_id = payload.get(ApiConst.PARENT_ID.value, None)
            code = payload.get(ApiConst.CODE.value, None)
            equipment_type = payload.get(ApiConst.EQUIPMENT_TYPE.value, None)
            name = payload.get(ApiConst.NAME.value, None)
            brand = payload.get(ApiConst.BRAND.value, None)
            ip = payload.get(ApiConst.IP.value, None)
            port = payload.get(ApiConst.PORT.value, None)
            capacity = payload.get(ApiConst.CAPACITY.value, None)
            unit_id = payload.get(ApiConst.UNIT_ID.value, None)

            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            # check permission
            self.logger.info('check permission [modify-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_EQUIPMENTS_POST_UPDATE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('update resources')
            pd_data = self.dao.update_system_equipment(_id=_id, parent_id=parent_id, case_id=case_id,
                                                       field_id=field_id, code=code, equipment_type=equipment_type,
                                                       name=name, brand=brand, ip=ip, port=port, capacity=capacity,
                                                       unit_id=unit_id)
            pd_data = pd_data.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
            pd_res = pd_data.to_dict('records')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] system equipments')
        try:
            # check permission
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_EQUIPMENTS_DELETE.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('delete resources')
            _id = request.get_json()[ApiConst.ID_.value]
            self.dao.delete_system_equipment([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
