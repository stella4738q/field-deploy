# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime

import numpy as np
import pandas as pd
from flask import request

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required
from . import Resource


class SystemBidWinningCurve(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('system bid winning curve')
        rtn_dict = {}
        try:
            field_id = request.args[ApiConst.FIELD_ID.value]
            equipment_id = request.args[ApiConst.EQUIPMENT_ID.value]
            date_time = request.args[ApiConst.DATE_TIME.value]

            if not date_time:
                date_time = datetime.now().strftime("%Y%m%d%H%M%S")

            sdate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 00:00:00")
            edate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 23:59:59")

            # get sbspm data
            logger.info('get sbspm data')
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_line_data = dao.get_SBSPM(sdate, edate, field_id, equipment_id)
            pd_line_data = pd_line_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_line_data.head(3)))

            cday = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y%m%d")
            sample_date = []
            for i in range(24):
                sample_date.append(f'{cday}{str(i).rjust(2, "0")}')
            map_df = pd.DataFrame({'time': sample_date, 'SBSPM_x': None, 'capacity(MW)_x': None})

            # groupby
            if not pd_line_data.empty:
                pd_line_data['time'] = pd.to_datetime(pd_line_data["time"])
                line_df = pd_line_data.assign(GroupKey=lambda x: pd_line_data['time'].dt.strftime("%Y%m%d%H"))
                line_df = line_df.groupby(by=["GroupKey"], dropna=False).mean().reset_index()

                result_data = map_df.merge(line_df, left_on='time', right_on='GroupKey', how='left')
                sbspm = result_data['SBSPM'].tolist()
                sbspm = [None if np.isnan(item) else item for item in sbspm]

                rtn_dict['x'] = pd.to_datetime(result_data['time_x'], format="%Y%m%d%H").tolist()
                rtn_dict['y'] = sbspm
            else:
                rtn_dict['x1'] = pd.to_datetime(map_df['time'], format="%Y%m%d%H").tolist()
                rtn_dict['y1'] = map_df['SBSPM_x'].tolist()

            # get capacity data
            logger.info('get capacity data')
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_his_data = dao.get_winning(sdate, edate, field_id)
            pd_his_data = pd_his_data.replace({np.nan: None})
            logger.debug('\nraw data: \n{}\n'.format(pd_his_data.head(3)))

            if not pd_his_data.empty:
                pd_his_data['start_time'] = pd.to_datetime(pd_his_data["start_time"])
                pd_his_data = pd_his_data.assign(GroupKey=lambda x: pd_his_data['start_time'].dt.strftime("%Y%m%d%H"))

                result_data = map_df.merge(pd_his_data, left_on='time', right_on='GroupKey', how='left')
                capacity = result_data['capacity(MW)'].tolist()
                capacity = [None if np.isnan(item) else item for item in capacity]

                rtn_dict['x2'] = pd.to_datetime(result_data['time'], format="%Y%m%d%H").tolist()
                rtn_dict['y2'] = capacity
            else:
                rtn_dict['x2'] = pd.to_datetime(map_df['time'], format="%Y%m%d%H").tolist()
                rtn_dict['y2'] = map_df['capacity(MW)_x'].tolist()

            rtn_dict['label'] = {'y1': 'SBSPM', 'y2': 'Mw'}

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': rtn_dict}, 200, None