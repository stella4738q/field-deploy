# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import numpy as np
import pandas as pd
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class BmuGetData(Resource):

    @staticmethod
    def get_col_by_brand(brand):
        col = list()
        if 'sungrow' == str(brand).lower():
            # outlet_water_temperature = 0  # 出水溫度
            # inlet_water_temperature = 0  # 回水溫度
            # outlet_water_pressure = 0  # 出水壓力
            # inlet_water_pressure = 0  # 回水壓力
            # cell_voltage_difference = 0  # 電芯壓差
            # cell_temperature_difference = 0  # 電芯溫差
            # bus_voltage = 0  # 母線電壓
            # bus_current = 0  # 母線電流
            col = [
                'outlet_water_temperature', 'inlet_water_temperature', 'outlet_water_pressure', 'inlet_water_pressure',
                'cell_voltage_difference', 'cell_temperature_difference', 'bus_voltage', 'bus_current'
            ]
        return col

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('Meter BMS Data')
        pd_res = None
        try:
            brand = request.args[
                ApiConst.BRAND.value] if ApiConst.BRAND.value in request.args else None
            if brand is None:
                raise Exception('brand is required.')

            equipment_id = request.args[
                ApiConst.EQUIPMENT_ID.value] if ApiConst.EQUIPMENT_ID.value in request.args else None
            if equipment_id is None:
                raise Exception('equipment_id is required.')

            s_datetime = request.args[ApiConst.START_TIME.value] if ApiConst.START_TIME.value in request.args else None
            e_datetime = request.args[ApiConst.END_TIME.value] if ApiConst.END_TIME.value in request.args else None
            if not s_datetime or not e_datetime:
                raise Exception('start and end date time is required.')

            s_date = datetime.datetime.strptime(s_datetime, '%Y%m%d%H%M%S')
            e_date = datetime.datetime.strptime(e_datetime, '%Y%m%d%H%M%S')

            fs_date = datetime.datetime.combine(s_date, datetime.time(s_date.hour))
            fe_date = datetime.datetime.combine(e_date, datetime.time(e_date.hour))

            data_type = request.args[ApiConst.DATE_TYPE.value] if ApiConst.DATE_TYPE.value in request.args else None

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            settings = FilesystemSettings(target_name_list=f'bmu_{equipment_id}*', target_data=FolderType.History,
                                          base_path=dao.base_path, filter_date_star=fs_date, filter_date_end=fe_date)
            data = dao.read(criteria=settings)
            if not data.empty:
                data = data.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                data['data_time'] = pd.to_datetime(data['data_time'])
                condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
                data = data[condition]
                data = data.sort_values(by='data_time', ascending=True)

                pd_res = dict()
                columns = self.get_col_by_brand(brand)
                if data_type == 'minute':
                    data.set_index('data_time', inplace=True)
                    data = data.resample('1Min').apply(
                        lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                    )
                    data.reset_index(inplace=True)
                    data = data.astype({'data_time': str})
                    for col in columns:
                        pd_res[col] = list()
                        pd_res[col].extend(data[['data_time', col]].values.tolist())
                else:
                    for col in columns:
                        pd_res[col] = list()
                        pd_res[col].extend(data[['data_time', col]].values.tolist())
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': pd_res}, 200, None

