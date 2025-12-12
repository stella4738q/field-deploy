# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import pickle
from operator import attrgetter

from itertools import groupby
from typing import List

import numpy as np
import json
import pandas as pd
from flask import request, session
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.rack_helper import RackInfo, get_bmu_data, replace_json_string
from utility.token_module import token_required, UserData
from . import Resource
from dashboard_lib.constant import ConfigConstant
import io
import os
from flask import request, send_file
from io import BytesIO


class GetRackTrandDataExport(Resource):
    @staticmethod
    def extract_number(element):
        return int(element.split('_')[1])

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('Get Rack Trand Data')
        pd_dict = list()
        data_str = ""

        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.BMS_GET_DOWNLOAD.value]:
                raise Exception('You dont have permission to access.')

            now = datetime.datetime.now()
            s_datetime = request.args[ApiConst.DATEBEGIN.value] if ApiConst.DATEBEGIN.value in request.args \
                else (now - datetime.timedelta(hours=1)).strftime("%Y%m%d%H%M%S")
            e_datetime = request.args[ApiConst.DATEEND.value] if ApiConst.DATEEND.value in request.args else now.strftime("%Y%m%d%H%M%S")
            if ApiConst.BMSFILENAME.value not in request.args or request.args[ApiConst.BMSFILENAME.value] is None:
                raise Exception(f'please enter [ {ApiConst.BMSFILENAME.value} ]')

            if ApiConst.LEVEL.value not in request.args or request.args[ApiConst.LEVEL.value] == "":
                raise Exception(f'please enter [ {ApiConst.LEVEL.value} ]')
            level = request.args[ApiConst.LEVEL.value]  # rack/pack/cell required

            if ApiConst.TYPE.value not in request.args or request.args[ApiConst.TYPE.value] == "":
                raise Exception(f'please enter [ {ApiConst.TYPE.value} ]')
            _type = request.args[ApiConst.TYPE.value]  # temp/current/voltage required
            #  pack & cell 沒有 current
            if (level == ApiConst.PACK.value or level == ApiConst.CELL.value) and _type == 'current':
                raise Exception('pack & cell 沒有 current data')

            # rack: level = pack, rack is required
            if level == ApiConst.PACK.value and (ApiConst.RACK.value not in request.args or request.args[ApiConst.RACK.value] == ""):
                raise Exception(f'your level is pack, [ {ApiConst.RACK.value} ] is required.')
            rack = request.args['rack']

            # pack: level = cell,  rack & pack is required
            if level == ApiConst.CELL.value and \
                    ((ApiConst.RACK.value not in request.args or request.args[ApiConst.RACK.value] == "")
                     or (ApiConst.PACK.value not in request.args or request.args[ApiConst.PACK.value] == "")):
                raise Exception(f'your level is pack, [ {ApiConst.RACK.value} ] & [ {ApiConst.PACK.value} ] is required.')
            pack = request.args[ApiConst.PACK.value]

            s_date = datetime.datetime.strptime(s_datetime, '%Y%m%d%H%M%S')
            e_date = datetime.datetime.strptime(e_datetime, '%Y%m%d%H%M%S')

            fs_date = datetime.datetime.combine(s_date, datetime.time(s_date.hour))
            fe_date = datetime.datetime.combine(e_date, datetime.time(e_date.hour))

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            settings = FilesystemSettings(target_name_list=f'bmu_*', target_data=FolderType.History,
                                          base_path=dao.base_path, filter_date_star=fs_date, filter_date_end=fe_date)
            bmu_data = dao.read(criteria=settings)
            if bmu_data.empty:
                raise Exception('找不到相關檔案。')
            bmu_data = bmu_data[
                (pd.to_datetime(bmu_data['data_time']) >= s_date) &
                (pd.to_datetime(bmu_data['data_time']) < e_date + datetime.timedelta(seconds=1))
            ]

            rack_info_res: List[RackInfo] = list()
            if not bmu_data.empty:

                # 時間轉換
                bmu_data['data_time'] = pd.to_datetime(bmu_data['data_time'], format='%Y-%m-%d %H:%M:%S')
                # Rack Json轉換
                bmu_data = bmu_data[['data_time', 'equipment_id', 'rack_list']]
                bmu_data['rack_list'] = bmu_data['rack_list'].apply(replace_json_string)

                def parser_rack(row):
                    data_time = row['data_time']
                    rack_data = pd.DataFrame(eval(row['rack_list']))
                    racks = get_bmu_data(data_time, rack_data, _type, level, rack, pack)
                    if racks:
                        rack_info_res.extend(racks)

                # 取資料
                bmu_data.apply(parser_rack, axis=1)
                if len(rack_info_res) > 0:
                    rack_info_res = sorted(rack_info_res, key=lambda x: x.data_time)

                    # 時間
                    date_list = sorted(set(
                        datetime.datetime.strftime(rack.data_time, '%Y%m%d%H%M%S') for rack in rack_info_res))
                    date_list = {
                        'name': 'datetime',
                        'data': date_list
                    }
                    pd_dict.append(date_list)

                    # rack
                    grouped = groupby(sorted(rack_info_res, key=attrgetter('name')), key=attrgetter('name'))
                    grouped_dict = {key: [g.data for g in group] for key, group in grouped}
                    for group_name in list(grouped_dict):
                        pd_dict.append({
                            'name': group_name,
                            'data': grouped_dict[group_name]
                        })

                if pd_dict:
                    # 轉換成 DataFrame
                    data = {item['name']: item['data'] for item in pd_dict}
                    df = pd.DataFrame(data)

                    # # 處理缺失值
                    df = df.replace({None: 0, 'None': 0, np.nan: 0, 'NaN': 0})
                    # 將 'datetime' 列轉換為日期時間格式
                    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d%H%M%S')

                    bytes_io = BytesIO(df.to_csv(index=False, encoding="UTF-8").encode())
                    return send_file(
                        bytes_io, mimetype="text/csv",
                        as_attachment=True, attachment_filename='data.csv')

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': data_str}, 200, None
