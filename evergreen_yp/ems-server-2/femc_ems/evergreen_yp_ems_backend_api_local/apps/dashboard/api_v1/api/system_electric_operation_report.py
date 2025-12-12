# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
import pandas as pd
from flask import request, session
from datetime import datetime
from datetime import timedelta
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.geo_location import coordination
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from modbus_tk import modbus_tcp
from dashboard_lib.modbus_template import BrandController
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType, FileExtension

from . import Resource


class SystemElectricOperationReport(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system electric operation report')
        pd_res=[]
        try:
            start_date = None
            end_date = None
            category = None
            if ApiConst.START_DATE.value in request.args:
                start_date = request.args[ApiConst.START_DATE.value]
            if ApiConst.END_DATE.value in request.args:
                end_date = request.args[ApiConst.END_DATE.value]
            if ApiConst.CATEGORY.value in request.args:
                category = int(request.args[ApiConst.CATEGORY.value])

            sdate = datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d %H:%M:%S")
            edate = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d 23:59:59")

            pd_data = self.dao.get_electric_report(sdate, edate)
            if not pd_data.empty:
                pd_data[ApiConst.DURATION.value] = pd_data[ApiConst.END_DATE.value] - pd_data[ApiConst.START_DATE.value]

                if category == 0:
                    pd_rnt_data = pd_data[['start_date', 'action', 'degree', 'total_price', 'duration']].\
                        rename(columns={"total_price": "total_amount", "start_date": "date"})
                elif category == 1:
                    pd_rnt_data = pd_data.groupby(
                        [pd.Grouper(key='start_date', freq='M'), 'action'])\
                        .agg(degree=("degree", "sum"), total_amount=('total_price', 'sum'),duration=('duration', 'sum'))\
                        .reset_index()
                    pd_rnt_data = pd_rnt_data.rename(columns={"start_date": "date"})
                else:
                    pd_rnt_data = pd_data.groupby([pd.Grouper(key='start_date', freq='Y'), 'action']).agg(
                        degree=("degree", "sum"),
                        total_amount=('total_price', 'sum'),
                        duration=('duration', 'sum')).reset_index()
                    pd_rnt_data = pd_rnt_data.rename(columns={"start_date": "date"})

                # get plot data
                pd_action = pd_rnt_data.groupby([pd.Grouper(key='date', freq='D'), 'action']). \
                    agg(total_amount=(ApiConst.TOTAL_AMOUNT.value, "sum"), ).reset_index()

                if category == 0 :
                    pd_revenue = pd_rnt_data.groupby([pd.Grouper(key=ApiConst.DATE.value, freq='D')])\
                        .agg(revenue=(ApiConst.TOTAL_AMOUNT.value, "sum"), ).reset_index()
                else:
                    pd_revenue = pd_rnt_data.groupby(ApiConst.DATE.value)\
                        .agg(revenue=(ApiConst.TOTAL_AMOUNT.value, "sum"), ).reset_index()

                pd_action_pivot = pd_action.pivot(index='date', columns='action', values='total_amount').reset_index()
                merged_df = pd_revenue.merge(pd_action_pivot, on='date')
                merged_df[ApiConst.DATE.value] = merged_df[ApiConst.DATE.value].dt.strftime('%Y-%m-%d')
                merged_df = FeatureFunc.round_data(
                    merged_df, [ApiConst.CHARGE.value, ApiConst.DISCHARGE.value, ApiConst.REVENUE.value], decimal=2)
                merged_df = merged_df.replace({np.nan: None})

                pd_rnt_data = pd_rnt_data.replace({np.nan: None})
                pd_rnt_data[ApiConst.DATE.value] = pd_rnt_data[ApiConst.DATE.value].astype(str)
                pd_rnt_data[ApiConst.DURATION.value] = pd_rnt_data[ApiConst.DURATION.value].astype(str)
                pd_rnt_data = FeatureFunc.round_data(pd_rnt_data, [ApiConst.TOTAL_AMOUNT.value, ApiConst.DEGREE.value])

                rtn_dict = dict()
                rtn_dict[ApiConst.RAW_DATA.value] = pd_rnt_data.to_dict('records')
                rtn_dict[ApiConst.PLOT_DATA.value] = merged_df.to_dict(orient='list')
                pd_res = [rtn_dict]
            else:
                pd_res = [{
                    ApiConst.PLOT_DATA.value: {
                            ApiConst.DATE.value: [],
                            ApiConst.CHARGE.value: [],
                            ApiConst.DISCHARGE.value: [],
                            ApiConst.REVENUE.value: []
                        },
                    ApiConst.RAW_DATA.value: [
                        {
                            ApiConst.DATE.value: None, ApiConst.TOTAL_AMOUNT.value: None, ApiConst.ACTION.value: None,
                            ApiConst.DURATION.value: None, ApiConst.DEGREE.value: None
                        }
                    ]
                }]
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None