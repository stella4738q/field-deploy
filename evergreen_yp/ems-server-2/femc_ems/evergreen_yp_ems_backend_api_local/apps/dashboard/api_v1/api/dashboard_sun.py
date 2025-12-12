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


class DashboardSun(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        """
        取得 太陽能 首頁資訊
        總發電量、今日發電量、等效發電小時、減碳量、造林樹
        """

        self.logger.info('Get Dashboard Sun')
        rtn_data = ApiResponse()
        rtn_data.Data = {
            "totalExpPower": 0,
            "todayExpPower": 0,
            "eqTime": 0,
            "co2Diff": 0,
            "createTree": 0
        }

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('You dont have permission to access.')

            # 總發電量、今日發電量 -> 從inverter抓
            # 等效發電小時、減碳量、造林樹 -> 計算
            totalExpPower = 0
            todayExpPower = 0
            eqTime = 0
            co2Diff = 0
            createTree = 0

            # 撈取inverter
            eq_list = self.dao.get_system_equipment(equipment_type=3)
            if eq_list.empty:
                raise Exception("資料庫查無逆變器相關資訊")

            # 撈取資訊
            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()

            current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = current_date + datetime.timedelta(days=-1)
            end_date = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            fs_date = start_date.replace(minute=0, second=0, microsecond=0)
            fe_date = end_date.replace(minute=0, second=0, microsecond=0)

            inverter_settings = FilesystemSettings(
                target_name_list=f'lite_inverter_*', target_data=FolderType.History, base_path=dao.base_path,
                filter_date_star=fs_date, filter_date_end=fe_date)
            col = ['data_time', 'equipment_id', 'energy_total_kwh', 'energy_today_kwh']
            inverter_df = dao.read(inverter_settings, usecols=col)
            if not inverter_df.empty:
                inverter_df = inverter_df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                inverter_df = inverter_df.apply(pd.to_numeric, errors='ignore')
                inverter_df['data_time'] = pd.to_datetime(inverter_df['data_time'])
                condition = (inverter_df['data_time'] >= start_date) & (inverter_df['data_time'] <= end_date) & \
                    (inverter_df['energy_total_kwh'] != 0)
                inverter_df = inverter_df[condition]
                inverter_df = inverter_df.sort_values(by='data_time', ascending=False)
                first_one = inverter_df.groupby('equipment_id').head(1).reset_index()

                for idx, row in first_one.iterrows():
                    tdf = eq_list.query(f"name == '{str(row['equipment_id']).replace('lite_', '')}'").iloc[0]
                    capacity = tdf['capacity']

                    totalExpPower += row['energy_total_kwh']
                    todayExpPower += row['energy_today_kwh'] if row['data_time'] >= current_date else 0
                    eqTime += row['energy_total_kwh'] / capacity

                # 取的減碳量資訊
                co2_df = self.dao.get_diff_co2_coefficient()
                if not co2_df.empty:
                    co2_df['accu_kwh'] = co2_df['accu_kwh'].fillna(0)
                    accu_kwh = co2_df['accu_kwh'].sum()
                    co2_df['co2Diff'] = co2_df.apply(
                        lambda x: (totalExpPower - accu_kwh) * x['coefficient'] if x['accu_kwh'] == 0
                        else x['coefficient'] * x['accu_kwh'], axis=1)
                co2Diff = co2_df['co2Diff'].sum()
                createTree = co2Diff / 1000 / 1000 * 161 / 10000

            rtn_data.Data = {
                "totalExpPower": round(totalExpPower, 2),
                "todayExpPower": round(todayExpPower, 2),
                "eqTime": round(eqTime, 2),
                "co2Diff": round(co2Diff, 0),
                "createTree": round(createTree, 0),
            }
        except Exception as e:
            message = str(e)
            rtn_data.Success = False
            rtn_data.Msg = message
        return make_response(jsonify(rtn_data.serialized), 200)

