# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime
import pandas as pd
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from logging_utils.logger import Logger
from . import Resource


class MeterGetDataThinjs(Resource):

    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('alert real time')
        pd_res = {
            "voltage": {
                "style": [
                    {
                        "name": "Vab",
                        "color": "#F5A623"
                    },
                    {
                        "name": "Vbc",
                        "color": "#2C9880"
                    },
                    {
                        "name": "Vca",
                        "color": "#C42236"
                    },
                ],
                "data": {
                    "Vab": [],
                    "Vbc": [],
                    "Vca": []
                }
            },
            "current": {
                "style": [
                    {
                        "name": "la",
                        "color": "#F5A623"
                    },
                    {
                        "name": "lb",
                        "color": "#2C9880"
                    },
                    {
                        "name": "lc",
                        "color": "#C42236"
                    },
                ],
                "data": {
                    "la": [],
                    "lb": [],
                    "lc": []
                }
            }
        }
        try:
            equipment_id = request.args[
                ApiConst.EQUIPMENT_ID.value] if ApiConst.EQUIPMENT_ID.value in request.args else None
            if equipment_id is None:
                raise Exception('equipment_id is required.')

            if ApiConst.DATE.value in request.args and request.args[ApiConst.DATE.value]:
                date = request.args[ApiConst.DATE.value]
                current_date = datetime.datetime.strptime(date, '%Y%m%d')
            else:
                current_date = datetime.datetime.now()

            s_date = datetime.datetime.combine(current_date, datetime.time(0, 0, 0))
            e_date = datetime.datetime.combine(current_date, datetime.time(23, 59, 59))

            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
            settings = FilesystemSettings(target_name_list=f'*_{equipment_id}', target_data=FolderType.History,
                                          base_path=dao.base_path, filter_date_star=s_date, filter_date_end=e_date)
            data = dao.read(criteria=settings)
            if not data.empty:
                data.set_index('data_time', inplace=True)
                data.index = pd.to_datetime(data.index)
                data = data.resample('5Min').apply(lambda x: x.sample(n=1))
                data.reset_index(inplace=True)

                data['data_time'] = data['data_time'].apply(
                    lambda x: int(pd.Timestamp(x, tz='UTC').timestamp() * 1000))

                data = data.astype({'data_time': str})
                pd_res['voltage']['data']['Vab'] = data[['data_time', 'v_phs_ab']].values.tolist()
                pd_res['voltage']['data']['Vbc'] = data[['data_time', 'v_phs_bc']].values.tolist()
                pd_res['voltage']['data']['Vca'] = data[['data_time', 'v_phs_ca']].values.tolist()

                volt = pd_res['voltage']['data']
                for item, item1, item2 in zip(volt['Vab'], volt['Vbc'], volt['Vca']):
                    item[0] = int(item[0])
                    item1[0] = int(item1[0])
                    item2[0] = int(item2[0])

                pd_res['current']['data']['la'] = data[['data_time', 'i_phs_a']].values.tolist()
                pd_res['current']['data']['lb'] = data[['data_time', 'i_phs_b']].values.tolist()
                pd_res['current']['data']['lc'] = data[['data_time', 'i_phs_c']].values.tolist()

                idata = pd_res['current']['data']
                for item, item1, item2 in zip(idata['la'], idata['lb'], idata['lc']):
                    item[0] = int(item[0])
                    item1[0] = int(item1[0])
                    item2[0] = int(item2[0])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': pd_res}, 200, None
