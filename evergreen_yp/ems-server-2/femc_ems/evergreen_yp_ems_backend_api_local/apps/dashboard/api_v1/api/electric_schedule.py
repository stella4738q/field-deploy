# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class ElectricSchedule(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] electric schedule')
        pd_res = []
        try:
            _id = None
            name = None
            memo = None

            if ApiConst.ID_.value in request.args:
                _id = request.args[ApiConst.ID_.value]
            if ApiConst.NAME.value in request.args:
                name = request.args[ApiConst.NAME.value]
            if ApiConst.MEMO.value in request.args:
                memo = request.args[ApiConst.MEMO.value]

            # get schedule
            self.logger.info('get electric schedule')
            pd_data = self.dao.get_electric_schedule(_id=_id, name=name, memo=memo)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post] electric schedule')
        pd_res = []
        try:
            payload = request.get_json()
            _id = payload.get(ApiConst.ID_.value, None)
            name = payload.get(ApiConst.NAME.value, None)
            memo = payload.get(ApiConst.MEMO.value, None)

            if _id:
                # check permission
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][PermissionConst.ELECTRIC_SCHEDULE_POST_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('update electric schedule')
                pd_data = self.dao.update_electric_schedule(_id, name, memo)
            else:
                # check permission
                self.logger.info('check permission [create-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and \
                        field not in allow_field or \
                        not user_info.user_field_permission[field][PermissionConst.ELECTRIC_SCHEDULE_POST_CREATE.value]:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create electric schedule')
                pd_data = self.dao.create_electric_schedule(_id, name, memo)

            pd_data = pd_data.replace({np.nan: None})
            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        self.logger.info('[delete] Electric Schedule')
        try:
            # check permission
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            # 刪除頭表，同時需要有刪除detail權限
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][PermissionConst.ELECTRIC_SCHEDULE_DELETE.value] or \
                    not user_info.user_field_permission[field][PermissionConst.ELECTRIC_SCHEDULE_DETAIL_DELETE.value]:
                raise Exception('You dont have permission to access.')

            _id = request.get_json()[ApiConst.ID.value]
            # 先判斷有沒有被引用到
            system_settings_df = self.dao.get_system_setting(key='charge_type_rundown')
            if not system_settings_df.empty:
                current_set = system_settings_df.iloc[0]['value']
                if _id == current_set:
                    raise Exception('此腳本已被系統設定引用，請先進行修正.')

            self.logger.info('delete electric schedule')
            # 先刪除detail，在刪除頭表
            self.dao.delete_electric_schedule_detail_by_parent(parent_id=_id)
            self.dao.delete_electric_schedule([_id])
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None
