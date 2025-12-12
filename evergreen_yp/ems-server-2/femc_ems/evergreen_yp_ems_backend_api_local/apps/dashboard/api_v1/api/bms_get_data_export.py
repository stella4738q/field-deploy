# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import ast
import copy
import datetime
import io
import json
import zipfile
from io import BytesIO

import numpy as np
import pandas as pd
from flask import request, session, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.rack_helper import replace_json_string
from utility.token_module import token_required, UserData
from . import Resource


class BmsGetDataExport(Resource):
    """
    報表-BMS資料匯出
    新版請使用 get_rack_trand_data_export
    """
    @token_required(token_module)
    def get(self):
        logger = Logger().create('Advanced-tek API', level=logging_level, log_path=log_path)
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
            e_datetime = request.args[ApiConst.START_DATE.value] if ApiConst.END_DATE.value in request.args else None
            if not s_datetime or not e_datetime:
                raise Exception('start and end date time is required.')

            s_date = datetime.datetime.strptime(s_datetime, '%Y%m%d%H%M%S')
            s_date = s_date.replace(second=0, microsecond=0)

            e_date = datetime.datetime.strptime(e_datetime, '%Y%m%d%H%M%S')
            e_date = e_date.replace(second=59, microsecond=999999)

            fs_date = datetime.datetime.combine(s_date, datetime.time(s_date.hour))
            fe_date = datetime.datetime.combine(e_date, datetime.time(e_date.hour))

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            settings = FilesystemSettings(target_name_list=f'bmu_{equipment_id}*', target_data=FolderType.History,
                                          base_path=dao.base_path, filter_date_star=fs_date, filter_date_end=fe_date)
            bmu_df = dao.read(criteria=settings)
            if not bmu_df.empty:
                bmu_df = bmu_df.replace({'None': None, 'nan': None, np.NAN: None})
                bmu_df = bmu_df.apply(pd.to_numeric, errors='ignore')

                bmu_df['data_time'] = pd.to_datetime(bmu_df['data_time'])
                condition = (bmu_df['data_time'] >= s_date) & (bmu_df['data_time'] <= e_date)
                bmu_df = bmu_df[condition]
                bmu_df = bmu_df.sort_values(by='data_time', ascending=True)

                if bmu_df.empty:
                    raise Exception("查無資料")

                # 將檔案分成2分
                buffer = io.BytesIO()

                # main
                main_df = copy.deepcopy(bmu_df)
                main_df = main_df.drop(['rack_list', 'warning'], axis=1)

                def preprocess_rack_list(r_list, data_time):
                    racks = ast.literal_eval(r_list)
                    rtn_list = list()
                    for rack in racks:
                        rack.pop('warning', None)
                        rack.pop('packs', None)

                        new_rack = {}
                        for idx, (key, value) in enumerate(rack.items()):
                            if idx == 0:
                                new_rack['data_time'] = pd.Timestamp(data_time).to_pydatetime()
                            new_rack[key] = value
                        rtn_list.append(new_rack)
                    return rtn_list

                bmu_df['data_time'] = pd.to_datetime(bmu_df['data_time'])
                bmu_df['rack_list'] = bmu_df['rack_list'] \
                    .replace("]'", "]").replace("'[", "[").replace("False", 'false')\
                    .replace("True", 'true').replace('None', 'null')

                time_list_np = bmu_df['data_time'].to_numpy()
                rack_list_np = bmu_df['rack_list'].to_numpy()
                racks_np = np.vectorize(preprocess_rack_list)(rack_list_np, time_list_np)
                rack_list = [rack for sublist in racks_np for rack in sublist]
                # 產生df
                rack_df = pd.DataFrame(rack_list)

                # 匯出Zip
                with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    main_df_buffer = io.BytesIO()
                    main_df.to_csv(main_df_buffer, index=False)
                    zip_file.writestr('bmu_data.csv', main_df_buffer.getvalue())

                    rack_df_buffer = io.BytesIO()
                    rack_df.to_csv(rack_df_buffer, index=False)
                    zip_file.writestr('rack_data.csv', rack_df_buffer.getvalue())

                buffer.seek(0)

                return send_file(
                    buffer, mimetype='application/zip',
                    as_attachment=True, attachment_filename=f"{equipment_id}.zip")
            raise Exception("查無資料")
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': pd_res}, 200, None

