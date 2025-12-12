# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import json
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


def clean_datetime_string(s):
    replace = True
    while replace:
        s_idx = s.find("datetime.datetime(")
        if s_idx == -1:
            replace = False
        else:
            e_idx = s.find(')', s_idx)
            target_replace = s[s_idx: e_idx + 1]
            replace_to = eval(target_replace.replace('datetime.', ''))
            s = s.replace(target_replace, f'"{str(replace_to)}"')
    return s


class DashboardSunDB(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        """
        取得 太陽能 首頁資訊
        總發電量、今日發電量、等效發電小時(平均發電量)、IRR、PR值、減碳量、造林樹
        """

        self.logger.info('Get Dashboard Sun')
        rtn_data = ApiResponse()
        rtn_data.Data = {
            "totalExpPower": 0,
            "todayExpPower": 0,
            "eqTime": 0,
            "co2Diff": 0,
            "createTree": 0,
            "irr": 0,
            "pr": 0,
        }

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('You dont have permission to access.')

            # 總發電量 -> 從inverter抓
            # 今日發電量 -> 自己計算
            # 等效發電小時、減碳量、造林樹 -> 計算
            totalExpPower = 0
            todayExpPower = 0
            eqTime = 0
            todayEqTime = 0
            co2Diff = 0
            createTree = 0

            # 撈取inverter
            eq_list = self.dao.get_system_equipment(equipment_type=3)
            eq_list = eq_list.query("code == 'DCU'")
            if eq_list.empty:
                raise Exception("資料庫查無逆變器相關資訊")

            # 撈取資訊
            now = datetime.datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = today + datetime.timedelta(days=-1)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

            filters = {'ac_energy_kwh': {'$gt': 0}}
            dcu_df = self.dao.get_dcu(start_date, end_date, need_inverter=False, filter=filters)
            if not dcu_df.empty:
                # 總發電量：各設備累計電量最大值相加
                totalExpPower = dcu_df.groupby('equipment_id')['ac_energy_kwh'].max().sum()

                # 今日發電量：各設備 (max - min)，遇到重置造成負值則當 0
                todayS = dcu_df.query('data_time >= @today')
                if not todayS.empty:
                    per_e = todayS.groupby('equipment_id')['ac_energy_kwh'].agg(lambda x: max(x) - min(x))
                    per_e = per_e.clip(lower=0)
                    todayExpPower = per_e.sum()

                # 容量匯總（加強容錯）
                capacity = 0
                # 先建立設備名稱查找（避免 query+iloc[0] 失敗）
                # 例如 eq_list 內有 'name'、'capacity' 欄位
                name_to_capacity = (
                    eq_list.groupby('name', as_index=False)['capacity']
                    .sum()
                    .set_index('name')['capacity']
                    .to_dict()
                )

                for key in dcu_df['equipment_id'].unique():
                    name_key = str(key).replace('lite_', '')
                    cap = name_to_capacity.get(name_key, 0)
                    capacity += cap

                eqTime = totalExpPower / capacity if capacity > 0 else 0
                todayEqTime = todayExpPower / capacity if capacity > 0 else 0

                # 減碳量
                co2_df = self.dao.get_diff_co2_coefficient()
                if not co2_df.empty:
                    co2_df['accu_kwh'] = co2_df['accu_kwh'].fillna(0)
                    accu_kwh = int(co2_df['accu_kwh'].sum())
                    co2_df['co2Diff'] = co2_df.apply(
                        lambda x: (totalExpPower - accu_kwh) * x['coefficient'] if x['accu_kwh'] == 0
                        else x['coefficient'] * x['accu_kwh'], axis=1)
                    co2Diff = co2_df['co2Diff'].sum()
                    createTree = co2Diff / 1000 / 1000 * 161 / 10000

            # --- IRR（由日照整合） ---
            file_dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            irradiation = 0
            settings = FilesystemSettings(
                target_name_list=[f'solar_exposure*'], target_data=FolderType.History,
                base_path=file_dao.base_path, filter_date_star=today, filter_date_end=end_date
            )
            exp_df = file_dao.read(criteria=settings)
            if not exp_df.empty:
                exp_df["data_time"] = pd.to_datetime(exp_df["data_time"])
                exp_df = exp_df.sort_values("data_time").drop_duplicates(subset="data_time", keep="last").reset_index(
                    drop=True)
                # 以「當前點到下一點」的區間做積分
                # 日照積分
                exp_df["time_diff_sec"] = (
                        exp_df["data_time"].shift(-1) - exp_df["data_time"]
                ).dt.total_seconds().fillna(0).clip(lower=0)
                exp_df = exp_df[exp_df["time_diff_sec"] > 0]
                exp_df["time_diff_sec"] = exp_df["time_diff_sec"].clip(lower=0)

                # solar_exposure: W/m² -> kWh/m²
                exp_df["irradiation"] = (exp_df["solar_exposure"] * exp_df["time_diff_sec"]) / 3600 / 1000
                irradiation = float(exp_df["irradiation"].sum())

            rtn_data.Data = {
                "totalExpPower": round(totalExpPower, 2),
                "todayExpPower": round(todayExpPower, 2),
                "eqTime": round(eqTime, 2),
                "co2Diff": round(co2Diff, 0),
                "createTree": round(createTree, 0),
                "irr": irradiation,
                "pr": round(todayEqTime / irradiation * 100, 2) if irradiation > 0 else 0
            }
        except Exception as e:
            message = str(e)
            rtn_data.Success = False
            rtn_data.Msg = message
        return make_response(jsonify(rtn_data.serialized), 200)

