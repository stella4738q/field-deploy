# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import numpy as np
from flask import request, g, session
from bson import ObjectId
from datetime import timedelta, datetime
import calendar
import pandas as pd
from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc, BidCalculate, TRUE_LIST
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource
from .. import schemas

today = datetime.today().date()
today_date = today.strftime('%Y%m%d')


class BidSbspmChart(Resource):
    """
    首頁 SBSPM Chart
    """
    logger = Logger().create('Advanced-tek API - bid spsbm chart', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('[get]')
        pd_res = []
        try:
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            pd_system_equipment = self.dao.get_system_equipment(field_id=[field_id])
            case_ids = pd_system_equipment['case_id'].tolist() if not pd_system_equipment.empty else []
            case_id_list = [case_id for case_id in case_ids if case_id is not None and case_id != 'None']

            pd_cases_info = self.dao.get_cases_info_many(case_id_list=case_id_list, date_list=[today_date])
            pd_case = self.dao.get_cases_many(_id_list=case_id_list)
            sdate, edate = FeatureFunc.full_date(today_date)
            pd_line_data = self.dao.get_SBSPM_local(sdate=sdate, edate=edate, field_id=field_id)

            if not pd_line_data.empty:
                pd_line_data[ApiConst.TIME.value] = pd.to_datetime(pd_line_data[ApiConst.TIME.value])

                pd_line_data.set_index(ApiConst.TIME.value, inplace=True)
                pd_line_data = pd_line_data.sort_index()
                pd_line_data['second'] = pd_line_data.index.second
                pd_line_data['minute'] = pd_line_data.index.minute

                for case_id in case_id_list:
                    case_code = list(pd_case[pd_case[ApiConst.ID_.value] == case_id][ApiConst.CODE.value])[0]
                    _pd_line_data = pd_line_data[pd_line_data[ApiConst.CASE_ID.value] == case_id]
                    pd_line_data_group_by = _pd_line_data.groupby(pd.Grouper(freq='1H'))

                    window_size = timedelta(seconds=4)
                    step_size = timedelta(seconds=1)

                    time_list = list()
                    sbspm_list = list()
                    quote_capacity_list = list()
                    close_capacity_list = list()

                    for _time, line_data_hour in pd_line_data_group_by:
                        time = _time.strftime("%H")

                        result_hour = []  # 儲存每小時每分鐘窗口內的最大值
                        data_time = line_data_hour.index
                        start_time = data_time[0].replace(microsecond=0)
                        end_time = data_time[-1] + timedelta(seconds=0.1)
                        current_time = start_time

                        while current_time + window_size <= end_time:
                            current_end_time = current_time + window_size
                            filtered_data = line_data_hour[(current_time <= line_data_hour.index) & (line_data_hour.index < current_end_time)]
                            max_sbspm = max(filtered_data['sbspm'])
                            result_hour.append(max_sbspm)
                            current_time += step_size  # 移動窗口每次1秒

                        min_max_value = min(result_hour)

                        # case info
                        quote_capacity = ''
                        close_capacity = ''
                        if not pd_cases_info.empty:
                            _pd_cases_info = pd_cases_info[
                                (pd_cases_info[ApiConst.TIME.value] == str(time)) & (pd_cases_info[ApiConst.CASE_ID.value] == case_id)]
                            _pd_cases_info = _pd_cases_info.replace({np.nan: None})
                            quote_data = _pd_cases_info[_pd_cases_info[ApiConst.STATUS.value] == ApiConst.QUOTE.value]
                            close_data = _pd_cases_info[_pd_cases_info[ApiConst.STATUS.value] == ApiConst.CLOSE.value]
                            quote_capacity = FeatureFunc.none_value(quote_data, ApiConst.CAPACITY.value)
                            close_capacity = FeatureFunc.none_value(close_data, ApiConst.CAPACITY.value)

                        time_list.append(time)
                        sbspm_list.append(round(min_max_value, 4))
                        quote_capacity_list.append(quote_capacity)
                        close_capacity_list.append(close_capacity)

                    pd_res.append({
                        'case_code': case_code, 'case_id': case_id, 'time': time_list, 'sbspm': sbspm_list,
                        'quote_capacity': quote_capacity_list, 'close_capacity': quote_capacity_list}
                    )

            else:
                for case_id in case_id_list:
                    case_code = list(pd_case[pd_case[ApiConst.ID_.value] == case_id][ApiConst.CODE.value])[0]
                    pd_res.append({
                        'case_code': case_code, 'case_id': case_id, 'time': list(range(0, 24)), 'sbspm': [],
                        'quote_capacity': [], 'close_capacity': []}
                    )

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
