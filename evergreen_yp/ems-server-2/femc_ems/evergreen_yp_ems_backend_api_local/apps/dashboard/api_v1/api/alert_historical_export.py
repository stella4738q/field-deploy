# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
from datetime import datetime

import numpy as np
import pandas as pd
from flask import request, session, send_file
from apps.dashboard.utils import FeatureFunc
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class AlertHistoricalExport(Resource):
    """
    歷史報警匯出
    """

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('historical export')
        pd_res = []
        try:
            # check permission
            logger.info('check permission [query]')
            user_info: UserData = session[token_module.auth_session_key]
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            if not user_info.is_admin:
                if field_id not in user_info.user_field_permission.keys():
                    raise Exception('you dont have permission to access.')

            checked = request.args[ApiConst.CHECKED.value] if ApiConst.CHECKED.value in request.args else None
            check_user = request.args[ApiConst.CHECK_USER.value] if ApiConst.CHECK_USER.value in request.args else None
            equipment_id = request.args[ApiConst.EQUIPMENT_ID.value] if ApiConst.EQUIPMENT_ID.value in request.args else None
            start_time = request.args[ApiConst.START_TIME.value] if ApiConst.START_TIME.value in request.args else None
            end_time = request.args[ApiConst.END_TIME.value] if ApiConst.END_TIME.value in request.args else None
            title = request.args[ApiConst.TITLE.value] if ApiConst.TITLE.value in request.args else None
            code = request.args[ApiConst.CODE.value] if ApiConst.CODE.value in request.args else None
            message = request.args[ApiConst.MESSAGE.value] if ApiConst.MESSAGE.value in request.args else None
            level = request.args[ApiConst.LEVEL.value] if ApiConst.LEVEL.value in request.args else None

            temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]
            logger.info('remove csv file')

            sdate = None
            edate = None
            if start_time:
                sdate = datetime.strptime(start_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            if end_time:
                edate = datetime.strptime(end_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_alarm_historical_export(
                sdate, edate, field_id, equipment_id, title, code, message, level, checked=checked, check_user=check_user)

            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                pd_data = pd_data.dropna(subset=['done_time'])
            else:
                pd_data = pd.DataFrame(columns=['_id', 'time', 'done_time', 'field_id', 'equipment_id', 'title', 'code','message'])
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            logger.info('save file to csv')
            file_name = f'{temp_folder}/historical.csv'
            FeatureFunc.delete_file(logger, [file_name])
            pd_data.to_csv(file_name, sep=',', encoding='utf-8', index=False)

            return send_file(file_name, mimetype="text/csv", attachment_filename='historical.csv', as_attachment=True)
        except Exception as e:
            print(repr(e))
