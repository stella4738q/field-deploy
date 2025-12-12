# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import numpy as np
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


def get_settings(settings, key):
    df = settings[settings['key'] == key]
    if df.empty:
        return None
    return df.iloc[0]['value']


def get_week_dates(target_date, start_day=0):
    # 星期一是0，星期天是6
    current_weekday = target_date.weekday()
    if start_day <= current_weekday:
        start_of_week = target_date - timedelta(days=current_weekday - start_day)
    else:
        start_of_week = target_date - timedelta(days=current_weekday - start_day + 7)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    return week_dates


class PowerControlSchedule(Resource):
    """
        利用設定檔中
        抑低用電 相關參數產出資料
        """
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] power control schedule')
        pd_res = []
        try:
            # 先取得設定檔案
            setting = self.dao.get_system_setting()
            keep_going = get_settings(setting, "automatic_power_control")
            if keep_going:
                start_dt = None
                end_dt = None

                # 抓取當週抑低用電排成
                start_date = get_settings(setting, "power_control_start_date")
                if start_date:
                    start_dt = datetime.strptime(f'{start_date}000000', '%Y%m%d%H%M%S')

                end_date = get_settings(setting, "power_control_end_date")
                if end_date:
                    end_dt = datetime.strptime(f'{end_date}235959', '%Y%m%d%H%M%S')

                # 取得台電假日日期
                all_holiday = list()

                # 今年 & 去年
                last_year = self.dao.get_taipower_holidays(datetime.today().year-1)
                if not last_year.empty:
                    all_holiday.extend(last_year.iloc[0]['holidays'])

                this_year = self.dao.get_taipower_holidays(datetime.today().year)
                if not this_year.empty:
                    all_holiday.extend(this_year.iloc[0]['holidays'])

                # 抓取抑低明細(抑制目標值)
                detail = self.dao.get_power_control_settings()
                settings = None
                if not detail.empty:
                    settings = [{
                        "start_time": item['start_time'],
                        "end_time": item['end_time'],
                        "kw": item['kw']
                    } for item in detail.to_dict('records')]

                # 抓取本週日期
                this_week = get_week_dates(datetime.today())
                for date in this_week:
                    str_date = datetime.strftime(date, '%Y-%m-%d')
                    if str_date in all_holiday:
                        continue

                    if start_dt <= date <= end_dt:
                        for setting in settings:
                            if date.weekday() + 1 not in [6, 7]:
                                pd_res.append({
                                    "week": date.weekday() + 1,
                                    "start_time": setting['start_time'],
                                    "end_time": setting['end_time'],
                                    "type": 3,
                                    "soc": setting['kw']
                                })
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
