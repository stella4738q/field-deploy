# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os

import datetime
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


class ChartHistory(Resource):
    @token_required(token_module)
    def get(self):
        """
        取得 EMS首頁chart資訊
        """
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('PCS Get Data')
        rtn_data = ApiResponse()
        rtn_data.Data = {
            'pcs_power': [],
            'soc': [],
            'temp': []
        }

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('You dont have permission to access.')

            now = datetime.datetime.now()
            end_date = now
            start_date = end_date + datetime.timedelta(days=-1)

            fs_date = start_date.replace(minute=0, second=0, microsecond=0)
            fe_date = end_date.replace(minute=0, second=0, microsecond=0)

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            pcs_settings = FilesystemSettings(
                target_name_list=f'pcs_*', target_data=FolderType.History, base_path=dao.base_path,
                filter_date_star=fs_date, filter_date_end=fe_date)

            pcs_col = ['data_time', 'active_power']
            pcs_df_min = pd.DataFrame(columns=pcs_col)
            pcs_df = dao.read(pcs_settings, usecols=pcs_col)
            if not pcs_df.empty:
                pcs_df = pcs_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                pcs_df = pcs_df.apply(pd.to_numeric, errors='ignore')
                pcs_df['data_time'] = pd.to_datetime(pcs_df['data_time'])
                condition = (pcs_df['data_time'] >= start_date) & (pcs_df['data_time'] <= end_date)
                pcs_df = pcs_df[condition]
                pcs_df = pcs_df.sort_values(by='data_time', ascending=True)

                pcs_df['data_time'] = pd.to_datetime(pcs_df['data_time']).dt.floor('T')
                pcs_df_min = pcs_df.groupby('data_time').last().reset_index()

            bmu_settings = FilesystemSettings(
                target_name_list=f'lite_bmu*', target_data=FolderType.History, base_path=dao.base_path,
                filter_date_star=fs_date, filter_date_end=fe_date)

            bms_col = ['data_time', 'soc', 'container_temp_a']
            bms_df_min = pd.DataFrame(columns=bms_col)
            bms_df = dao.read(bmu_settings, usecols=bms_col)
            if not bms_df.empty:
                bms_df = bms_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                bms_df = bms_df.apply(pd.to_numeric, errors='ignore')
                bms_df['data_time'] = pd.to_datetime(bms_df['data_time'])
                condition = (bms_df['data_time'] >= start_date) & (bms_df['data_time'] <= end_date)
                bms_df = bms_df[condition]
                bms_df = bms_df.sort_values(by='data_time', ascending=True)
                bms_df['data_time'] = pd.to_datetime(bms_df['data_time']).dt.floor('T')
                bms_df_min = bms_df.groupby('data_time').min().reset_index()

            # Merge Data
            merged_df = pd.merge(pcs_df_min, bms_df_min, on='data_time', how='outer')
            merged_df.dropna(inplace=True)
            if not merged_df.empty:
                merged_df['dt_str'] = merged_df['data_time'].apply(lambda x: str(x))
                rtn_data.Data = {
                    'pcs_power': merged_df[['dt_str', 'active_power']].values.tolist(),
                    'soc': merged_df[['dt_str', 'soc']].values.tolist(),
                    'temp': merged_df[['dt_str', 'container_temp_a']].values.tolist()
                }
        except Exception as e:
            message = str(e)
            rtn_data.Success = False
            rtn_data.Msg = message
        return make_response(jsonify(rtn_data.serialized), 200)

