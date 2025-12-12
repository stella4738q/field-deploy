import copy
import glob
import json
import os
import random
import re
from datetime import date, datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
from bson import ObjectId

from src.constants.source_type_const import SourceTypeConfigConst
from src.dao.file_system_dao import FileSystemDao, FolderType, FilesystemSettings


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

def clean_datetime_string(s):
    replace = True
    while replace:
        s_idx = s.find("datetime.datetime(")
        if s_idx == -1:
            replace = False
        else:
            e_idx = s.find(')', s_idx)
            target_replace = s[s_idx: e_idx + 1]
            replace_to = eval(target_replace.replace('datetime.', ''))
            s = s.replace(target_replace, f'"{str(replace_to)}"')
    return s


def publish_socket_data(
        layout_format, use_meter_ms, mvcb_meter_base_path, mvcb_map_key,
        append_accu_data, meter_accu_dao, meter_accu_settings, source_list, use_sim_data, load_fixed_attr,
        db_dao, pri_data=None):
    # df: pd.DataFrame = pd.read_csv("C:/Users/User/Desktop/advanced-tek/storage/2024/7/20/16/bmu_BMU_1.csv")
    # if not df.empty:
    #     df = df.replace({'None': None, 'nan': None, np.NAN: None})
    #     data = df.to_dict('records')
    #     rack_data = list()
    #     if len(data) > 0:
    #         for d in data:
    #             if d['warning'] is not None and type(d['warning']) is str:
    #                 d['warning'] = json.loads(d['warning'])
    #
    #             if d['rack_list']:
    #                 racks = d['rack_list'].replace("\'[", "[") \
    #                     .replace("]\'", "]") \
    #                     .replace("\'", "\"") \
    #                     .replace("True", "true").replace("False", "false")
    #
    #                 replace = True
    #                 while replace:
    #                     s_idx = racks.find("datetime.datetime(")
    #                     if s_idx == -1:
    #                         replace = False
    #                     else:
    #                         e_idx = racks.find(')', s_idx)
    #                         target_replace = racks[s_idx: e_idx + 1]
    #                         replace_to = eval(target_replace.replace('datetime.', ''))
    #                         racks = racks.replace(target_replace, f'"{str(replace_to)}"')
    #                 del d['rack_list']
    #                 racks = racks.replace('None', 'null')
    #                 rack_list = json.loads(racks)
    #
    #                 for r in rack_list:
    #                     for p in r['packs']:
    #                         rack_data.append({
    #                             'data_time': d['data_time'],
    #                             'rack_no': r['rack_no'],
    #                             'pack_no': p['pack_no'],
    #                             'cell_volt': max(p['cell_volt']),
    #                             'cell_temp': max(p['cell_temp'])
    #                         })
    #
    #     pdd = pd.DataFrame(rack_data)
    #     pdd.to_csv("C:/Users/User/Desktop/advanced-tek/storage/2024/7/20/4/rack_data.csv", index=False)
    #
    # aa = 'a'

    femc_data = FEMCData()
    # 使用測試資料
    if use_sim_data:
        # publish_data = gen_temp_data()
        sim_data_path = "sim_data/socket_temp.json"
        with open(sim_data_path, 'r', encoding='utf-8') as file:
            publish_data = json.load(file)

        for key in publish_data:
            if key == 'other':
                continue

            datas = publish_data[key]
            # 改時間
            for data in datas:
                data['data_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # if key == 'pcs':
                #     data['active_power'] = data['active_power'] + round(data['active_power'] * round(random.uniform(0.001, -0.009), 3), 1)
                #     data['volt_rs'] = data['volt_rs'] + round(data['volt_rs'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['volt_st'] = data['volt_st'] + round(data['volt_st'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['volt_tr'] = data['volt_tr'] + round(data['volt_tr'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['volt_avg'] = data['volt_avg'] + round(data['volt_avg'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['current_r'] = data['current_r'] + round(data['current_r'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['current_s'] = data['current_s'] + round(data['current_s'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['current_t'] = data['current_t'] + round(data['current_t'] * round(random.uniform(0.009, -0.009), 3), 1)
                #     data['current_avg'] = data['current_avg'] + round(data['current_avg'] * round(random.uniform(0.009, -0.009), 3), 1)
    else:
        # 正式抓資料
        publish_data = copy.deepcopy(layout_format)
        if use_meter_ms:
            try:
                current_time = datetime.now()
                second = current_time.second
                folder = os.path.join(mvcb_meter_base_path, 'meter_ms')
                latest_meter_file = find_latest_meter_file(folder, f'meter_{second}')
                if latest_meter_file and os.path.exists(latest_meter_file):
                    df = pd.read_csv(latest_meter_file)
                    df = df.replace({'None': None, 'nan': None, np.NAN: None})
                    data = df.to_dict('records')
                    if len(data) > 0:
                        for d in data:
                            d['warning'] = json.loads(d['warning'])
                    publish_data[mvcb_map_key].extend(data)
            except Exception:
                if pri_data:
                    publish_data[mvcb_map_key] = pri_data[mvcb_map_key]

            if append_accu_data:
                try:
                    df: pd.DataFrame = meter_accu_dao.read(criteria=meter_accu_settings)
                    if not df.empty:
                        df = df.replace({'None': None, 'nan': None, np.NAN: None})
                        data = df.to_dict('records')[0]
                        publish_data[mvcb_map_key][0]['ac_energy_imp'] = data['ac_energy_imp']
                        publish_data[mvcb_map_key][0]['ac_energy_exp'] = data['ac_energy_exp']
                    else:
                        raise Exception
                except Exception:
                    if pri_data:
                        publish_data[mvcb_map_key][0]['ac_energy_imp'] = pri_data[mvcb_map_key][0]['ac_energy_imp']
                        publish_data[mvcb_map_key][0]['ac_energy_exp'] = pri_data[mvcb_map_key][0]['ac_energy_exp']

        for source in source_list:
            try:
                source_type = source.get('type')
                # 檔案型
                if source_type == SourceTypeConfigConst.FILE_SYSTEM.value:
                    settings = source.get('settings')
                    dao = source.get('dao')
                    map_key = source.get('map_key')

                    try:
                        df: pd.DataFrame = dao.read(criteria=settings)
                        if not df.empty:
                            df = df.replace({'None': None, 'nan': None, np.NAN: None})

                            if map_key == 'sbspm':
                                # 轉換Web需要的欄位
                                # pre_tcp_frequency,pre_tcp_frequency_center,tcp_frequency,tcp_frequency_center
                                data = df.to_dict('records')[-1:]
                                target_data = data[0]

                                if 'pre_tcp_frequency' in target_data:
                                    data[0]['pre_frequency'] = target_data['pre_tcp_frequency']

                                if 'pre_tcp_frequency_center' in target_data:
                                    data[0]['pre_frequency_center'] = target_data['pre_tcp_frequency_center']

                                if 'tcp_frequency' in target_data:
                                    data[0]['frequency'] = target_data['tcp_frequency']

                                if 'tcp_frequency_center' in target_data:
                                    data[0]['frequency_center'] = target_data['tcp_frequency_center']

                                if 'total_active_power' in target_data:
                                    data[0]['total_active_power'] = target_data['total_active_power'] * 1000
                            else:
                                data = df.to_dict('records')
                                if len(data) > 0:
                                    for d in data:
                                        # Warning處理
                                        if d['warning'] is not None and type(d['warning']) is str:
                                            d['warning'] = json.loads(d['warning'])

                                        # BMS 特別處理
                                        if 'rack_list' in d:
                                            if d['rack_list']:
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
                                                del d['rack_list']
                                                racks = racks.replace('None', 'null')
                                                d['rack'] = json.loads(racks)
                                            else:
                                                del d['rack_list']
                                                d['rack'] = list()

                                        # FEMC Status 特別處理
                                        if map_key == 'env_status':
                                            for key, value in d.items():
                                                if hasattr(femc_data, key.lower()) and not getattr(femc_data,
                                                                                                   key.lower()):
                                                    setattr(femc_data, key.lower(), value)
                                            if d['warning']:
                                                femc_data.warning.extend(d['warning'])

                                            # 不添加到 publish_data 中
                                            continue

                                        # DCU 特別處理
                                        if 'inverter_list' in d:
                                            if isinstance(d['inverter_list'], str) and d['inverter_list'].strip():
                                                try:
                                                    s = d['inverter_list']
                                                    s = s.replace("\'[", "[") \
                                                        .replace("]\'", "]") \
                                                        .replace("\'", "\"") \
                                                        .replace("True", "true") \
                                                        .replace("False", "false") \
                                                        .replace("None", "null")

                                                    s = clean_datetime_string(s)
                                                    d['inverter'] = json.loads(s)
                                                except Exception as e:
                                                    d['inverter'] = []
                                            else:
                                                d['inverter'] = []

                                            del d['inverter_list']
                                        if 'optimizer_list' in d:
                                            if isinstance(d['optimizer_list'], str) and d['optimizer_list'].strip():
                                                try:
                                                    s = d['optimizer_list']
                                                    s = s.replace("\'[", "[") \
                                                        .replace("]\'", "]") \
                                                        .replace("\'", "\"") \
                                                        .replace("True", "true") \
                                                        .replace("False", "false") \
                                                        .replace("None", "null") \
                                                        .replace("\\x00", "")
                                                    s = re.sub(r'\\?(NaN|nan)', 'null', s)

                                                    s = clean_datetime_string(s)
                                                    d['optimizer'] = json.loads(s)
                                                except Exception as e:
                                                    d['optimizer'] = []
                                            else:
                                                d['optimizer'] = []

                                            del d['optimizer_list']

                            publish_data[map_key].extend(data)
                    except Exception as e:
                        print(f"An error occurred while reading {map_key} data: {e}")
                # Web API型
                # ToDo: 補相關API邏輯，暫時沒用到
                elif source_type == SourceTypeConfigConst.WEB_API.value:
                    pass

            except KeyError as e:
                source.logger.exception(repr(e))
                # raise KeyError
            except Exception as e:
                source.logger.exception(repr(e))
                # raise Exception

    try:
        # 固定撈取 env_status / db: alarm、status、operation_mode
        if load_fixed_attr:
            # # env_status
            # publish_data['env_status'] = list()
            # if len(femc_data.warning) > 0:
            #     femc_data.abnormal = True
            # femc_data.data_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")
            # publish_data['env_status'].append(femc_data.__dict__)

            # alarm
            publish_data['alarm'] = list()
            client = db_dao.get_connect()
            db = client[db_dao.database_name]
            cursor = db.alarm.find({'done_time': None})
            alarm_data = pd.DataFrame(list(cursor))
            for data in alarm_data.to_dict(orient='records'):
                alarm = Alarm()
                alarm.time = datetime.strftime(data['time'], '%Y-%m-%d %H:%M:%S')
                alarm.field_id = data['field_id']
                alarm.equipment_id = data['equipment_id']
                alarm.equipment_type = parser_equipment_code(data['equipment_id'])
                alarm.level = data['level'] if data['level'] is not None else None
                alarm.code = data['code']
                alarm.message = data['message']
                publish_data['alarm'].append(alarm.to_json())

            # ems schedule(充放電排程、抑低排程)
            publish_data['ems_schedule'] = list()

            # 取得system setting
            cursor = db.system_settings.find()
            sys_setting_data = pd.DataFrame(list(cursor))

            # 充電模式, 0:手動排程，1:自動離峰儲電
            charge_type = sys_setting_data[sys_setting_data['key'] == 'charge_type']['value'].tolist()[0]
            if charge_type == 0:
                charge_id = sys_setting_data[sys_setting_data['key'] == 'charge_type_rundown']['value'].tolist()[0]

                # 取得充放電排程
                cursor = db.electric_schedule_detail.find({'parent_id': charge_id})
                schedule_detail_data = pd.DataFrame(list(cursor))

                if not schedule_detail_data.empty:
                    if schedule_detail_data['week'].dtype != object:
                        schedule_detail_data['week'] = schedule_detail_data['week'].astype(str)

                    # 離峰日排程
                    holiday_df = schedule_detail_data.loc[schedule_detail_data['week'] == '7']
                    today = datetime.today()
                    week_monday = today - timedelta(days=today.weekday())

                    # 找出本週內實際為台電假日的 weekday（1~7；週一=1）
                    holiday_weekdays = []
                    for d in range(7):
                        current_date = week_monday + timedelta(days=d)
                        cursor = db.taipower_holidays.find({'year': str(current_date.year)})
                        holiday_data = pd.DataFrame(list(cursor))
                        if not holiday_data.empty:
                            cd = datetime.strftime(current_date, '%Y-%m-%d')
                            holidays = holiday_data.iloc[0]['holidays']
                            if cd in holidays:
                                holiday_weekdays.append(str(current_date.weekday() + 1))

                    if holiday_weekdays and not holiday_df.empty:
                        # 移除原對應資料
                        schedule_detail_data = schedule_detail_data.loc[
                            ~schedule_detail_data['week'].isin(holiday_weekdays)
                        ]

                        duplicated = []
                        for w in holiday_weekdays:
                            # 只改 week 欄位，其餘欄位原樣
                            tmp = holiday_df.copy(deep=False)
                            tmp = tmp.assign(week=w)
                            duplicated.append(tmp)

                        if duplicated:
                            schedule_detail_data = pd.concat([schedule_detail_data] + duplicated, ignore_index=True)

                    schedule_detail_data = schedule_detail_data.replace({np.nan: None})
                    for data in schedule_detail_data.to_dict(orient='records'):
                        schedule = EmsSchedule()
                        schedule.week = data['week']
                        schedule.start_time = data['start_time']
                        schedule.end_time = data['end_time']
                        schedule.type = data['type']
                        schedule.soc = data['soc'] if not pd.isna(data['soc']) else None
                        schedule.kw = data.get('kw') if not pd.isna(data.get('kw', np.nan)) else None
                        publish_data['ems_schedule'].append(schedule.to_json())

            # 取得抑低排程
            enable_power_control = \
                sys_setting_data[sys_setting_data['key'] == 'automatic_power_control']['value'].tolist()[0]

            if enable_power_control:
                # 取得台電假日日期
                all_holiday = list()
                start_dt = sys_setting_data[sys_setting_data['key'] == 'power_control_start_date']['value'].tolist()[0]
                end_dt = sys_setting_data[sys_setting_data['key'] == 'power_control_end_date']['value'].tolist()[0]

                # 今年 & 去年
                cursor = db.taipower_holidays.find({"year": str(datetime.today().year - 1)})
                last_year = pd.DataFrame(list(cursor))
                if not last_year.empty:
                    all_holiday.extend(last_year.iloc[0]['holidays'])

                cursor = db.taipower_holidays.find({"year": str(datetime.today().year)})
                this_year = pd.DataFrame(list(cursor))
                if not this_year.empty:
                    all_holiday.extend(this_year.iloc[0]['holidays'])

                all_holiday = [x.replace('-', '') for x in all_holiday]
                settings = None
                cursor = db.power_control_settings.find()
                power_control_data = pd.DataFrame(list(cursor))
                if not power_control_data.empty:
                    settings = [{
                        "start_time": item['start_time'],
                        "end_time": item['end_time'],
                        "kw": item['kw']
                    } for item in power_control_data.to_dict('records')]

                this_week = get_week_dates(datetime.today())
                for _date in this_week:
                    str_date = datetime.strftime(_date, '%Y%m%d')
                    if str_date in all_holiday:
                        continue

                    if start_dt <= str_date <= end_dt:
                        for setting in settings:
                            if _date.weekday() + 1 not in [6, 7]:
                                control_schedule = EmsSchedule()
                                control_schedule.week = _date.weekday() + 1
                                control_schedule.start_time = setting['start_time']
                                control_schedule.end_time = setting['end_time']
                                control_schedule.type = 3
                                control_schedule.soc = setting.get('soc') if setting.get('soc') is not None else None
                                control_schedule.kw = setting.get('kw') if setting.get('kw') is not None else None
                                publish_data['ems_schedule'].append(control_schedule.to_json())

            publish_data['other'] = dict()

            # operation_mode
            operation_mode = db.operation_mode.find_one()
            mode = None if operation_mode is None else int(operation_mode['mode'])
            publish_data['other']['operation_mode'] = mode

            # working_status
            working_status = db.working_status.find_one()
            status = None if working_status is None else int(working_status['system_status'])
            publish_data['other']['ems_status'] = status

            # # For 測試
            # publish_data['pcs'][0]['active_power'] = 0
            # publish_data['bms'][0]['abnormal'] = True
            # publish_data['bms'][0]['rack'][0]['abnormal'] = True
            # publish_data['bms'][0]['rack'][1]['abnormal'] = True
            # publish_data['bms'][0]['rack'][2]['abnormal'] = True
            # publish_data['bms'][0]['rack'][3]['abnormal'] = True
            # publish_data['bms'][0]['rack'][4]['abnormal'] = True
            # publish_data['bms'][0]['rack'][5]['abnormal'] = True
            # publish_data['bms'][0]['rack'][6]['abnormal'] = True
            # publish_data['bms'][0]['rack'][7]['abnormal'] = True
            # publish_data['bms'][0]['rack'][8]['abnormal'] = True
    except Exception as e:
        print(e)

    return publish_data, json.dumps(publish_data)


class Alarm:
    def __init__(self):
        self.time = None
        self.field_id = None
        self.equipment_type = None
        self.equipment_id = None
        self.level = None
        self.code = None
        self.message = None
        self.abnormal = True

    def to_json(self):
        return {
            'time': str(self.time),
            'field_id': self.field_id,
            'equipment_type': self.equipment_type,
            'equipment_id': self.equipment_id,
            'level': self.level,
            'code': self.code,
            'message': self.message,
            'abnormal': self.abnormal
        }


class EmsSchedule:
    def __init__(self):
        self.week = None
        self.start_time = None
        self.end_time = None
        self.type = None
        self.soc = None
        self.kw = None

    def to_json(self):
        return {
            'week': str(self.week),
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'type': self.type,
            'soc': self.soc,
            'kw': self.kw
        }


def process_alarm(mongo_handler_list, alarm_data, target_eq_list):
    try:
        alarm_data = alarm_data.groupby(['equipment_id', 'message']).head(1) \
            if not alarm_data.empty else pd.DataFrame({})

        for mongo_dao in mongo_handler_list:
            client = mongo_dao.get_connect()
            db = client[mongo_dao.database_name]

            utc_now = datetime.utcnow()
            local_now = (utc_now + timedelta(hours=8))
            try:
                if alarm_data.empty:
                    # 目前沒有發生alarm, 更新相關設備alarm完成時間
                    db.alarm.update_many(
                        {'equipment_id': {"$in": target_eq_list},
                         'done_time': None},
                        {'$set': {'done_time': local_now}})
                else:
                    # 檢查alarm中不存在的alarm
                    exist_alarm = []
                    for idx, row in alarm_data.iterrows():
                        cursor = db.alarm.find_one(
                            {'done_time': None,
                             'equipment_id': row['equipment_id'],
                             'message': row['message']})
                        if cursor is None:
                            obj_id = ObjectId()
                            exist_alarm.append(obj_id)
                            db.alarm.insert_one({
                                '_id': obj_id,
                                'time': row['time'],
                                'done_time': None,
                                'field_id': row['field_id'],
                                'equipment_id': row['equipment_id'],
                                'title': row['title'],
                                'code': row['code'],
                                'level': row['level'] if row['level'] is not None else None,
                                'message': row['message']
                            })
                        else:
                            exist_alarm.append(cursor['_id'])
                    if len(exist_alarm) > 0:
                        db.alarm.update_many(
                            {'_id': {"$nin": exist_alarm}, 'equipment_id': {"$in": target_eq_list}, 'done_time': None},
                            {'$set': {'done_time': local_now}})
            except Exception as e:
                raise Exception
    except Exception as e:
        pass


def parser_equipment_code(equipment_id):
    rtn_code = 0
    if 'AIR' in equipment_id:
        rtn_code = 0
    elif 'FIRE' in equipment_id:
        rtn_code = 1
    elif 'DOOR' in equipment_id:
        rtn_code = 2
    elif 'RELAY' in equipment_id:
        rtn_code = 3
    elif 'PCS' in equipment_id:
        rtn_code = 4
    elif 'BMS' in equipment_id:
        rtn_code = 5
    elif 'RACK' in equipment_id:
        rtn_code = 6
    elif 'METER' in equipment_id:
        rtn_code = 7
    elif 'UPS' in equipment_id:
        rtn_code = 8
    elif 'ACB' in equipment_id:
        rtn_code = 9
    elif 'VCB' in equipment_id:
        rtn_code = 10
    elif 'LC' in equipment_id:
        rtn_code = 11
    return rtn_code


class WarningData:
    def __init__(self, level=0, code=None, name=None, time=None):
        self.level = level
        self.code = code
        self.name = name
        self.start_tme: datetime = time

    def encode(self):
        return {
            "level": self.level,
            "code": self.code,
            "name": self.name,
            "start_tme": str(self.start_tme)
        }


class FEMCData:
    def __init__(self):
        self.data_time = None
        self.field_id = None
        self.resource_id = None
        self.equipment_id = None
        self.parent_id = None
        # 通訊錯誤
        self.conn_abnormal_pcs = False
        self.conn_abnormal_bms = False
        # 過壓/欠壓
        self.over_voltage_bms_alarm = False
        self.over_voltage_bms_fault = False
        # 過流
        self.over_current_bms_alarm = False
        self.over_current_bms_fault = False
        # 過溫
        self.over_temperature_bms_alarm = False
        self.over_temperature_bms_fault = False
        # 絕緣/接地異常
        self.ground_fault = None
        # 消防/火災
        self.fire = False
        # 緊急控制
        self.emergency = False
        # 逆送電
        self.reverse_power = False

        self.abnormal = False
        self.warning: List[WarningData] = list()


def find_latest_meter_file(directory, prefix):
    if os.path.exists(directory):
        pattern = os.path.join(directory, f"{prefix}*")
        files = glob.glob(pattern)
        if not files:
            return find_latest_meter_file(directory, prefix)
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    return None


def gen_temp_data():
    now = datetime.now()
    now = now.replace(year=2024, month=9, day=19)
    e_now = now + timedelta(seconds=6)

    socket_data = {
        "pcs": [],
        "bms": [],
        "meter": [],
        "bms_air": [],
        "bms_fan": [],
        "io": [],
        "alarm": [],
        "env_status": [],
        "other": {
            "operation_mode": 0,
            "ems_status": 0
        }
    }
    meter_sun = {
        "data_time": datetime.strftime(now, '%Y-%m-%d %H:%M:%S.%f'),
        "field_id": "6633c0acc7a76aa6c045b96b",
        "case_id": "",
        "resource_id": "advanced-tek",
        "equipment_id": "METER_SUN",
        "parent_id": "",
        "frequency": 60,
        "voltage_ab": 0,
        "voltage_bc": 0,
        "voltage_ca": 0,
        "voltage_a": 0,
        "voltage_b": 0,
        "voltage_c": 0,
        "voltage_avg": 0,
        "line_voltage_avg": 0,
        "current_a": 0,
        "current_b": 0,
        "current_c": 0,
        "current_avg": 0,
        "in_current": 0,
        "pfa": 0,
        "pfb": 0,
        "pfc": 0,
        "total_power_factor": 0,
        "pa": 0,
        "pb": 0,
        "pc": 0,
        "total_active_power": 0,
        "qa": 0,
        "qb": 0,
        "qc": 0,
        "total_reactive_power": 0,
        "sa": 0,
        "sb": 0,
        "sc": 0,
        "total_apparent_power": 0,
        "ac_energy_imp": 0,
        "ac_energy_exp": 0,
        "total_energy_power": None,
        "total_energy_apparent": None,
        "warning": []
    }

    s_time = now.replace(hour=now.hour, minute=0, second=0, microsecond=0)
    e_time = e_now.replace(hour=e_now.hour, minute=0, second=0, microsecond=0)

    file_dao = FileSystemDao("/app/data")

    # PCS
    pcs_settings = FilesystemSettings(
        target_name_list=['pcs_*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    pcs_df = file_dao.read(criteria=pcs_settings)
    if not pcs_df.empty:
        pcs_df['data_time'] = pd.to_datetime(pcs_df['data_time'])
        condition = (pcs_df['data_time'] >= now) & (pcs_df['data_time'] < e_now)
        pcs_df = pcs_df[condition]
        pcs_df = pcs_df.sort_values(by='data_time', ascending=True)
        pcs_df = pcs_df.head(1)
        pcs_df = pcs_df.replace({'None': None, 'nan': None, np.NAN: None})
        pcs_df = pcs_df.astype({'data_time': str})
        data = pcs_df.to_dict('records')
        data = process_warn(data)
        socket_data['pcs'].extend(data)

    # BMS
    bms_settings = FilesystemSettings(
        target_name_list=['bmu_*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    bms_df = file_dao.read(criteria=bms_settings)
    if not bms_df.empty:
        bms_df['data_time'] = pd.to_datetime(bms_df['data_time'])
        condition = (bms_df['data_time'] >= now) & (bms_df['data_time'] < e_now)
        bms_df = bms_df[condition]
        bms_df = bms_df.sort_values(by='data_time', ascending=True)
        bms_df = bms_df.head(1)
        bms_df = bms_df.replace({'None': None, 'nan': None, np.NAN: None})
        bms_df = bms_df.astype({'data_time': str})
        data = bms_df.to_dict('records')
        data = process_warn(data)
        socket_data['bms'].extend(data)

    # meter MAIN
    meter_settings = FilesystemSettings(
        target_name_list=['meter_METER_MAIN*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    meter_df = file_dao.read(criteria=meter_settings)
    if not meter_df.empty:
        meter_df['data_time'] = pd.to_datetime(meter_df['data_time'])
        condition = (meter_df['data_time'] >= now) & (meter_df['data_time'] < e_now)
        meter_df = meter_df[condition]
        meter_df = meter_df.sort_values(by='data_time', ascending=True)
        meter_df = meter_df.head(1)
        meter_df = meter_df.replace({'None': None, 'nan': None, np.NAN: None})
        meter_df = meter_df.astype({'data_time': str})
        data = meter_df.to_dict('records')
        data = process_warn(data)
        socket_data['meter'].extend(data)

    # meter FACTORY
    meter_settings = FilesystemSettings(
        target_name_list=['meter_METER_FACTORY*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    meter_df = file_dao.read(criteria=meter_settings)
    if not meter_df.empty:
        meter_df['data_time'] = pd.to_datetime(meter_df['data_time'])
        condition = (meter_df['data_time'] >= now) & (meter_df['data_time'] < e_now)
        meter_df = meter_df[condition]
        meter_df = meter_df.sort_values(by='data_time', ascending=True)
        meter_df = meter_df.head(1)
        meter_df = meter_df.replace({'None': None, 'nan': None, np.NAN: None})
        meter_df = meter_df.astype({'data_time': str})
        data = meter_df.to_dict('records')
        data = process_warn(data)
        socket_data['meter'].extend(data)

    # meter CABINET
    meter_settings = FilesystemSettings(
        target_name_list=['meter_METER_CABINET*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    meter_df = file_dao.read(criteria=meter_settings)
    if not meter_df.empty:
        meter_df['data_time'] = pd.to_datetime(meter_df['data_time'])
        condition = (meter_df['data_time'] >= now) & (meter_df['data_time'] < e_now)
        meter_df = meter_df[condition]
        meter_df = meter_df.sort_values(by='data_time', ascending=True)
        meter_df = meter_df.head(1)
        meter_df = meter_df.replace({'None': None, 'nan': None, np.NAN: None})
        meter_df = meter_df.astype({'data_time': str})
        data = meter_df.to_dict('records')
        data = process_warn(data)
        socket_data['meter'].extend(data)

    # Air A
    air_settings = FilesystemSettings(
        target_name_list=['air_AIR_A*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    air_df = file_dao.read(criteria=air_settings)
    if not air_df.empty:
        air_df['data_time'] = pd.to_datetime(air_df['data_time'])
        condition = (air_df['data_time'] >= now) & (air_df['data_time'] < e_now)
        air_df = air_df[condition]
        air_df = air_df.sort_values(by='data_time', ascending=True)
        air_df = air_df.head(1)
        air_df = air_df.replace({'None': None, 'nan': None, np.NAN: None})
        air_df = air_df.astype({'data_time': str})
        data = air_df.to_dict('records')
        data = process_warn(data)
        socket_data['bms_air'].extend(data)

    # Air B
    air_settings = FilesystemSettings(
        target_name_list=['air_AIR_B*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    air_df = file_dao.read(criteria=air_settings)
    if not air_df.empty:
        air_df['data_time'] = pd.to_datetime(air_df['data_time'])
        condition = (air_df['data_time'] >= now) & (air_df['data_time'] < e_now)
        air_df = air_df[condition]
        air_df = air_df.sort_values(by='data_time', ascending=True)
        air_df = air_df.head(1)
        air_df = air_df.replace({'None': None, 'nan': None, np.NAN: None})
        air_df = air_df.astype({'data_time': str})
        data = air_df.to_dict('records')
        data = process_warn(data)
        socket_data['bms_air'].extend(data)

    # Fan A
    fan_settings = FilesystemSettings(
        target_name_list=['fan_FAN_A*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    fan_df = file_dao.read(criteria=fan_settings)
    if not fan_df.empty:
        fan_df['data_time'] = pd.to_datetime(fan_df['data_time'])
        condition = (fan_df['data_time'] >= now) & (fan_df['data_time'] < e_now)
        fan_df = fan_df[condition]
        fan_df = fan_df.sort_values(by='data_time', ascending=True)
        fan_df = fan_df.head(1)
        fan_df = fan_df.replace({'None': None, 'nan': None, np.NAN: None})
        fan_df = fan_df.astype({'data_time': str})
        data = fan_df.to_dict('records')
        data = process_warn(data)
        socket_data['bms_fan'].extend(data)

    # Fan B
    fan_settings = FilesystemSettings(
        target_name_list=['fan_FAN_B*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    fan_df = file_dao.read(criteria=fan_settings)
    if not fan_df.empty:
        fan_df['data_time'] = pd.to_datetime(fan_df['data_time'])
        condition = (fan_df['data_time'] >= now) & (fan_df['data_time'] < e_now)
        fan_df = fan_df[condition]
        fan_df = fan_df.sort_values(by='data_time', ascending=True)
        fan_df = fan_df.head(1)
        fan_df = fan_df.replace({'None': None, 'nan': None, np.NAN: None})
        fan_df = fan_df.astype({'data_time': str})
        data = fan_df.to_dict('records')
        data = process_warn(data)
        socket_data['bms_fan'].extend(data)

    # IO
    io_settings = FilesystemSettings(
        target_name_list=['io_*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    io_df = file_dao.read(criteria=io_settings)
    if not io_df.empty:
        io_df['data_time'] = pd.to_datetime(io_df['data_time'])
        condition = (io_df['data_time'] >= now) & (io_df['data_time'] < e_now)
        io_df = io_df[condition]
        io_df = io_df.sort_values(by='data_time', ascending=True)
        io_df = io_df.head(1)
        io_df = io_df.replace({'None': None, 'nan': None, np.NAN: None})
        io_df = io_df.astype({'data_time': str})
        data = io_df.to_dict('records')
        data = process_warn(data)
        socket_data['io'].extend(data)

    # env_status
    env_settings = FilesystemSettings(
        target_name_list=['femc_*'], target_data=FolderType.History, base_path="/app/data",
        filter_date_star=s_time, filter_date_end=e_time
    )
    env_df = file_dao.read(criteria=env_settings)
    if not env_df.empty:
        env_df['data_time'] = pd.to_datetime(env_df['data_time'])
        condition = (env_df['data_time'] >= now) & (env_df['data_time'] < e_now)
        env_df = env_df[condition]
        env_df = env_df.sort_values(by='data_time', ascending=True)
        env_df = env_df.head(1)
        env_df = env_df.replace({'None': None, 'nan': None, np.NAN: None})
        env_df = env_df.astype({'data_time': str})
        data = env_df.to_dict('records')
        data = process_warn(data)
        socket_data['env_status'].extend(data)

    socket_data['meter'].append(meter_sun)
    return socket_data


def process_warn(data):
    if len(data) > 0:
        for d in data:
            # Warning處理
            if d['warning'] is not None and type(d['warning']) is str:
                d['warning'] = json.loads(d['warning'])

            # BMS 套別處理
            if 'rack_list' in d:
                if d['rack_list']:
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
                    del d['rack_list']
                    racks = racks.replace('None', 'null')
                    d['rack'] = json.loads(racks)
                else:
                    del d['rack_list']
                    d['rack'] = list()

    return data

def get_week_dates(target_date, start_day=0):
    # 星期一是0，星期天是6
    current_weekday = target_date.weekday()
    if start_day <= current_weekday:
        start_of_week = target_date - timedelta(days=current_weekday - start_day)
    else:
        start_of_week = target_date - timedelta(days=current_weekday - start_day + 7)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    return week_dates
