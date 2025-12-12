# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import calendar
import io
from datetime import datetime

import pandas as pd
from flask import request, make_response, jsonify, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required
from . import Resource


class CabinetReportChartData(Resource):
    """
    PCS、充放電報表資訊
    - 日、月、年報查詢
    """
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = {
            'key': [],
            'values': []
        }
        self.logger.info('[post] get CabinetReportChartData')
        try:
            payload = request.get_json()

            is_down_load = payload.get(ApiConst.ACTION_TYPE.value, 0)
            use_pcs_key = payload.get(ApiConst.USE_PCS_KEY.value, False)
            pcs_in_key = 'bms_charge_capacity'
            pcs_out_key = 'bms_discharge_capacity'
            if use_pcs_key:
                pcs_in_key = 'pcs_charge_capacity'
                pcs_out_key = 'pcs_discharge_capacity'

            # 0:日報, 1:月報, 2:年報
            report_type = payload.get(ApiConst.TIME_TYPE.value, None)
            if report_type is None:
                raise Exception('報表類型為必要項目')
            report_type = int(report_type)

            # 20241020
            temp_s_date = payload[ApiConst.START_DATE.value]
            start_date = datetime.strptime(temp_s_date, '%Y%m%d')

            temp_e_date = payload[ApiConst.END_DATE.value]
            end_date = datetime.strptime(temp_e_date, '%Y%m%d')

            if not is_down_load:
                sun_categories = [
                    {
                        'key': pcs_in_key,
                        'name': 'PCS-充電量(DC)',
                        'stack': 'PCS',
                    },
                    {
                        'key': pcs_out_key,
                        'name': 'PCS-放電量(DC)',
                        'stack': 'PCS',
                    },
                    {
                        'key': 'meter_charge_capacity',
                        'name': 'METER-充電量(AC)',
                        'stack': 'METER',
                    },
                    {
                        'key': 'meter_discharge_capacity',
                        'name': 'METER-放電量(AC)',
                        'stack': 'METER',
                    }
                ]

                # get data
                if report_type == 0:
                    pd_data = self.dao.get_ems_monthly_report(
                        year=start_date.year, start_month=start_date.month, end_month=end_date.month)
                    if not pd_data.empty:
                        merge_df = pd.DataFrame()
                        for idx, row in pd_data.iterrows():
                            data_list = row['data_list']
                            data_df = pd.DataFrame(data_list)
                            data_df['data_time'] = data_df['day'].apply(
                                lambda x: datetime(row['year'], row['month'], x).strftime('%Y%m%d'))

                            filtered_df = data_df[
                                (pd.to_datetime(data_df['data_time'], format='%Y%m%d') >= start_date) &
                                (pd.to_datetime(data_df['data_time'], format='%Y%m%d') <= end_date)
                                ].copy()
                            filtered_df['data_time'] = filtered_df['data_time'].apply(lambda x: x)

                            if merge_df.empty:
                                merge_df = filtered_df
                            else:
                                merge_df = pd.concat([merge_df, filtered_df], ignore_index=True)

                        if not merge_df.empty:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            rtn_data.Data['key'] = data_df['data_time'].tolist()
                            rtn_data.Data['values'] = [
                                {
                                    'name': col['name'],
                                    'stack': col['stack'],
                                    'values': [round(v, 3) if pd.notna(v) else 0 for v in data_df[col['key']].tolist()]
                                }
                                for col in sun_categories
                            ]

                elif report_type == 1:
                    pd_data = self.dao.get_ems_yearly_report(year=start_date.year)
                    if not pd_data.empty:
                        merge_df = pd.DataFrame()
                        for idx, row in pd_data.iterrows():
                            data_list = row['data_list']
                            data_df = pd.DataFrame(data_list)
                            data_df['data_time'] = data_df['month'].apply(
                                lambda x: f"{row['year']}{str(x).rjust(2,'0')}")

                            start_month = start_date.strftime('%Y%m')
                            end_month = end_date.strftime('%Y%m')

                            filtered_df = data_df[
                                (data_df['data_time'] >= start_month) &
                                (data_df['data_time'] <= end_month)
                                ].copy()
                            filtered_df['data_time'] = filtered_df['data_time'].apply(lambda x: x)

                            if merge_df.empty:
                                merge_df = filtered_df
                            else:
                                merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                        if not merge_df.empty:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            rtn_data.Data['key'] = data_df['data_time'].tolist()
                            rtn_data.Data['values'] = [
                                {
                                    'name': col['name'],
                                    'stack': col['stack'],
                                    'values': [round(v, 3) if pd.notna(v) else 0 for v in data_df[col['key']].tolist()]
                                }
                                for col in sun_categories
                            ]

                else:
                    pd_data = self.dao.get_ems_yearly_report(year=start_date.year)
                    if not pd_data.empty:
                        merge_df = pd.DataFrame()
                        for idx, row in pd_data.iterrows():
                            data_list = row['data_list']
                            data_df = pd.DataFrame(data_list)
                            data_df['data_time'] = data_df['month'].apply(
                                lambda x: f"{row['year']}")
                            if merge_df.empty:
                                merge_df = data_df
                            else:
                                merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                        if not merge_df.empty:
                            data_df = merge_df.groupby('data_time').sum().reset_index()
                            rtn_data.Data['key'] = data_df['data_time'].tolist()
                            rtn_data.Data['values'] = [
                                {
                                    'name': col['name'],
                                    'stack': col['stack'],
                                    'values': [round(v, 3) if pd.notna(v) else 0 for v in data_df[col['key']].tolist()]
                                }
                                for col in sun_categories
                            ]
            # 下載 CSV
            else:
                if report_type == 0:
                    if start_date is None or end_date is None:
                        raise Exception("報表參數錯誤")
                    start_date = start_date.replace(hour=0, minute=0, microsecond=0)
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    data_dict = self.dao.get_daily_report(start_date=start_date, end_date=end_date, need_data_list=1)

                elif report_type == 1:
                    if start_date is None or end_date is None:
                        raise Exception("報表參數錯誤")
                    last_day = calendar.monthrange(end_date.year, end_date.month)[1]
                    start_date = start_date.replace(day=1, hour=0, minute=0, microsecond=0)
                    end_date = end_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
                    data_dict = self.dao.get_monthly_report(start_date=start_date, end_date=end_date, need_data_list=1)

                else:
                    if start_date is None or end_date is None:
                        raise Exception("報表參數錯誤")
                    start_date = start_date.replace(month=1, day=1, hour=0, minute=0, microsecond=0)
                    end_date = end_date.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
                    data_dict = self.dao.get_yearly_report(start_date=start_date, end_date=end_date, need_data_list=1)

                merge_df = pd.DataFrame()
                if data_dict['total_count'] > 0:
                    for idx, row in data_dict['data'].iterrows():
                        data_list = row['data_list']
                        data_df = pd.DataFrame(data_list)
                        if report_type == 0:
                            data_df['data_time'] = data_df['hour'].apply(
                                lambda x: datetime(row['year'], row['month'], row['day'], x)
                                .strftime('%Y-%m-%d_%H'))
                            if merge_df.empty:
                                merge_df = data_df
                            else:
                                merge_df = pd.concat([merge_df, data_df], ignore_index=True)
                        elif report_type == 1:
                            data_df['data_time'] = data_df['day'].apply(
                                lambda x: datetime(row['year'], row['month'], x)
                                .strftime('%Y-%m-%d'))
                            if merge_df.empty:
                                merge_df = data_df
                            else:
                                merge_df = pd.concat([merge_df, data_df], ignore_index=True)
                        else:
                            data_df['data_time'] = data_df['month'].apply(
                                lambda x: datetime(row['year'], x, 1)
                                .strftime('%Y-%m'))
                            if merge_df.empty:
                                merge_df = data_df
                            else:
                                merge_df = pd.concat([merge_df, data_df], ignore_index=True)

                if not merge_df.empty:
                    keep_col = [
                        "data_time", pcs_in_key, pcs_out_key, "meter_charge_capacity", "meter_discharge_capacity",
                        "vcb_charge_capacity", "vcb_discharge_capacity"
                    ]
                    if report_type == 0:
                        keep_col.extend(["soc", "container_temp"])

                    merge_df = merge_df[keep_col]
                    file_name = f"儲能系統報表-{temp_s_date}~{temp_e_date}_{int(datetime.now().timestamp())}.csv"
                    byte_io = io.BytesIO()
                    merge_df.to_csv(byte_io, index=False)
                    byte_io.seek(0)
                    return send_file(byte_io, mimetype='text/csv', as_attachment=True, attachment_filename=file_name)
                else:
                    rtn_data.Msg = "查無資料"
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
