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


class QualitySbspm(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('quality sbspm')
        rtn_dict = {}
        try:
            field_id = request.args[ApiConst.FIELD_ID.value]
            equipment_id = request.args[ApiConst.EQUIPMENT_ID.value]
            date_time = request.args[ApiConst.DATE_TIME.value]

            if not date_time:
                date_time = datetime.now().strftime("%Y%m%d%H%M%S")

            sdate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 00:00:00")
            edate = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d 23:59:59")

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_SBSPM(sdate, edate, field_id, equipment_id)
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            if not pd_data.empty:
                # groupby
                pd_data['time'] = pd.to_datetime(pd_data["time"])
                df = pd_data.assign(GroupKey=lambda x: pd_data['time'].dt.strftime("%Y%m%d%H"))
                df = df.groupby(by=["GroupKey"], dropna=False).mean().reset_index()

                cday = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%Y%m%d")
                sample_date = []
                for i in range(24):
                    sample_date.append(f'{cday}{str(i).rjust(2, "0")}')
                map_df = pd.DataFrame({'time': sample_date})
                result_data = map_df.merge(df, left_on='time', right_on='GroupKey', how='left')
                sbspm = result_data['sbspm'].tolist()
                result_data = result_data.replace({np.nan: None})
                sbspm = [None if np.isnan(item) else item for item in sbspm]

                rtn_dict['x'] = pd.to_datetime(result_data['time'], format="%Y%m%d%H").tolist()
                rtn_dict['y'] = sbspm

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': rtn_dict}, 200, None