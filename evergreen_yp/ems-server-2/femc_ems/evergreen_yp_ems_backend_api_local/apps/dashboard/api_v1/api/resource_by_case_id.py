# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g, session
import datetime
import pandas as pd
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc, NONE_LIST, TRUE_LIST, FALSE_LIST
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource
from .. import schemas


class ResourceByCaseId(Resource):
    logger = Logger().create('Local EMS API - resource by case Id', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get]')
        pd_res = []
        try:
            case_id = None if request.args.get(ApiConst.CASE_ID.value) == '' else request.args.get(ApiConst.CASE_ID.value)
            code = None if request.args.get(ApiConst.CODE.value) == '' else request.args.get(ApiConst.CODE.value)
            service = None if request.args.get(ApiConst.SERVICE.value) == '' else request.args.get(ApiConst.SERVICE.value)
            status = request.args.get(ApiConst.STATUS.value)
            performance_level = None if request.args.get(ApiConst.PERFORMANCE_LEVEL.value) == '' else request.args.get(ApiConst.PERFORMANCE_LEVEL.value)
            input_column = [case_id, code, service, status, performance_level]
            status = True if status in TRUE_LIST else False if status in FALSE_LIST else None

            pd_cases = self.dao.get_cases(_id=case_id, code=code, service=service, status=status, performance_level=performance_level)
            _case_id_list = list(pd_cases[ApiConst.ID_.value]) if not pd_cases.empty else list()

            # check permission
            self.logger.info('check permission [query]')
            user_info: UserData = session[token_module.auth_session_key]
            field_list = [key for key in user_info.user_field_permission.keys()]
            pd_resource = self.dao.get_resources(field_id=field_list)
            case_ids = pd_resource['case_id'].tolist() if not pd_resource.empty else []
            case_id_list = list(set(_case_id_list).intersection(set(case_ids)))

            if (not pd_cases.empty) or (all([str(column) in NONE_LIST for column in input_column])):
                pd_data_case = self.dao.get_cases_many(_id_list=case_id_list)
                if not pd_data_case.empty:
                    pd_data_case = pd_data_case.rename(columns={'_id': 'case_id', 'code': 'case_code', 'name': 'case_name', 'company_id': 'case_company_id',
                                                                'user_id': 'case_user_id', 'communication': 'case_communication', 'implement': 'case_implement'})
                else:
                    pd_data_case = pd.DataFrame(columns=['case_id', 'case_code', 'service', 'status', 'date_time',
                                                         'performance_level', 'case_company_id', 'case_user_id', 'case_name', 'case_communication', 'case_implement'])

                pd_data_resource = self.dao.get_resources_many(case_id_list=case_id_list)
                if pd_data_resource.empty:
                    pd_data_resource = pd.DataFrame(columns=['_id', 'code', 'equipment_type', 'name', 'capacity',
                                                             'communication', 'implement', 'field_id', 'case_id'])

                field_ids = list(set([resource_dict[ApiConst.FIELD_ID.value] for resource_dict in
                                 FeatureFunc.result_dict(self.logger, pd_data_resource)]))
                pd_data_field = self.dao.get_fields_many(_id_list=field_ids).rename(columns={'_id': 'field_id', 'code': 'field_code', 'name': 'field_name'})
                if not pd_data_field.empty:
                    pd_data_field = pd_data_field.rename(columns={'_id': 'field_id', 'code': 'field_code', 'name': 'field_name', 'user_id': 'field_user_id', 'company_id': 'field_company_id',})
                else:
                    pd_data_field = pd.DataFrame(columns=['field_id', 'field_code', 'field_name', 'address', 'type', 'field_user_id', 'field_company_id'])

                pd_data = pd.merge(pd_data_resource, pd_data_case, how="left", on=["case_id"])
                pd_data = pd.merge(pd_data, pd_data_field, how="left", on=["field_id"])
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
            case_id = payload[ApiConst.CASE_ID.value]
            code = payload[ApiConst.CODE.value]
            service = payload[ApiConst.SERVICE.value]
            status = payload[ApiConst.STATUS.value]
            performance_level = payload[ApiConst.PERFORMANCE_LEVEL.value]
            company_id = payload[ApiConst.COMPANY_ID.value]
            user_id = payload[ApiConst.USER_ID.value]
            name = payload[ApiConst.NAME.value]
            communication = payload[ApiConst.COMMUNICATION.value]
            implement = payload[ApiConst.IMPLEMENT.value]
            status = True if status in TRUE_LIST else False if status in FALSE_LIST else None

            if case_id:
                self.logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                pd_fields = self.dao.get_resources(case_id=case_id)
                fields = pd_fields['field_id'].tolist() if (not pd_fields.empty) and ('field_id' in pd_fields.columns) else config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                if not user_info.is_admin and not user_info.is_field_admin:
                    allow_field = user_info.user_field_permission.keys()
                    for field in fields:
                        if len(user_info.user_field_permission) > 0 and \
                            field not in allow_field or \
                                not user_info.user_field_permission[field][
                                    PermissionConst.RESOURCE_BY_CASEID_POST_UPDATE.value]:
                            raise Exception('You dont have permission to access.')

                self.logger.info('update resource')
                pd_data = self.dao.update_cases(_id=case_id, code=code, service=service, status=status,
                                                performance_level=performance_level, company_id=company_id, user_id=user_id, name=name, communication=communication, implement=implement)
            else:
                self.logger.info('check permission [add-operation]')
                has_permission = False
                user_info: UserData = session[token_module.auth_session_key]
                for api in user_info.user_field_permission.values():
                    if api[PermissionConst.RESOURCE_BY_CASEID_POST_CREATE.value]:
                        has_permission = True
                        break
                if not has_permission:
                    raise Exception('You dont have permission to access.')

                self.logger.info('create resource')
                if not self.dao.get_cases(code=code).empty:
                    raise ValueError(f"code {code} already exists, please update it or check your case code")
                pd_data = self.dao.create_cases(_id=case_id, code=code, service=service, status=status,
                                                performance_level=performance_level, company_id=company_id, user_id=user_id, name=name, communication=communication, implement=implement)

            pd_res = FeatureFunc.result_dict(self.logger, pd_data)
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    def delete(self):
        self.logger.info('[delete]')
        pd_res = []
        try:
            case_id = request.get_json()[ApiConst.CASE_ID.value]

            fields = self.dao.get_resources(case_id=case_id)['field_id'].tolist()
            self.logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                allow_field = user_info.user_field_permission.keys()
                for field in fields:
                    if len(user_info.user_field_permission) == 0 or \
                            field not in allow_field or \
                            not user_info.user_field_permission[field][PermissionConst.RESOURCE_BY_CASEID_DELETE.value]:
                        raise Exception('You dont have permission to access.')

            self.dao.delete_cases([case_id])
            pd_data = self.dao.get_resources(case_id=case_id)
            resources_id = list(set([resource_dict[ApiConst.ID_.value] for resource_dict in FeatureFunc.result_dict(self.logger, pd_data)]))
            self.dao.delete_resources(resources_id)
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
