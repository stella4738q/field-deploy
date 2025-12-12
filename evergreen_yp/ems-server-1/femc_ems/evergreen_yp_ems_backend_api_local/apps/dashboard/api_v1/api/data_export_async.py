# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import ast
import copy
import io
import os
import threading
import zipfile
from datetime import datetime, time

import numpy as np
import pandas as pd
from flask import request, session, make_response, jsonify, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource
from utility.meter_map import MeterMapper
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst


class DataExportAsync(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] data export')
        rtn_data = ApiResponse()
        rtn_data.data = list()
        rtn_data.process_done = False
        rtn_data.success = True

        try:
            payload = request.args
            equipment_id = payload.get(ApiConst.EQUIPMENT_ID.value,
                                       None)  # PCS_1, BMS_1, METER_MAIN, METER_SUN, METER_FACTORY, METER_CABINET
            data_type = 'pcs' if 'pcs' in str(equipment_id).lower() else 'bmu' if 'bmu' in str(
                equipment_id).lower() else 'meter'
            if equipment_id == 'BMU':
                equipment_id = ['BMU_1', 'BMU_2']
            elif equipment_id == 'METER':
                equipment_id = ['METER_MAIN', 'METER_SUN', 'METER_FACTORY', 'METER_CABINET', 'METER_VCB']

            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('你沒有權限查詢')

            if (data_type == 'pcs' and
                not user_info.user_field_permission[field][PermissionConst.PCS_POST_DOWNLOAD.value]) or \
                    (data_type == 'bmu' and
                     not user_info.user_field_permission[field][PermissionConst.BMS_GET_DOWNLOAD.value]) or \
                    (data_type == 'meter' and
                     not user_info.user_field_permission[field][PermissionConst.METER_GET_DOWNLOAD.value]):
                raise Exception('你沒有權限查詢.')

            # 查詢是否有紀錄
            pd_data = self.dao.get_async_export_data(user_info.user_id, equipment_id)
            if not pd_data.empty:
                for idx, item in pd_data.iterrows():
                    item: dict = pd_data.iloc[idx].to_dict()
                    item['created_on'] = item['creator']['created_on']
                    item['start_date'] = datetime.strptime(item['start_date'], '%Y%m%d%H%M%S')
                    item['end_date'] = datetime.strptime(item['end_date'], '%Y%m%d%H%M%S')
                    item.pop('_id')
                    item.pop('export_data')
                    item.pop('creator')
                    rtn_data.data.append(item)

            else:
                rtn_data.data = pd_data.to_dict('records')

            rtn_data.msg = SUCCESS_MESSAGE
        except Exception as e:
            rtn_data.success = False
            rtn_data.msg = str(e)
        return {'message': rtn_data.msg, 'data': rtn_data.data, 'success': rtn_data.success}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[get] data export')
        rtn_data = ApiResponse()
        rtn_data.data = None
        rtn_data.process_done = False
        rtn_data.success = True

        try:
            payload = request.get_json()
            equipment_id = payload[
                ApiConst.EQUIPMENT_ID.value]  # PCS_1, BMU_1, METER_MAIN, METER_SUN, METER_FACTORY, METER_CABINET
            data_type = 'pcs' if 'pcs' in str(equipment_id).lower() else 'bmu' if 'bmu' in str(
                equipment_id).lower() else 'meter'
            time_type = payload.get(ApiConst.TIME_TYPE.value, None)
            is_rack = payload.get(ApiConst.IS_RACK.value, False)

            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field:
                raise Exception('你沒有權限下載')

            if (data_type == 'pcs' and
                not user_info.user_field_permission[field][PermissionConst.PCS_POST_DOWNLOAD.value]) or \
                    (data_type == 'bmu' and
                     not user_info.user_field_permission[field][PermissionConst.BMS_GET_DOWNLOAD.value]) or \
                    (data_type == 'meter' and
                     not user_info.user_field_permission[field][PermissionConst.METER_GET_DOWNLOAD.value]):
                raise Exception('你沒有權限下載.')

            # 查詢是否有紀錄
            pd_data = self.dao.get_async_export_data(user_info.user_id, equipment_id)
            if not pd_data.empty:
                data = pd_data.iloc[0]
                if data['process_done']:
                    file_path = data['export_data']
                    if file_path:
                        return_data = io.BytesIO()
                        with open(file_path, 'rb') as fo:
                            return_data.write(fo.read())
                            return_data.seek(0)
                        os.remove(f'{file_path}')
                        self.dao.delete_async_export([data['_id']])

                        _, file_extension = os.path.splitext(file_path)
                        if file_extension == ".zip":
                            return send_file(
                                return_data, mimetype='application/zip',
                                as_attachment=True,
                                attachment_filename=f"{equipment_id}.zip")

                        elif file_extension == ".csv":
                            return send_file(
                                return_data, mimetype='text/csv',
                                as_attachment=True,
                                attachment_filename=f"{equipment_id}.csv")
                        else:
                            raise NotImplementedError(f"未知的副檔名: {file_extension}")
                    else:
                        rtn_data.msg = data['process_msg']
                        self.dao.delete_async_export([data['_id']])
                else:
                    created_on = data['creator']['created_on']
                    if (datetime.now() - created_on).total_seconds() <= 600:  # 10分鐘當timeout
                        raise Exception("資料尚在準備，請稍後在嘗試下載")
                    else:
                        self.dao.delete_async_export([data['_id']])

            else:
                s_datetime = payload.get(ApiConst.START_DATE.value, None)
                e_datetime = payload.get(ApiConst.END_DATE.value, None)
                if not s_datetime or not e_datetime:
                    raise Exception('start and end date time is required.')

                creator = {
                    'id': user_info.user_id,
                    'name': user_info.user_name,
                    'created_on': datetime.now()
                }
                new_id = self.dao.create_async_export_data(equipment_id, s_datetime, e_datetime, creator)
                task = threading.Thread(
                    target=self.do_async_job,
                    args=(new_id, data_type, equipment_id, s_datetime, e_datetime, time_type, is_rack))
                task.start()
                rtn_data.msg = '資料準備中，請等待3-5分鐘後，再次進行下載'

        except Exception as e:
            rtn_data.success = False
            rtn_data.msg = str(e)
        return {'message': rtn_data.msg, 'data': rtn_data.data, 'success': rtn_data.success}, 200, None

    def do_async_job(self, target_id, data_type, equipment_id, s_datetime, e_datetime, time_type, is_rack):
        s_date = datetime.strptime(s_datetime, '%Y%m%d%H%M%S')
        s_date = s_date.replace(second=0, microsecond=0)

        e_date = datetime.strptime(e_datetime, '%Y%m%d%H%M%S')
        e_date = e_date.replace(second=59, microsecond=999999)

        fs_date = datetime.combine(s_date, time(s_date.hour))
        fe_date = datetime.combine(e_date, time(e_date.hour))

        dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
        settings = FilesystemSettings(target_name_list=f'{data_type}_{equipment_id}*', target_data=FolderType.History,
                                      base_path=dao.base_path, filter_date_star=fs_date, filter_date_end=fe_date)

        if data_type == 'pcs':
            data = dao.read(criteria=settings)
            if data.empty:
                self.dao.update_async_export_data(target_id, None, True, "查無相關資料")
                return

            data = data.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
            data['data_time'] = pd.to_datetime(data['data_time'])
            condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
            data = data[condition]
            data = data.sort_values(by='data_time', ascending=True)

            if time_type == 'minute':
                data.set_index('data_time', inplace=True)
                data = data.resample('1Min').apply(
                    lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                )
                data.reset_index(inplace=True)
                data = data.astype({'data_time': str})

            file_path = f'{self.temp_folder}/{target_id}.csv'
            data.to_csv(file_path, sep=',', encoding='utf-8', index=False)
            self.dao.update_async_export_data(target_id, file_path, True, "")

        elif data_type == 'bmu':
            if is_rack:
                filter_columns = ["data_time", "rack_list"]
            else:
                filter_columns = ["data_time", "field_id", "case_id", "resource_id", "equipment_id", "parent_id",
                                  "voltage", "current", "soc", "soh", "max_cell_voltage", "max_cell_volt_rack_address",
                                  "max_cell_volt_point_address", "min_cell_voltage", "min_cell_volt_rack_address",
                                  "min_cell_volt_point_address", "max_cell_temperature", "max_cell_temp_rack_address",
                                  "max_cell_temp_point_address", "min_cell_temperature", "min_cell_temp_rack_address",
                                  "min_cell_temp_point_address", "total_charge_capacity", "total_discharge_capacity",
                                  "allow_charge_capacity", "allow_discharge_capacity", "allow_charge_max_power",
                                  "allow_discharge_max_power", "allow_charge_max_current", "allow_discharge_max_current",
                                  "daily_charging_capacity", "daily_discharging_capacity", "operating_temperature",
                                  "status_code", "status", "insulation_resistance", "cycle", "equivalent_cycle", "dod",
                                  "humidity", "active_power", "reactive_power", "apparent_power", "freq", "fan_status",
                                  "fan_error", "fire", "container_temp_a", "container_humidity_a", "container_temp_b",
                                  "container_humidity_b", "heartbeat", "tms_status_code", "tms_status",
                                  "tms_outlet_temp", "tms_return_temp", "tms_inlet_pressure", "tms_outlet_pressure",
                                  "tms_fault_code", "tms_fault", "tms_fault_level", "ups_status_code", "ups_status",
                                  "ups_soc", "abnormal"]
            data = dao.read(criteria=settings, usecols=filter_columns)
            if data.empty:
                self.dao.update_async_export_data(target_id, None, True, "查無相關資料")
                return
            data = data.replace({'None': None, 'nan': None, np.NAN: None})
            data['data_time'] = pd.to_datetime(data['data_time'])
            condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
            bmu_df = data[condition]
            bmu_df = bmu_df.sort_values(by='data_time', ascending=True)

            if bmu_df.empty:
                raise Exception("查無資料")

            if is_rack:
                def preprocess_rack_list(r_list, data_time):
                    replace = True
                    while replace:
                        s_idx = r_list.find("datetime.datetime(")
                        if s_idx == -1:
                            replace = False
                        else:
                            e_idx = r_list.find(')', s_idx)
                            target_replace = r_list[s_idx: e_idx + 1]
                            replace_to = eval(target_replace.replace('datetime.', ''))
                            r_list = r_list.replace(target_replace, f'"{str(replace_to)}"')

                    racks = ast.literal_eval(r_list)
                    rtn_list = list()
                    for rack in racks:
                        rack.pop('warning', None)
                        rack.pop('packs', None)
                        rack.pop('time', None)

                        new_rack = {}
                        for idx, (key, value) in enumerate(rack.items()):
                            if idx == 0:
                                new_rack['data_time'] = pd.Timestamp(data_time).to_pydatetime()
                            new_rack[key] = value
                        rtn_list.append(new_rack)
                    return rtn_list

                bmu_df['data_time'] = pd.to_datetime(bmu_df['data_time'])
                bmu_df['rack_list'] = bmu_df['rack_list'] \
                    .replace("\'", "\"") \
                    .replace("]'", "]").replace("'[", "[").replace("False", 'false') \
                    .replace("True", 'true').replace('None', 'null')

                time_list_np = bmu_df['data_time'].to_numpy()
                rack_list_np = bmu_df['rack_list'].to_numpy()
                racks_np = np.vectorize(preprocess_rack_list)(rack_list_np, time_list_np)
                rack_list = [rack for sublist in racks_np for rack in sublist]
                # 產生df
                rdf = pd.DataFrame(rack_list)

                all_rack_df = pd.DataFrame(columns=rdf.columns)
                if time_type == 'minute':
                    gdf = rdf.groupby('equipment_id')
                    for key, rack_df in gdf:
                        rack_df.set_index('data_time', inplace=True)
                        rack_df = rack_df.resample('1Min').apply(
                            lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                        )
                        rack_df.reset_index(inplace=True)
                        rack_df = rack_df.astype({'data_time': str})
                        all_rack_df = all_rack_df.append(rack_df, ignore_index=True)
                        all_rack_df = all_rack_df.sort_values(by=['data_time', 'rack_no'], ascending=True)
                else:
                    all_rack_df = rdf

                # 匯出csv
                file_path = f'{self.temp_folder}/{target_id}_rack.csv'
                all_rack_df.to_csv(file_path, sep=',', encoding='utf-8', index=False)
                self.dao.update_async_export_data(target_id, file_path, True, "")
            else:
                # main
                main_df = copy.deepcopy(bmu_df)

                if time_type == 'minute':
                    main_df.set_index('data_time', inplace=True)
                    main_df = main_df.resample('1Min').apply(
                        lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                    )
                    main_df.reset_index(inplace=True)
                    main_df = main_df.astype({'data_time': str})

                # 匯出csv
                file_path = f'{self.temp_folder}/{target_id}.csv'
                main_df.to_csv(file_path, sep=',', encoding='utf-8', index=False)
                self.dao.update_async_export_data(target_id, file_path, True, "")

        else:
            data = dao.read(criteria=settings)
            if data.empty:
                self.dao.update_async_export_data(target_id, None, True, "查無相關資料")
                return
            pd_data = self.dao.get_system_equipment(name=equipment_id)
            brand_name = pd_data['brand'][0]
            mapper = MeterMapper(brand_name, data)
            data = mapper.transfer_to_template()
            data = data.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
            data['data_time'] = pd.to_datetime(data['data_time'])
            condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
            data = data[condition]
            data = data.sort_values(by='data_time', ascending=True)

            if time_type == 'minute':
                data.set_index('data_time', inplace=True)
                data = data.resample('1Min').apply(
                    lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                )
                data.reset_index(inplace=True)
                data = data.astype({'data_time': str})

            file_path = f'{self.temp_folder}/{target_id}.csv'
            data.to_csv(file_path, sep=',', encoding='utf-8', index=False)
            self.dao.update_async_export_data(target_id, file_path, True, "")
