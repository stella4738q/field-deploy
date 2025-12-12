# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
import copy

import datetime
import numpy as np
import pandas as pd
from flask import request, make_response, send_file, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource


class BmsGetData(Resource):

    @token_required(token_module)
    def get(self):
        """
        取得 BMS資料
        """
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('BMS Get Data')
        pd_res = None
        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.BMS_GET_DOWNLOAD.value]:
                raise Exception('You dont have permission to access.')

            equipment_id = request.args[
                ApiConst.EQUIPMENT_ID.value] if ApiConst.EQUIPMENT_ID.value in request.args else None
            if equipment_id is None:
                raise Exception('equipment_id is required.')

            s_datetime = request.args[ApiConst.START_DATE.value] if ApiConst.START_DATE.value in request.args else None
            e_datetime = request.args[ApiConst.END_DATE.value] if ApiConst.END_DATE.value in request.args else None
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
            columns = [
                'data_time', 'soc', 'soh', 'voltage', 'current', 'daily_charging_capacity', 'daily_discharging_capacity',
                'total_charge_capacity', 'total_discharge_capacity'
            ]
            data = dao.read(criteria=settings, usecols=columns)
            if not data.empty:
                data = data.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                data = data.apply(pd.to_numeric, errors='ignore')
                data['data_time'] = pd.to_datetime(data['data_time'])
                condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
                data = data[condition]
                data = data.sort_values(by='data_time', ascending=True)

            if data.empty:
                raise Exception("查無資料")

            pd_res = dict()
            if data_type == 'minute':
                data.set_index('data_time', inplace=True)
                main_data = data.resample('1Min').apply(
                    lambda x: x.sample(n=1) if not x.empty else pd.DataFrame()
                )
                main_data.reset_index(inplace=True)
                main_data = main_data.astype({'data_time': str})
                for col in columns:
                    pd_res[col] = list()
                    pd_res[col].extend(main_data[['data_time', col]].values.tolist())
            else:
                data = data.groupby('data_time').first().reset_index()
                for col in columns:
                    pd_res[col] = list()
                    pd_res[col].extend(data[['data_time', col]].values.tolist())

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': pd_res}, 200, None

