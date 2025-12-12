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


class ChartHistorySunDB(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

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

            # 先取eq_list
            eq_df = self.dao.get_system_equipment(equipment_type=3)
            eq_df = eq_df.query("code == 'DCU'")
            if eq_df.empty:
                raise Exception("資料庫查無逆變器相關資訊")

            eq_list = eq_df['name'].tolist()

            target_date = request.args.get(ApiConst.START_DATE.value, None)
            if not target_date:
                now = datetime.datetime.now()
                end_date = now
                start_date = end_date + datetime.timedelta(days=-1)
            else:
                start_date = datetime.datetime.strptime(target_date, '%Y%m%d')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            inverter_no = 1
            all_time_tags = set()

            for equipment_name in eq_list:
                if equipment_name == "DCU_1":
                    inverter_no = 1
                elif equipment_name == "DCU_2":
                    inverter_no = 4

                dcu = self.dao.get_dcu(start_date, end_date, equipment_name, True)
                if dcu.empty:
                    continue

                inverter_all = sum(dcu['inverter_list'].to_list(), [])
                idf = pd.DataFrame(inverter_all)
                if not idf.empty:
                    gi = idf.groupby('equipment_id')
                    for key, inverter_df in gi:
                        inverter_key = f'INVERTER_{inverter_no}'
                        if not inverter_df.empty:
                            inverter_df = inverter_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                            inverter_df = inverter_df.apply(pd.to_numeric, errors='ignore')
                            inverter_df['data_time'] = pd.to_datetime(inverter_df['data_time'])
                            inverter_df['data_time'] = inverter_df['data_time'].dt.floor('T')
                            inverter_df = inverter_df.sort_values(by='data_time', ascending=True)

                            full_time_range = pd.date_range(start=start_date, end=datetime.datetime.now(), freq='T')
                            full_time_df = pd.DataFrame({'data_time': full_time_range})
                            inverter_df = pd.merge(full_time_df, inverter_df, on='data_time', how='left')
                            inverter_df = inverter_df[~inverter_df['dc_k_watt'].isna()]

                            inverter_df = inverter_df.groupby('data_time').last().reset_index()
                            inverter_df['dc_k_watt'] = inverter_df['dc_k_watt'].round(3)
                            inverter_df['dt_str'] = inverter_df['data_time'].astype(str)

                            rtn_data.Data[inverter_key] = inverter_df[['dt_str', 'dc_k_watt']].values.tolist()

                            # 收集所有時間點（聯集）
                            all_time_tags.update(inverter_df['data_time'].tolist())
                        else:
                            rtn_data.Data[inverter_key] = []

                        inverter_no += 1

            # 補日照量
            sun_df = self.dao.get_solar_exposure(start_date, end_date)
            if not sun_df.empty:
                sun_df = sun_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                sun_df = sun_df.apply(pd.to_numeric, errors='ignore')
                sun_df['data_time'] = pd.to_datetime(sun_df['data_time']).dt.floor('T')
                sun_df = sun_df.sort_values(by='data_time', ascending=True)

                # 根據所有 inverter 的聯集時間做過濾
                if all_time_tags:
                    sun_df = sun_df[sun_df['data_time'].isin(all_time_tags)]

                full_time_range = pd.date_range(start=start_date, end=datetime.datetime.now(), freq='T')
                full_time_df = pd.DataFrame({'data_time': full_time_range})
                sun_df = pd.merge(full_time_df, sun_df, on='data_time', how='left')
                sun_df['solar_exposure'] = sun_df['solar_exposure'].fillna(0)

                sun_df = sun_df.groupby('data_time').last().reset_index()
                sun_df['solar_exposure'] = sun_df['solar_exposure'].round(3)
                sun_df['dt_str'] = sun_df['data_time'].astype(str)

                rtn_data.Data['solar_exposure'] = sun_df[['dt_str', 'solar_exposure']].values.tolist()
            else:
                rtn_data.Data['solar_exposure'] = []

        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)

        return make_response(jsonify(rtn_data.serialized), 200)
