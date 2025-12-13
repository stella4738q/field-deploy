import json

import copy
import logging
import os
import pandas
import pandas as pd
from datetime import datetime, timedelta, time

import numpy as np

from src.components.abstract_job import AbstractJob
from src.components.batch_result import BatchResult
from src.dao.file_system_dao import FolderType, FilesystemSettings
from src.func_lib.system_settings import get_settings
from src.utility.eci_helper import ECI, ESSECI


class TascoBatchChargeReport(AbstractJob):
    """
    充放電報表計算
    每天凌晨12:30計算前一日
    """
    def initial_data(self):
        self.__init_start_end_date__()
        self.__init_log__()
        self.__init_batch_result__()

    def __init_log__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.logging_level)

        utc_now = datetime.utcnow()
        local_now = (utc_now + timedelta(hours=8))
        base_path = f'{self.log_base_path}/{local_now.year}/{local_now.month}/{local_now.day}/{local_now.hour}'
        current_path = f'{base_path}/{self.__class__.__name__}.log'
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        fh = logging.FileHandler(current_path)
        fh.setLevel(self.logging_level)
        self.logger.addHandler(fh)

    def __init_start_end_date__(self):
        # Time Init
        if self.input_start_date is None:
            self.start_date = datetime.combine(datetime.now() + timedelta(days=-1), time(0))
        else:
            self.start_date = self.input_start_date

        if self.input_end_date is None:
            self.end_date = datetime.combine(datetime.now() + timedelta(days=-1), time(23))
        else:
            self.end_date = self.input_end_date

    def __init_batch_result__(self):
        self.batch_result = BatchResult(datetime.now(), self.__class__.__name__, "BatchECITasco")

    def execute(self):
        try:
            self.initial_data()

            # 商業邏輯開始
            filters = FilesystemSettings(
                target_name_list=['lc_*'], target_data=FolderType.History, base_path=self.source_dao.config['uri'],
                filter_date_star=self.start_date,
                filter_date_end=self.end_date)
            df = self.source_dao.read(criteria=filters)
            if not df.empty:
                # # 抓取總容量
                # total_MWH = 2752
                # eq_df = self.destination_dao.get_control_equipment('BMS')
                # if not eq_df.empty:
                #     target = eq_df.iloc[0]
                #     total_MWH = float(target['capacity'])

                # 判斷是否為夏日時間
                settings: pd.DataFrame = self.destination_dao.get_system_settings()
                is_summer = 0
                sum_start = get_settings(settings, 'summer_time_start')
                if sum_start is None:
                    sum_start = 601

                sum_end = get_settings(settings, 'summer_time_end')
                if sum_end is None:
                    sum_end = 831

                current = self.start_date.strftime('%m%d')
                if int(sum_start) <= int(current) <= int(sum_end):
                    is_summer = 1

                # 撈取設定檔
                week_day = self.start_date.weekday()+1
                price_list = self.destination_dao.get_electric_price(is_summer, None)  # 0=離峰, 1:半尖峰, 2:尖峰
                price_list['start_time'] = pd.to_timedelta(price_list['start_time'] + ":00")
                price_list['end_time'] = pd.to_timedelta(price_list['end_time'] + ":00")
                price_list: pd.DataFrame = price_list.query(f"week.str.contains('.*{week_day}.*', regex=True)")

                # 資料排序
                df = df.replace({'None': None, 'nan': None, np.NAN: None})
                df['data_time'] = pd.to_datetime(df['data_time'])
                df.sort_values(by='data_time', inplace=True)

                # 過濾欄位+型態轉換
                df = df[['data_time', 'system_soc', 'active_power']]
                df['system_soc'] = pd.to_numeric(df['system_soc'], errors='coerce')
                df['active_power'] = pd.to_numeric(df['active_power'], errors='coerce')
                df = df[df['active_power'] != 0]

                # 新增action欄位
                df['action'] = df['active_power'].apply(lambda x: 'discharge' if x > 0 else 'charge')

                # 處理price欄位
                df_price = list()
                df: pd.DataFrame = df.dropna(subset=['system_soc', 'active_power'])
                for idx, row in df.iterrows():
                    current_timedelta = pd.to_timedelta(row['data_time'].strftime('%H:%M:%S'))
                    temp_df: pd.DataFrame = price_list.query("start_time <= @current_timedelta <= end_time")
                    price = 0
                    if not temp_df.empty:
                        price = temp_df.iloc[0]['price']
                    df_price.append(price)
                df['price'] = df_price
                df['degree'] = df['active_power'].apply(lambda x: x/3600)  # 功率/3600 = 每秒度數

                upser_list = list()
                # 進行時間分組
                df['group'] = (df['action'] != df['action'].shift()).cumsum()
                grouped_df = df.groupby(['group', 'action', 'price'])
                for (group, action, price), group_data in grouped_df:
                    start_date = group_data.iloc[0]['data_time']
                    end_date = group_data.iloc[-1]['data_time']
                    soc = abs(group_data.iloc[0]['system_soc'] - group_data.iloc[-1]['system_soc'])
                    degree = abs(group_data['degree'].sum())  # round(soc/100 * total_MWH, 2)
                    unit_price = price
                    total_price = degree * unit_price

                    upser_list.append({
                        'start_date': start_date,
                        'end_date': end_date,
                        'action': action,
                        'soc': round(soc, 8),
                        'degree': round(degree, 8),
                        'unit_price': unit_price,
                        'total_price': round(total_price, 8)
                    })

                if len(upser_list) > 0:
                    self.destination_dao.upsert_electric_report(upser_list)

            # 商業邏輯結束
        except Exception as e:
            self.batch_result.success = False
            self.batch_result.msg = str(e)
            self.logger.error(str(e))

            # 失敗發Alarm
            self.send_alarm(str(e))

        # # 結束紀錄Log
        # self.insert_log(self.batch_result)
