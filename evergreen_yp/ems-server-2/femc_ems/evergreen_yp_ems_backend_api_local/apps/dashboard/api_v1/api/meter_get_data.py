# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime

import numpy as np
import pandas as pd
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from utility.meter_map import MeterMapper
from utility.token_module import token_required, UserData
from . import Resource


class MeterGetData(Resource):
    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('Meter Get Data')
        pd_res = None
        try:

            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.METER_GET_DATA.value]:
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

            # get db_data
            dao_db = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao_db.get_system_equipment(name=equipment_id)
            brand_name = pd_data['brand'][0]

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            settings = FilesystemSettings(target_name_list=f'meter_{equipment_id}*', target_data=FolderType.History,
                                          base_path=dao.base_path, filter_date_star=fs_date, filter_date_end=fe_date)
            data = dao.read(criteria=settings)
            if data.empty:
                raise Exception('找不到相關檔案。')

            mapper = MeterMapper(brand_name, data)
            data = mapper.transfer_to_template()
            data = data.apply(pd.to_numeric, errors='ignore')
            data['data_time'] = pd.to_datetime(data['data_time'])
            condition = (data['data_time'] >= s_date) & (data['data_time'] <= e_date)
            data = data[condition]
            data = data.sort_values(by='data_time', ascending=True)

            pd_res = dict()
            columns = mapper.meter_column
            if data_type == 'minute':
                data.set_index('data_time', inplace=True)
                data = data.resample('1Min').apply(lambda x: x.sample(n=1) if not x.empty else 0)
                data.reset_index(inplace=True)

                if str(brand_name).lower() == 'ion-9000':
                    # 額外撈取accu資訊
                    settings = FilesystemSettings(target_name_list=f'accu_*', target_data=FolderType.History,
                                                  base_path=dao.base_path, filter_date_star=fs_date,
                                                  filter_date_end=fe_date)
                    accu_data = dao.read(criteria=settings)
                    accu_data = accu_data.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                    accu_data['data_time'] = pd.to_datetime(accu_data['data_time'])
                    condition = (accu_data['data_time'] >= s_date) & (accu_data['data_time'] <= e_date)
                    accu_data = accu_data[condition]
                    accu_data = accu_data.sort_values(by='data_time', ascending=True)
                    accu_data = accu_data[['data_time', 'ac_energy_imp', 'ac_energy_exp']]
                    accu_data = accu_data.rename(
                        columns={'ac_energy_imp': 'energy_imp', 'ac_energy_exp': 'energy_exp'})

                    # Accu處理
                    accu_data.set_index('data_time', inplace=True)
                    accu_data = accu_data.resample('1Min').max()
                    accu_data.reset_index(inplace=True)

                    # 組合
                    result = pd.merge(data, accu_data, on='data_time', suffixes=('_left', '_right'))
                    result['energy_imp'] = result['energy_imp_right'].combine_first(result['energy_imp_left'])
                    result['energy_exp'] = result['energy_exp_right'].combine_first(result['energy_exp_left'])
                    result.drop(['energy_imp_right', 'energy_imp_left', 'energy_exp_right', 'energy_exp_left'],
                                axis=1, inplace=True)
                    result = result.applymap(lambda x: None if isinstance(x, np.ndarray) and len(x) == 0 else x)
                    result = result.replace({np.nan: None})
                    data = result

                data = data.astype({'data_time': str})
                for col in columns:
                    pd_res[col] = list()
                    if col in data.columns:
                        val_list = data[['data_time', col]].values.tolist()
                        val_list = [[dt, 0 if pd.isnull(val) else val] for dt, val in val_list]
                        pd_res[col].extend(val_list)
                    else:
                        data[col] = None
                        pd_res[col].extend(data[['data_time', col]].values.tolist())
            else:
                data['data_time2'] = data['data_time'].dt.floor('ms')
                for col in columns:
                    pd_res[col] = list()
                    if col in data.columns:
                        val_list = data[['data_time2', col]].values.tolist()
                        val_list = [[dt, 0 if pd.isnull(val) else val] for dt, val in val_list]
                        pd_res[col].extend(val_list)
                    else:
                        data[col] = None
                        pd_res[col].extend(data[['data_time2', col]].values.tolist())

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': pd_res}, 200, None

