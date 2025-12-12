from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

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


class NotifyLog(Resource):
    logger = Logger().create('Evergreen API - notify log', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('get notify log')
        pd_res = []
        try:
            start_date = request.args.get(ApiConst.START_DATE.value, None)
            end_date = request.args.get(ApiConst.END_DATE.value, None)
            token_id = request.args.get(ApiConst.TOKEN_ID.value, None)
            rule_id = request.args.get(ApiConst.RULE_ID.value, None)

            if start_date:
                start_date = datetime.strptime(start_date, "%Y%m%d").replace(hour=0, minute=0, second=0, microsecond=0)

            if end_date:
                end_date = \
                    datetime.strptime(end_date, "%Y%m%d").replace(hour=23, minute=59, second=59, microsecond=999999)

            pd_log = self.dao.get_notify_log(
                sdate=start_date, edate=end_date, notify_rule=rule_id, notify_token=token_id)
            if not pd_log.empty:
                pd_notify_token = self.dao.get_notify_token(_id=token_id)
                pd_notify_rule = self.dao.get_notify_rule(_id=rule_id)

                if not pd_notify_rule.empty and 'name' in pd_notify_rule.columns:
                    pd_notify_rule = pd_notify_rule.rename(columns={'_id': 'notify_rule', 'name': 'rule_name'})
                    pd_notify_rule['notify_rule'] = pd_notify_rule['notify_rule'].astype(str)
                    pd_log['notify_rule'] = pd_log['notify_rule'].astype(str)
                pd_log = pd.merge(pd_log, pd_notify_rule, on=ApiConst.NOTIFY_RULE.value, how='left')

                if not pd_notify_token.empty and 'name' in pd_notify_token.columns:
                    pd_notify_token = pd_notify_token.rename(columns={'_id': 'notify_token', 'name': 'token_name'})
                    pd_notify_token['notify_token'] = pd_notify_token['notify_token'].astype(str)
                    pd_log['notify_token'] = pd_log['notify_token'].astype(str)
                pd_log = pd.merge(pd_log, pd_notify_token, on=ApiConst.NOTIFY_TOKEN.value, how='left')

                pd_res = FeatureFunc.result_dict(self.logger, pd_log)
            message = SUCCESS_MESSAGE

        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
