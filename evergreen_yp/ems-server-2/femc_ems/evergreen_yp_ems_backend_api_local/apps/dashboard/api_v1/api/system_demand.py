from __future__ import absolute_import, print_function

from datetime import datetime

import pandas as pd

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.sr_helper import SRProcess
from utility.token_module import token_required
from . import Resource


def get_settings(settings, key):
    df = settings[settings['key'] == key]
    if df.empty:
        return None
    return df.iloc[0]['value']


def check_is_summer(summer_start, summer_end, current_date: datetime = None):
    if current_date is None:
        current_date = datetime.now()
    current = current_date.strftime('%m%d')
    if int(summer_start) <= int(current) <= int(summer_end):
        return True
    return False


def check_can_add_kw(is_summer, ele_price, current_date: datetime = None):
    """
    夏月非夏月都可用:
        周六半尖峰可否使用判斷
        週六的離峰、半尖峰可用
        其他日(含星期天的離峰可用)
    """

    if not ele_price:
        print('ele_price 找不到相關設定')
        return False

    target_ele = next((item for item in ele_price['data'] if item['is_set'] == 1), None)
    if not target_ele:
        print('target_ele 找不到相關設定')
        return False

    price_data = target_ele['data']
    summer_type = '夏月' if is_summer else '非夏月'

    now = current_date if current_date is not None else datetime.now()
    current_timedelta = pd.to_timedelta(now.strftime('%H:%M:%S'))  # noqa
    pattern = (now.weekday() + 1)
    if pattern == 7:
        pass
    elif pattern == 6:
        # 星期六:離峰+半尖峰
        price_data = [price for price in price_data if price['price_level'] in ['離峰', '半尖峰'] and
                      price['summer_type'] == summer_type and (price['day_start'] <= pattern <= price['day_end'])]
        price_list = pd.DataFrame(price_data)
        price_list['time_end'] = price_list['time_end'].replace('24:00', '23:59')

        price_list['time_start'] = pd.to_timedelta(price_list['time_start'] + ":00")
        price_list['time_end'] = pd.to_timedelta(price_list['time_end'] + ":00")

        schedule_df: pd.DataFrame = price_list.query(f"time_start <= @current_timedelta < time_end")
        # 先撈取目前時間是否在尖峰時段
        if schedule_df.empty:
            return False
    else:
        # 其他只能使用在離峰
        price_data = [price for price in price_data if price['price_level'] in ['離峰'] and
                      price['summer_type'] == summer_type and (price['day_start'] <= pattern <= price['day_end'])]
        price_list = pd.DataFrame(price_data)
        price_list['time_end'] = price_list['time_end'].replace('24:00', '23:59')

        price_list['time_start'] = pd.to_timedelta(price_list['time_start'] + ":00")
        price_list['time_end'] = pd.to_timedelta(price_list['time_end'] + ":00")

        schedule_df: pd.DataFrame = price_list.query(f"time_start <= @current_timedelta < time_end")
        # 先撈取目前時間是否在離峰時段
        if schedule_df.empty:
            return False
    return True


class SystemDemand(Resource):
    """
    2024.11.28 新增 charge_type
    """
    logger = Logger().create('Evergreen API - SystemDemand', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        self.logger.info('get demand power')
        sr_status = 0
        power_demand = 0
        charge_type_desc = ''

        try:
            settings = self.dao.get_system_setting()
            charge_type = get_settings(settings, 'charge_type')  # 充電模式-0:手動排程，1:自動離峰儲電
            charge_type_desc = '手動排程' if int(charge_type) == 0 else '自動離峰儲電'

            ele_price = self.dao.get_electricity_settings()
            summer_time_start = str(ele_price['summer_date_start']).replace('-', '')
            summer_time_end = str(ele_price['summer_date_end']).replace('-', '')
            is_summer = check_is_summer(summer_time_start, summer_time_end)  # 是否為夏季時間
            if is_summer:
                contract_capacity = get_settings(settings, 'contract_capacity')  # 契約容量(MW)
                power_demand = contract_capacity * 1000  # 轉kW
            else:
                contract_capacity = get_settings(settings, 'nonsummer_contract_capacity')  # 非夏月契約容量(MW)
                power_demand = contract_capacity * 1000  # 轉kW

            # 判斷今日是否為台電離峰日
            is_holiday = self.dao.check_today_is_taipower_holiday(datetime.today())
            can_add_kw = check_can_add_kw(is_summer, ele_price) if not is_holiday else True  # 台電離峰日一律可使用
            if can_add_kw:
                saturday_contract_capacity = get_settings(settings, 'saturday_contract_capacity')  # 週六半尖峰
                power_demand = power_demand + saturday_contract_capacity

            sr = SRProcess(self.dao)
            if sr.case_list:
                sr_status = sr.case_list[0]['status']

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {
            'message': message,
            'data': power_demand,
            'charge_type': charge_type_desc,
            'sr_status': sr_status}, 200, None
