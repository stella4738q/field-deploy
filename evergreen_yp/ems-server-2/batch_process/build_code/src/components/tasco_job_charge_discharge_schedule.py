import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
from pyModbusTCP.client import ModbusClient

from src.components.abstract_job import AbstractJob
from src.components.batch_result import BatchResult
from src.dao.file_system_dao import FolderType, FilesystemSettings
from src.func_lib.lc_control import lc_set_power, power_cal
from src.func_lib.system_settings import get_settings
from src.func_lib.system_status import SystemStatus


class TascoChargeDischargeSchedule(AbstractJob):
    """
    充放電排程 + 離峰充電
    資料表: charge_schedule
    action_type:
       (1) FREE: 淨空狀態 -> 手動充放、契約模式、排程、自動離峰充電可執行
       (2) MANUAL: 手動充放模式 -> 手動充放中, 功率為 0 後持續 N 秒狀態轉為 FREE -> 契約模式、排程、自動離峰充電暫停，不可執行 (優先程度最高)
       (3) CONTRACT_MODE: 契約模式 -> 功率為 0 後持續 N 秒狀態轉為 FREE -> 排程、自動離峰充電暫停，不可執行 (優先程度次高)
       (3) SCHEDULE: 排程充放模式 -> 功率為 0 後持續 N 秒狀態轉為 FREE
       (4) AUTO: 自動離峰充電 -> 功率為 0 後持續 N 秒狀態轉為 FREE
       FREE 狀態由 StatusControl 控制，此批次僅降功率為 0
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
            self.start_date = datetime.now()
        else:
            self.start_date = self.input_start_date

        if self.input_end_date is None:
            self.end_date = datetime.now()
        else:
            self.end_date = self.input_end_date

    def __init_batch_result__(self):
        self.batch_result = BatchResult(datetime.now(), self.__class__.__name__, "BatchECITasco")

    def execute(self):
        try:
            self.initial_data()

            # 取得LC
            eq_df = self.destination_dao.get_control_equipment('LC')
            if eq_df.empty:
                return
            target = eq_df.iloc[0]

            ip = target['ip']
            port = target['port']
            unit_id = target['unit_id']

            client = ModbusClient(host=ip, port=int(port), unit_id=int(unit_id), timeout=5)

            # 取得總容量
            total_MWH = 2752
            eq_df = self.destination_dao.get_control_equipment('BMS')
            if not eq_df.empty:
                target = eq_df.iloc[0]
                total_MWH = float(target['capacity'])

            # 抓取目前狀態是否可執行
            # 狀態不為 FREE、SCHEDULE、AUTO 時直接返回，不可進行操作
            #
            status = self.destination_dao.get_working_status()
            status = status['system_status']
            if status != SystemStatus.FREE.value \
                    and status != SystemStatus.SCHEDULE.value \
                    and status != SystemStatus.AUTO.value:
                return

            # 抓取設定檔案
            #
            settings: pd.DataFrame = self.destination_dao.get_system_settings()
            charge_type = get_settings(settings, 'charge_type')  # 0: 手動排程, 1:離峰儲電
            charge_type = int(charge_type)

            # run_mod: -1 未設定, 0: 走排程, 1: 走自動充電
            run_mode = -1

            # 撈取是否有排程資料
            #
            now = datetime.now()
            current_timedelta = pd.to_timedelta(now.strftime('%H:%M:%S'))
            schedule_data: pd.DataFrame = self.destination_dao.get_charge_schedule(
                now.weekday() + 1, current_timedelta)
            if not schedule_data.empty:
                # 模式若為手動充放電排程，且有排程資料
                #
                if charge_type == 0:
                    run_mode = 0

                # 模式若為離峰儲電，且有排程資料 type: 0:充, 1:放
                #
                elif charge_type == 1:
                    # 判斷該時間點有無放電排程，有的話走放電排程 (充電排程忽略，因走自動充電)
                    discharge_task: pd.DataFrame = schedule_data.query("type == 1")
                    if discharge_task.empty:
                        run_mode = 1
                    # 沒有排程時，走自動充電
                    else:
                        run_mode = 0
            elif charge_type == 1:
                run_mode = 1

            # 依據 run_mode 進行相關動作
            #
            if run_mode == -1:
                return

            # 排程充/放電
            elif run_mode == 0:
                filters = FilesystemSettings(
                    target_name_list=['lc_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
                df = self.source_dao.read(criteria=filters)
                if df.empty:
                    # 找不到資料當作沒在運行
                    return

                # 抓目前SOC
                lc_data = df.iloc[0]
                current_soc = lc_data['system_soc']
                current_soc = float(current_soc)

                s_time = current_timedelta
                e_time = schedule_data.iloc[0]['end_time']
                # 目標放到SOC
                target_soc = schedule_data.iloc[0]['soc']

                # 可充放電總小時計算
                diff_time = (e_time - s_time).components
                total_hour = diff_time.hours + diff_time.minutes / 60

                c_type = schedule_data.iloc[0]['type']
                c_type = int(c_type)
                # 排程充電
                if c_type == 0:
                    max_soc = get_settings(settings, 'soc')
                    if max_soc is None:
                        max_soc = 90
                    max_soc = float(max_soc)
                    if target_soc > max_soc:
                        target_soc = max_soc

                    if current_soc >= target_soc or total_hour <= 0.05:
                        # 最後3分鐘就不充了
                        if status == SystemStatus.SCHEDULE.value:
                            if lc_data['active_power'] != 0:
                                lc_set_power(client, 0)
                    else:
                        power = power_cal(current_soc, target_soc, total_hour, total_MWH)
                        if abs(power) <= 600:
                            power = -600
                        elif abs(power) > 1375:
                            power = -1375
                        lc_set_power(client, power)
                        self.destination_dao.upsert_working_status(status=SystemStatus.SCHEDULE.value)

                # 排程放電
                elif c_type == 1:
                    emergency_power = get_settings(settings, 'emergency_power')
                    if emergency_power is None:
                        emergency_power = 0
                    emergency_power = float(emergency_power)
                    emergency_soc = round(emergency_power/total_MWH * 100, 0)

                    min_soc = get_settings(settings, 'protect_power')
                    if min_soc is None:
                        min_soc = 10
                    min_soc = float(min_soc) + emergency_soc  # 保護SOC + 緊急供電 SOC
                    if target_soc < min_soc:
                        target_soc = min_soc

                    if current_soc <= target_soc or total_hour <= 0.05:
                        # 最後3分鐘就不放了
                        if status == SystemStatus.SCHEDULE.value:
                            if lc_data['active_power'] != 0:
                                lc_set_power(client, 0)
                    else:
                        power = power_cal(current_soc, target_soc, total_hour, total_MWH)
                        lc_set_power(client, power)
                        self.destination_dao.upsert_working_status(status=SystemStatus.SCHEDULE.value)

            # 自動充電
            elif run_mode == 1:
                # 判斷是否為夏日時間
                is_summer = 0
                sum_start = get_settings(settings, 'summer_time_start')
                if sum_start is None:
                    sum_start = 601

                sum_end = get_settings(settings, 'summer_time_end')
                if sum_end is None:
                    sum_end = 831

                current = now.strftime('%m%d')
                if int(sum_start) <= int(current) <= int(sum_end):
                    is_summer = 1

                # 撈取設定檔
                price_list = self.destination_dao.get_electric_price(is_summer, 0)  # 0=離峰, 1:半尖峰, 2:尖峰
                price_list['end_time'] = price_list['end_time'].replace('24:00', '23:59')

                pattern = (now.weekday() + 1)
                price_list['start_time'] = pd.to_timedelta(price_list['start_time'] + ":00")
                price_list['end_time'] = pd.to_timedelta(price_list['end_time'] + ":00")

                start_df: pd.DataFrame = price_list.query(
                    f"week.str.contains('.*{pattern}.*', regex=True) and "
                    f"start_time <= @current_timedelta <= end_time")

                # 先撈取目前時間是否在離峰時段
                if start_df.empty:
                    # 非離峰時段返回
                    return

                s_time = current_timedelta
                e_time = start_df.iloc[0]['end_time']

                # 若結束時間為23:59, 判斷是否接續後一天的時間
                if e_time.components.hours == 23 and e_time.components.minutes == 59:
                    e_time = pd.to_timedelta("00:00:00")
                    pattern = pattern + 1
                    end_df: pd.DataFrame = price_list.query(
                        f"week.str.contains('.*{pattern}.*', regex=True) and "
                        f"start_time == @e_time")

                    if not end_df.empty:
                        e_time = end_df.iloc[0]['end_time']

                # 可充電總小時計算
                diff_time = (e_time - s_time).components
                total_hour = diff_time.hours + diff_time.minutes / 60

                # 目標SOC
                target_soc = get_settings(settings, 'soc')
                if target_soc is None:
                    target_soc = 90
                target_soc = float(target_soc)

                # 目前SOC
                filters = FilesystemSettings(
                    target_name_list=['lc_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
                df = self.source_dao.read(criteria=filters)
                if df.empty:
                    # 找不到資料當作沒在運行
                    return

                lc_data = df.iloc[0]
                current_soc = lc_data['system_soc']
                current_soc = float(current_soc)
                if current_soc >= target_soc or total_hour <= 0.05:
                    # 最後3分鐘就不充了
                    status = self.destination_dao.get_working_status()
                    status = status['system_status']
                    if status == SystemStatus.AUTO.value:
                        if lc_data['active_power'] != 0:
                            lc_set_power(client, 0)
                else:
                    power = power_cal(current_soc, target_soc, total_hour, total_MWH)
                    if abs(power) <= 600:
                        power = -600
                    elif abs(power) > 1375:
                        power = -1375
                    lc_set_power(client, power)
                    self.destination_dao.upsert_working_status(status=SystemStatus.AUTO.value)

            # 商業邏輯結束
        except Exception as e:
            self.batch_result.success = False
            self.batch_result.msg = str(e)
            self.logger.error(str(e))

            # 失敗發Alarm
            self.send_alarm(str(e))

        # # 結束紀錄Log
        # self.insert_log(self.batch_result)


