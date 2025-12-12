# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import io
import os

import numpy as np
import pandas as pd
from flask import request, session, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class InverterGetData(Resource):
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        """
        取得 DCU 資料
        """
        self.logger.info('DCU Get Data')
        temp_df = pd.DataFrame()
        pd_res = {
            'key': [],
            'values': [],
            'y2_values': []
        }

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()

            # 取得參數
            payload = request.get_json()

            # 0: 查詢, 1: 下載
            action = payload[ApiConst.ACTION.value]

            # 資料類型: 0: 小時, 1:日, 2:月, 3:年, 4: 原始數據, 5: 區間統計資料
            time_type = payload[ApiConst.TIME_TYPE.value]

            # 0: Simple Bar(全部總和), 1: Group Bar(分equipment), 2: DCU下Inverter
            report_type = payload[ApiConst.TYPE.value]

            # 20241020
            temp_s_date = payload[ApiConst.START_DATE.value]
            start_date = datetime.datetime.strptime(temp_s_date, '%Y%m%d')

            temp_e_date = payload[ApiConst.END_DATE.value]
            end_date = datetime.datetime.strptime(temp_e_date, '%Y%m%d')

            if time_type == 0:
                # 小時
                inverter_df = self.dao.get_daily_report_sun(start_date=start_date, end_date=end_date)
                if not inverter_df.empty:
                    merge_df = pd.DataFrame()
                    for idx, row in inverter_df.iterrows():
                        data_list = row.get('data_list') or []
                        if report_type == 2 and data_list:
                            _temp_df = pd.DataFrame(data_list)
                            if 'inverter' in _temp_df.columns and not _temp_df['inverter'].isna().all():
                                exploded = _temp_df[['hour', 'inverter']].explode(
                                    'inverter', ignore_index=True)
                                inv_df = pd.json_normalize(exploded['inverter'])
                                inv_df['hour'] = exploded['hour'].values
                                inv_df['data_time'] = inv_df['hour'].apply(
                                    lambda x: datetime.datetime(row['year'], row['month'], row['day'], x).strftime(
                                        '%y%m%d_%H'))
                                data_df = inv_df
                            else:
                                continue
                        else:
                            data_df = pd.DataFrame(data_list)
                            if 'inverter' in data_df.columns:
                                data_df = data_df.drop(columns=['inverter'])

                            data_df['data_time'] = data_df['hour'].apply(
                                lambda x: datetime.datetime(row['year'], row['month'], row['day'], x)
                                .strftime('%y%m%d_%H'))

                        if merge_df.empty:
                            merge_df = data_df
                        else:
                            merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                    if not merge_df.empty:
                        if report_type == 0:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            pd_res['key'] = data_df['data_time'].tolist()
                            pd_res['values'] = data_df['energy_kwh'].tolist()
                            pd_res['y2_values'] = (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan))\
                                .fillna(0).tolist()
                        else:
                            group_df = merge_df.groupby(['equipment_id', 'data_time']).sum()
                            for _, data_df in group_df.groupby('equipment_id'):
                                data_df = data_df.reset_index()
                                app_obj = {
                                    'name': _,
                                    'data': data_df['energy_kwh'].tolist()
                                }
                                pd_res['key'] = data_df['data_time'].tolist()
                                pd_res['values'].append(app_obj)

                                y2_obj = {
                                    'name': _,
                                    'data': (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan))
                                    .fillna(0).tolist()
                                }
                                pd_res['y2_values'].append(y2_obj)
            elif time_type == 1:
                # 日
                inverter_df = self.dao.get_monthly_report_sun(year=start_date.year, start_month=start_date.month,
                                                              end_month=end_date.month)
                if not inverter_df.empty:
                    merge_df = pd.DataFrame()
                    for idx, row in inverter_df.iterrows():
                        data_list = row.get('data_list') or []
                        if report_type == 2 and data_list:
                            _temp_df = pd.DataFrame(data_list)
                            if 'inverter' in _temp_df.columns and not _temp_df['inverter'].isna().all():
                                exploded = _temp_df[['day', 'inverter']].explode(
                                    'inverter', ignore_index=True)
                                inv_df = pd.json_normalize(exploded['inverter'])
                                inv_df['day'] = exploded['day'].values
                                inv_df['data_time'] = inv_df['day'].apply(
                                    lambda x: datetime.datetime(row['year'], row['month'], x).strftime('%Y%m%d'))
                                data_df = inv_df
                            else:
                                continue
                        else:
                            data_df = pd.DataFrame(data_list)
                            if 'inverter' in data_df.columns:
                                data_df = data_df.drop(columns=['inverter'])

                            data_df['data_time'] = data_df['day'].apply(
                                lambda x: datetime.datetime(row['year'], row['month'], x).strftime('%Y%m%d'))

                        filtered_df = data_df[
                            (pd.to_datetime(data_df['data_time'], format='%Y%m%d') >= start_date) &
                            (pd.to_datetime(data_df['data_time'], format='%Y%m%d') <= end_date)
                            ]
                        filtered_df['data_time'] = filtered_df['data_time'].apply(lambda x: x)

                        if merge_df.empty:
                            merge_df = filtered_df
                        else:
                            merge_df = pd.concat([merge_df, filtered_df], ignore_index=True)

                    if not merge_df.empty:
                        if report_type == 0:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            pd_res['key'] = data_df['data_time'].tolist()
                            pd_res['values'] = data_df['energy_kwh'].tolist()
                            pd_res['y2_values'] = (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan)) \
                                .fillna(0).tolist()
                        else:
                            group_df = merge_df.groupby(['equipment_id', 'data_time']).sum()
                            for _, data_df in group_df.groupby('equipment_id'):
                                data_df = data_df.reset_index()
                                app_obj = {
                                    'name': _,
                                    'data': data_df['energy_kwh'].tolist()
                                }
                                pd_res['key'] = data_df['data_time'].tolist()
                                pd_res['values'].append(app_obj)

                                y2_obj = {
                                    'name': _,
                                    'data': (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan))
                                    .fillna(0).tolist()
                                }
                                pd_res['y2_values'].append(y2_obj)
            elif time_type == 2:
                # 月
                inverter_df = self.dao.get_yearly_report_sun(year=start_date.year)
                if not inverter_df.empty:
                    merge_df = pd.DataFrame()
                    for idx, row in inverter_df.iterrows():
                        data_list = row.get('data_list') or []
                        if report_type == 2 and data_list:
                            _temp_df = pd.DataFrame(data_list)
                            if 'inverter' in _temp_df.columns and not _temp_df['inverter'].isna().all():
                                exploded = _temp_df[['month', 'inverter']].explode(
                                    'inverter', ignore_index=True)
                                inv_df = pd.json_normalize(exploded['inverter'])
                                inv_df['month'] = exploded['month'].values
                                inv_df['data_time'] = inv_df['month'].apply(
                                    lambda x: f"{row['year']}{str(x).rjust(2, '0')}")
                                data_df = inv_df
                            else:
                                continue
                        else:
                            data_df = pd.DataFrame(data_list)
                            if 'inverter' in data_df.columns:
                                data_df = data_df.drop(columns=['inverter'])

                            data_df['data_time'] = data_df['month'].apply(
                                lambda x: f"{row['year']}{str(x).rjust(2, '0')}")

                        start_month = start_date.strftime('%Y%m')
                        end_month = end_date.strftime('%Y%m')

                        filtered_df = data_df[
                            (data_df['data_time'] >= start_month) &
                            (data_df['data_time'] <= end_month)
                            ]
                        filtered_df['data_time'] = filtered_df['data_time'].apply(lambda x: x)

                        if merge_df.empty:
                            merge_df = filtered_df
                        else:
                            merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                    if not merge_df.empty:
                        if report_type == 0:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            pd_res['key'] = data_df['data_time'].tolist()
                            pd_res['values'] = data_df['energy_kwh'].tolist()
                            pd_res['y2_values'] = (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan)) \
                                .fillna(0).tolist()
                        else:
                            group_df = merge_df.groupby(['equipment_id', 'data_time']).sum()
                            for _, data_df in group_df.groupby('equipment_id'):
                                data_df = data_df.reset_index()
                                app_obj = {
                                    'name': _,
                                    'data': data_df['energy_kwh'].tolist()
                                }
                                pd_res['key'] = data_df['data_time'].tolist()
                                pd_res['values'].append(app_obj)

                                y2_obj = {
                                    'name': _,
                                    'data': (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan))
                                    .fillna(0).tolist()
                                }
                                pd_res['y2_values'].append(y2_obj)
            elif time_type == 3:
                # 年
                inverter_df = self.dao.get_yearly_report_sun(year=start_date.year)
                if not inverter_df.empty:
                    merge_df = pd.DataFrame()
                    for idx, row in inverter_df.iterrows():
                        data_list = row.get('data_list') or []
                        if report_type == 2 and data_list:
                            _temp_df = pd.DataFrame(data_list)
                            if 'inverter' in _temp_df.columns and not _temp_df['inverter'].isna().all():
                                exploded = _temp_df[['month', 'inverter']].explode(
                                    'inverter', ignore_index=True)
                                inv_df = pd.json_normalize(exploded['inverter'])
                                inv_df['month'] = exploded['month'].values
                                inv_df['data_time'] = inv_df['month'].apply(
                                    lambda x: datetime.datetime(row['year'], x).strftime('%Y%m%d'))
                                data_df = inv_df
                            else:
                                continue
                        else:
                            data_df = pd.DataFrame(data_list)
                            if 'inverter' in data_df.columns:
                                data_df = data_df.drop(columns=['inverter'])

                            data_df['data_time'] = data_df['month'].apply(
                                lambda x: f"{row['year']}")

                        if merge_df.empty:
                            merge_df = data_df
                        else:
                            merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                    if not merge_df.empty:
                        if report_type == 0:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            pd_res['key'] = data_df['data_time'].tolist()
                            pd_res['values'] = data_df['energy_kwh'].tolist()
                            pd_res['y2_values'] = (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan)) \
                                .fillna(0).tolist()
                        else:
                            group_df = merge_df.groupby(['equipment_id', 'data_time']).sum()
                            for _, data_df in group_df.groupby('equipment_id'):
                                data_df = data_df.reset_index()
                                app_obj = {
                                    'name': _,
                                    'data': data_df['energy_kwh'].tolist()
                                }
                                pd_res['key'] = data_df['data_time'].tolist()
                                pd_res['values'].append(app_obj)

                                y2_obj = {
                                    'name': _,
                                    'data': (data_df['energy_kwh'] / data_df['capacity'].replace(0, np.nan))
                                    .fillna(0).tolist()
                                }
                                pd_res['y2_values'].append(y2_obj)
            elif time_type == 4:
                # 原始數據
                pd_res = {}
                dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()

                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                fs_date = start_date.replace(minute=0, second=0, microsecond=0)
                fe_date = end_date.replace(minute=0, second=0, microsecond=0)

                for i in range(2):
                    key = f'dcu_{i + 1}'
                    inverter_settings = FilesystemSettings(
                        target_name_list=f'dcu_{key.upper()}*', target_data=FolderType.History,
                        base_path=dao.base_path,
                        filter_date_star=fs_date, filter_date_end=fe_date)

                    col = ['data_time', 'ac_power_kw']
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
                        # 保留小數3位
                        inverter_df['ac_power_kw'] = inverter_df['ac_power_kw'].round(3)

                        inverter_df['dt_str'] = inverter_df['data_time'].apply(lambda x: str(x))
                        if temp_df.empty:
                            temp_df['data_time'] = inverter_df['dt_str']
                            temp_df[key] = inverter_df['ac_power_kw']
                        else:
                            temp_df[key] = inverter_df['ac_power_kw']
                        pd_res[key] = inverter_df[['dt_str', 'ac_power_kw']].values.tolist()
                    else:
                        pd_res[key] = []
            elif time_type == 5:
                # 每日統計
                inverter_df = self.dao.get_daily_report_sun(start_date=start_date, end_date=end_date)
                if not inverter_df.empty:
                    sun_data_list = list()
                    for idx, row in inverter_df.iterrows():
                        sum_data = row.get('sum_data', None)
                        if sum_data:
                            if action == 1:
                                flat_sum_data = {
                                    "data_time": datetime.datetime.strftime(row["date_time"], '%Y-%m-%d'),
                                    "total_kwh": sum_data["total_kwh"],
                                    **{item["equipment_id"]: item["kwh"] for item in sum_data["inverter_kwh"]},
                                    "irr_kwh_m2": sum_data["irr_kwh_m2"],
                                    "hours_in_window": sum_data["hours_in_window"],
                                    "capacity_kw": sum_data["capacity_kw"],
                                    "irr_pct": sum_data["irr_pct"],
                                    "pr_pct": sum_data["pr_pct"]
                                }
                                sun_data_list.append(flat_sum_data)
                            else:
                                flat_sum_data = {
                                    "data_time": datetime.datetime.strftime(row["date_time"], '%Y-%m-%d'),
                                    "total_kwh": sum_data["total_kwh"],
                                    "inverter_kwh": sum_data["inverter_kwh"],
                                    "irr_kwh_m2": sum_data["irr_kwh_m2"],
                                    "hours_in_window": sum_data["hours_in_window"],
                                    "capacity_kw": sum_data["capacity_kw"],
                                    "irr_pct": sum_data["irr_pct"],
                                    "pr_pct": sum_data["pr_pct"]
                                }
                                sun_data_list.append(flat_sum_data)
                    pd_res = sun_data_list

            if action == 1:
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][PermissionConst.INVERTER_GER_DOWNLOAD.value]:
                    raise Exception('You dont have permission to access.')

                if time_type == 5:
                    temp_df = pd.DataFrame(pd_res)
                elif time_type != 4:
                    temp_df['data_time'] = pd_res['key']
                    if report_type == 0:
                        temp_df['value'] = pd_res['values']
                        temp_df['y2_values'] = pd_res['y2_values']
                    else:
                        for value in pd_res['values']:
                            temp_df[value['name']] = value['data']
                        for value in pd_res['y2_values']:
                            temp_df[f"{value['name']}_FLH"] = value['data']
                if temp_df.empty:
                    raise Exception("查無相關資訊")

                file_name = f"太陽能系統報表-{temp_s_date}~{temp_e_date}_{int(datetime.datetime.now().timestamp())}.csv"
                byte_io = io.BytesIO()
                temp_df.to_csv(byte_io, index=False)
                byte_io.seek(0)
                return send_file(byte_io, mimetype='text/csv', as_attachment=True, attachment_filename=file_name)
            else:
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][PermissionConst.INVERTER_GER_DATA.value]:
                    raise Exception('You dont have permission to access.')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
            pd_res = None
        return {'message': message, 'data': pd_res}, 200, None

