import json

import copy
import logging
import os
import pandas
import pandas as pd
from datetime import datetime, timedelta, time

import numpy as np
from pyModbusTCP.client import ModbusClient

from src.components.abstract_job import AbstractJob
from src.components.batch_result import BatchResult
from src.dao.file_system_dao import FolderType, FilesystemSettings
from src.func_lib.lc_control import lc_set_power
from src.func_lib.system_settings import get_settings
from src.func_lib.system_status import SystemStatus
from src.utility.eci_helper import ECI, ESSECI


class TascoNeededControl(AbstractJob):
    """
    需量反映監測
    監控須量反應設定值:
    契約容量 -> 設定檔 contract_power
    到達 ? 時自動啟動 -> 設定檔 needed_power
    啟動時使用 ? 功率放電 -> 設定檔 -> auto_discharge_power
    持續到下次重置時間 (約每15分鐘)
    每30秒檢查一次有無觸發
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

            # 抓取目前狀態是否可執行
            # 狀態為 MANUAL 時直接返回，不可進行操作
            #
            status = self.destination_dao.get_working_status()
            status = status['system_status']
            if status == SystemStatus.MANUAL.value or status == SystemStatus.NOT_AVAILABLE.value:
                return

            # 抓取設定檔案
            #
            settings: pd.DataFrame = self.destination_dao.get_system_settings()
            enable_auto_discharge = get_settings(settings, 'enable_auto_discharge')  # 啟用契約抑制功能
            if not enable_auto_discharge:
                return

            # contract_power = get_settings(settings, 'contract_power')  # 契約容量
            # contract_power = float(contract_power)

            start_power = get_settings(settings, 'needed_power')  # 啟動容量
            start_power = float(start_power)

            auto_discharge_power = get_settings(settings, 'auto_discharge_power')  # 使用功率
            auto_discharge_power = float(auto_discharge_power)

            # 取得LC
            eq_df = self.destination_dao.get_control_equipment('LC')
            if eq_df.empty:
                return
            target = eq_df.iloc[0]

            ip = target['ip']
            port = target['port']
            unit_id = target['unit_id']
            lc_client = ModbusClient(host=ip, port=int(port), unit_id=int(unit_id), timeout=5)

            # TODO 接台合科資料
            #
            m_ip = "127.0.0.1"
            m_port = 502
            m_unit_id = 1
            m_address = 1024
            tasco_client = ModbusClient(host=m_ip, port=int(m_port), unit_id=int(m_unit_id), timeout=5)

            # 目前已使用容量
            #
            current_contract_power = tasco_client.read_holding_registers(m_address)
            current_contract_power = current_contract_power[0]

            # 商業邏輯開始
            if current_contract_power >= start_power:
                self.destination_dao.upsert_working_status(status=SystemStatus.CONTRACT_MODE.value)
                lc_set_power(lc_client, auto_discharge_power)
            else:
                filters = FilesystemSettings(
                    target_name_list=['lc_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
                df = self.source_dao.read(criteria=filters)
                if df.empty:
                    # 找不到資料當作沒在運行
                    return

                lc_data = df.iloc[0]

                status = self.destination_dao.get_working_status()
                status = status['system_status']
                if status == SystemStatus.CONTRACT_MODE.value:
                    if lc_data['active_power'] != 0:
                        lc_set_power(lc_client, 0)

            # 商業邏輯結束
        except Exception as e:
            self.batch_result.success = False
            self.batch_result.msg = str(e)
            self.logger.error(str(e))

            # 失敗發Alarm
            self.send_alarm(str(e))

        # # 結束紀錄Log
        # self.insert_log(self.batch_result)


