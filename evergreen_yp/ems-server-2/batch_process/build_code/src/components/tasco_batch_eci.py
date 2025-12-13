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
from src.utility.eci_helper import ECI, ESSECI


class TascoBatchECI(AbstractJob):
    """
    ESSCI + ECI 計算
    資料表: essci
    每分鐘一次
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
            warning_list = list()

            # 初始化資料
            rack_vol_count = 64
            rack_temp_count = 16
            eci_threshold = 0.1
            eci_warning_std = 0.8

            warning_threshold: pd.DataFrame = self.destination_dao.get_eci_settings()
            if not warning_threshold.empty:
                eci_threshold = warning_threshold[warning_threshold['key'] == 'eci_threshold']['value'].iloc[0]
                eci_warning_std = warning_threshold[warning_threshold['key'] == 'eci_warning_std']['value'].iloc[0]

            self.initial_data()
            self.logger.info(f'{self.start_date} - BatchECITasco - job_execute')

            self.start_date = self.start_date + timedelta(minutes=-1)
            self.end_date = self.start_date
            t_start = datetime.combine(self.start_date, time(self.start_date.hour, self.start_date.minute, 0))
            t_end = datetime.combine(self.start_date, time(self.start_date.hour, self.start_date.minute, 59))

            # 商業邏輯開始
            settings = FilesystemSettings(
                target_name_list=['bmu_*'], target_data=FolderType.History, base_path=self.source_dao.config['uri'],
                filter_date_star=datetime.combine(self.start_date, time(self.start_date.hour, 0, 0)),
                filter_date_end=datetime.combine(self.start_date, time(self.start_date.hour, 0, 0)))
            df = self.source_dao.read(criteria=settings)
            if not df.empty:
                df = df.replace({'None': None, 'nan': None, np.NAN: None})

                # 過濾時間
                df = df[(df['data_time'] >= str(t_start)) & (df['data_time'] <= str(t_end))]

                data = df.to_dict('records')
                rack_list = list()
                rack_volt_list = list()
                rack_temp_list = list()
                if len(data) > 0:
                    for d in data:
                        racks = d['rack_list'].replace("\'[", "[") \
                            .replace("]\'", "]") \
                            .replace("\'", "\"") \
                            .replace("True", "true").replace("False", "false")

                        replace = True
                        while replace:
                            s_idx = racks.find("datetime.datetime(")
                            if s_idx == -1:
                                replace = False
                            else:
                                e_idx = racks.find(')', s_idx)
                                target_replace = racks[s_idx: e_idx + 1]
                                replace_to = eval(target_replace.replace('datetime.', ''))
                                racks = racks.replace(target_replace, f'"{str(replace_to)}"')

                        racks = json.loads(racks)
                        for rack in racks:
                            rack_list.append(rack['equipment_id'])

                            volt_data = {
                                'time': d['data_time'],
                                'parent_id': rack['equipment_id']
                            }
                            temp_data = {
                                'time': d['data_time'],
                                'parent_id': rack['equipment_id']
                            }

                            vol_count = 0
                            temp_count = 0
                            for pack in rack['packs']:
                                for volt in pack['cell_volt']:
                                    volt_data[f'V{str(vol_count + 1).rjust(4, "0")}'] = volt
                                    vol_count = vol_count + 1

                                for temp in pack['cell_temp']:
                                    temp_data[f'T{str(temp_count + 1).rjust(4, "0")}'] = temp
                                    temp_count = temp_count + 1

                            rack_volt_list.append(volt_data)
                            rack_temp_list.append(temp_data)

                rack_volt = pd.DataFrame(rack_volt_list) if rack_volt_list else pd.DataFrame()
                rack_temp = pd.DataFrame(rack_temp_list) if rack_temp_list else pd.DataFrame()
                rack_list = list(set(rack_list))

                eci_list = list()
                eci_insert_list = list()
                for rack_id in rack_list:
                    pd_data = self.get_file_bms_ess_data(rack_temp, rack_volt, [rack_id], group_freq='1Min')
                    eci_object = ECI(pd_data, rack_id)
                    eci_object.get_eci(rack_vol_count, rack_temp_count, eci_threshold, rack_id)
                    eci_list.append(copy.deepcopy(eci_object))
                    eci_insert_list.append(eci_object.to_json())

                    rack_id = eci_object.eci_list[0]['rack_key']
                    eci_value = eci_object.eci_list[0]['value']
                    if eci_value < eci_warning_std:
                        warning_list.append(
                            f"[{str(t_start)}]{rack_id}: ECI低於設定標準, 目前數值{round(eci_value, 4)}")

                if eci_list:
                    esseci = ESSECI(eci_list)
                    esseci.get_esseci()
                    pd_res = {'ECI': esseci.eci_list, 'ICI': esseci.ici_list, 'RAW': esseci.raw_list}

                    #  insert into db
                    insert_data = {
                        'data_time': t_start,
                        'essci': pd_res,
                        'eci_list': eci_insert_list
                    }
                    self.destination_dao.upsert_essci({'data_time': t_start}, insert_data)

            if len(warning_list) > 0:
                self.alarm_controller.send_message(','.join(warning_list))

            # 每半小時移除4小時前資料
            if t_start.minute == 0 or t_start.minute == 30:
                remove_start_date = t_start + timedelta(hours=-4)
                query = {'data_time': {'$lt': remove_start_date}}
                self.destination_dao.delete_essci(query)

            # 商業邏輯結束
        except Exception as e:
            self.batch_result.success = False
            self.batch_result.msg = str(e)
            self.logger.error(str(e))

            # 失敗發Alarm
            self.send_alarm(str(e))

        # # 結束紀錄Log
        # self.insert_log(self.batch_result)

    def get_file_bms_ess_data(self, rack_temp_df, rack_volt_df, parent_id_list=[], group_freq='10Min'):
        bms_temp_data = rack_temp_df
        bms_volt_data = rack_volt_df
        if len(parent_id_list) > 0 and not bms_temp_data.empty and not bms_volt_data.empty:
            bms_temp_data = rack_temp_df.query("parent_id==@parent_id_list")
            bms_volt_data = rack_volt_df.query("parent_id==@parent_id_list")
        else:
            bms_temp_data = pandas.DataFrame([])
            bms_volt_data = pandas.DataFrame([])

        if not bms_temp_data.empty and not bms_volt_data.empty:
            pd_data = bms_volt_data.merge(bms_temp_data, left_on=['time', 'parent_id'], right_on=['time', 'parent_id'])
            pd_data = pd_data.sort_values(by=['time'])
            del pd_data['parent_id']
            from pandas.core import resample
            pd_data = pd_data.set_index(pd.DatetimeIndex(pd_data['time']))
            pd_data = pd_data.groupby(resample.TimeGrouper(freq=group_freq)).aggregate(np.mean)
        else:
            pd_data = pandas.DataFrame([])
        return pd_data


