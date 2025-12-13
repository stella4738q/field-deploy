import logging
import os
from datetime import datetime, timedelta
from enum import Enum

from src.components.abstract_job import AbstractJob
from src.components.batch_result import BatchResult
from src.dao.file_system_dao import FolderType, FilesystemSettings
from src.func_lib.system_status import SystemStatus, working_status_check


class TascoStatusControl(AbstractJob):
    """
    操作狀態FLAG控制:
    -1: NOT-AVAILABLE (PCS、BMS、LC狀態非正常)
     0: FREE 可隨時下功率操作
     1: MANUAL 手動充放模式
     2: CONTRACT_MODE 契約模式
     3: SCHEDULE: 手動排程充放模式
     4: AUTO: 自動排成充電
    每 5 秒檢查一次
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
        self.batch_result = BatchResult(datetime.now(), self.__class__.__name__, "StatusControl")

    def execute(self):
        try:
            self.initial_data()

            # 商業邏輯開始
            # LC狀態抓取
            settings = FilesystemSettings(
                target_name_list=['lc_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
            df = self.source_dao.read(criteria=settings)
            if df.empty:
                # 找不到資料當作沒在運行
                self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                return
            else:
                lc_data = df.iloc[0]
                if not working_status_check(lc_data['system_working_status']):
                    # 非運行狀態當不可執行
                    self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                    return

            # PCS狀態抓取
            settings = FilesystemSettings(
                target_name_list=['pcs_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
            df = self.source_dao.read(criteria=settings)
            if df.empty:
                # 找不到資料當作沒在運行
                self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                return
            else:
                pcs_data = df.iloc[0]
                if not working_status_check(pcs_data['working_status']):
                    # 非運行狀態當不可執行
                    self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                    return

            # BMS狀態抓取
            settings = FilesystemSettings(
                target_name_list=['bmu_*'], target_data=FolderType.Current, base_path=self.source_dao.config['uri'])
            df = self.source_dao.read(criteria=settings)
            if df.empty:
                # 找不到資料當作沒在運行
                self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                return
            else:
                bms_data = df.iloc[0]
                if not working_status_check(bms_data['working_status']):
                    # 非運行狀態當不可執行
                    self.destination_dao.upsert_working_status(status=SystemStatus.NOT_AVAILABLE.value, force=True)
                    return

            # 狀態還原:::::
            current_status = self.destination_dao.get_working_status()

            # 手動狀態控制檢查
            if current_status['system_status'] == SystemStatus.MANUAL.value:
                mod_data_time: datetime = current_status['update_time']
                # 手動充放電下, 若閒置超過N秒，自動切換回Free模式
                if (datetime.now() - mod_data_time).total_seconds() >= 10:
                    if pcs_data['active_power'] == 0:
                        self.destination_dao.upsert_working_status(status=SystemStatus.FREE.value, force=True)
                return

            # 契約容量模式檢查
            elif current_status['system_status'] == SystemStatus.CONTRACT_MODE.value:
                mod_data_time: datetime = current_status['update_time']
                # 契約容量下, 若閒置超過N秒，自動切換回Free模式
                if (datetime.now() - mod_data_time).total_seconds() >= 10:
                    if pcs_data['active_power'] == 0:
                        self.destination_dao.upsert_working_status(status=SystemStatus.FREE.value, force=True)
                return

            # 排程
            elif current_status['system_status'] == SystemStatus.SCHEDULE.value:
                mod_data_time: datetime = current_status['update_time']
                # 排程模式下, 若閒置超過N秒，自動切換回Free模式
                if (datetime.now() - mod_data_time).total_seconds() >= 10:
                    if pcs_data['active_power'] == 0:
                        self.destination_dao.upsert_working_status(status=SystemStatus.FREE.value, force=True)
                return

            # 自動充電
            elif current_status['system_status'] == SystemStatus.AUTO.value:
                mod_data_time: datetime = current_status['update_time']
                # 自動充電模式下, 若閒置超過N秒，自動切換回Free模式
                if (datetime.now() - mod_data_time).total_seconds() >= 10:
                    if pcs_data['active_power'] == 0:
                        self.destination_dao.upsert_working_status(status=SystemStatus.FREE.value, force=True)
                return

            # 什麼模式都不是，直接進入FREE
            self.destination_dao.upsert_working_status(status=SystemStatus.FREE.value, force=True)

            # 商業邏輯結束
        except Exception as e:
            self.batch_result.success = False
            self.batch_result.msg = str(e)
            self.logger.error(str(e))

            # 失敗發Alarm
            self.send_alarm(str(e))

        # # 結束紀錄Log
        # self.insert_log(self.batch_result)
