# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os

import datetime
import threading

import numpy as np
import pandas as pd
from flask import request, make_response, send_file, session, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class ChartHistorySun(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        """
        取得 太陽能 首頁 chart資訊
        """
        self.logger.info('Get Inverter Data')
        rtn_data = ApiResponse()
        rtn_data.Data = {}

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('You dont have permission to access.')

            target_date = request.args.get(ApiConst.START_DATE.value, None)
            if not target_date:
                now = datetime.datetime.now()
                end_date = now
                start_date = end_date + datetime.timedelta(days=-1)

                fs_date = start_date.replace(minute=0, second=0, microsecond=0)
                fe_date = end_date.replace(minute=0, second=0, microsecond=0)
            else:
                start_date = datetime.datetime.strptime(target_date, '%Y%m%d')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                fs_date = start_date.replace(minute=0, second=0, microsecond=0)
                fe_date = end_date.replace(minute=0, second=0, microsecond=0)

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            taski_list = []
            for i in range(5):
                key = f'inverter_{i+1}'
                task = threading.Thread(
                    target=self.get_history,
                    args=(key, dao, fs_date, fe_date, start_date, end_date, rtn_data.Data))
                task.start()
                taski_list.append(task)

            for task in taski_list:
                task.join()
        except Exception as e:
            message = str(e)
            rtn_data.Success = False
            rtn_data.Msg = message
        return make_response(jsonify(rtn_data.serialized), 200)

    def get_history(self, key, dao, fs_date, fe_date, start_date, end_date, rtn_data):
        try:
            inverter_settings = FilesystemSettings(
                target_name_list=f'lite_inverter_lite_{key.upper()}*',
                target_data=FolderType.History,
                base_path=dao.base_path,
                filter_date_star=fs_date,
                filter_date_end=fe_date
            )

            col = ['data_time', 'total_active_power']
            inverter_df = dao.read(inverter_settings, usecols=col)

            if not inverter_df.empty:
                inverter_df = inverter_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                inverter_df = inverter_df.apply(pd.to_numeric, errors='ignore')
                inverter_df['data_time'] = pd.to_datetime(inverter_df['data_time'])
                condition = (inverter_df['data_time'] >= start_date) & (inverter_df['data_time'] <= end_date)
                inverter_df = inverter_df[condition]
                inverter_df = inverter_df.sort_values(by='data_time', ascending=True)

                inverter_df['data_time'] = pd.to_datetime(inverter_df['data_time']).dt.floor('T')
                inverter_df = inverter_df.groupby('data_time').last().reset_index()
                inverter_df['total_active_power'] = inverter_df['total_active_power'].round(3)

                inverter_df['dt_str'] = inverter_df['data_time'].apply(lambda x: str(x))
                rtn_data[key] = inverter_df[['dt_str', 'total_active_power']].values.tolist()
            else:
                rtn_data[key] = []
        except Exception as e:
            self.logger.error(f"Error while processing {key}: {str(e)}")
            rtn_data[key] = []
