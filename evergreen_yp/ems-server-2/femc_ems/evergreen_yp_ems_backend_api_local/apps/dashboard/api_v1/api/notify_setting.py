# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
import pandas as pd
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst, ConfigConstant
from apps.dashboard.utils import FeatureFunc
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class NotifySetting(Resource):
    logger = Logger().create('Evergreen API - notify setting', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()
    collection = 'notify setting'

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] notify_setting')
        pd_res = []
        try:
            notify_token = None if request.args.get(ApiConst.NOTIFY_TOKEN.value) == '' else request.args.get(ApiConst.NOTIFY_TOKEN.value)

            # check permission
            self.logger.info('check permission')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            if not user_info.is_admin:
                allow_field = user_info.user_field_permission.keys()
                if (len(user_info.user_field_permission) == 0 or field not in allow_field or
                        not user_info.user_field_permission[field][
                                PermissionConst.NOTIFY_SETTING_GET.value]):
                    raise Exception('You dont have permission to access.')
            try:
                pd_notify_token = self.dao.get_notify_token(_id=notify_token)
                pd_notify_token = pd_notify_token.rename(columns={'_id': ApiConst.NOTIFY_TOKEN.value})

                pd_notify_setting = self.dao.get_notify_setting(notify_token=notify_token)
                pd_notify_setting = pd_notify_setting.rename(columns={'_id': ApiConst.NOTIFY_SETTING.value})

                notify_rule_ids = pd_notify_setting['notify_rule'].tolist() if not pd_notify_setting.empty else []
                pd_notify_rule = self.dao.get_notify_rule(_id=list(notify_rule_ids))
                pd_notify_rule = pd_notify_rule.rename(columns={'_id': ApiConst.NOTIFY_RULE.value})

                # #pd_notify_rule column
                if not pd_notify_rule.empty and 'name' in pd_notify_rule.columns:
                    pd_notify_rule = pd_notify_rule.rename(columns={'name': 'rule_name'})
                pd_notify_setting = pd.merge(pd_notify_setting, pd_notify_rule, on=ApiConst.NOTIFY_RULE.value, how='left')

                if not pd_notify_token.empty and 'name' in pd_notify_token.columns:
                    pd_notify_token = pd_notify_token.rename(columns={'name': 'token_name'})
                pd_notify_setting = pd.merge(pd_notify_setting, pd_notify_token, on=ApiConst.NOTIFY_TOKEN.value, how='left')

                pd_res = FeatureFunc.result_dict(self.logger, pd_notify_setting)

            except Exception as e:
                message = repr(e)

            message = SUCCESS_MESSAGE

        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Evergreen API - post notify_setting', level=logging_level, log_path=log_path)
        logger.info('[post] notify_setting')
        pd_res = []
        try:
            payload = request.get_json()
            data_list = payload.get("data_list", [])

            notify_token = None if request.args.get(ApiConst.NOTIFY_TOKEN.value) == '' else request.args.get(ApiConst.NOTIFY_TOKEN.value)

            # check permission
            self.logger.info('check permission')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            if not user_info.is_admin:
                allow_field = user_info.user_field_permission.keys()
                if (len(user_info.user_field_permission) == 0 or field not in allow_field or
                        not user_info.user_field_permission[field][
                                PermissionConst.NOTIFY_SETTING_POST_UPDATE.value]):
                    raise Exception('You dont have permission to access.')

            if data_list:
                self.logger.info('deleted notify_setting')
                pd_notify_setting = self.dao.get_notify_setting(notify_token=notify_token)
                notify_setting_ids = pd_notify_setting['_id'].tolist() if not pd_notify_setting.empty else []
                pd_notify_setting = self.dao.delete_notify_setting(notify_setting_ids)

                self.logger.info('create notify_setting')
                for data in data_list:
                    notify_rule = data.get("notify_rule")
                    notify_token = data.get("notify_token")
                    pd_notify_setting = self.dao.create_notify_setting(notify_rule=notify_rule, notify_token=notify_token)

                pd_data = pd_notify_setting.replace({np.nan: None})
                self.logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None