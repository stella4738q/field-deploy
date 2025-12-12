import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
import os
import string
from apps.dashboard.constant import ApiConst
from flask import session
from utility.token_module import UserData
from apps.dashboard import token_module

regulation_list = [ApiConst.DREG025.value, ApiConst.DREG05.value, ApiConst.EDREG.value]
work_range_list_025 = [f'{ApiConst.RANGE_NEGATIVE_52.value}%~{ApiConst.RANGE_NEGATIVE_100.value}%',
                       f'{ApiConst.RANGE_NEGATIVE_9.value}%~{ApiConst.RANGE_NEGATIVE_52.value}%',
                       f'{ApiConst.RANGE_9.value}%~{ApiConst.RANGE_NEGATIVE_9.value}%',
                       f'{ApiConst.RANGE_52.value}%~{ApiConst.RANGE_9.value}%',
                       f'{ApiConst.RANGE_100.value}%~{ApiConst.RANGE_52.value}%']
work_range_list_05 = [f'{ApiConst.RANGE_NEGATIVE_48.value}%~{ApiConst.RANGE_NEGATIVE_100.value}%',
                      f'{ApiConst.RANGE_NEGATIVE_9.value}%~{ApiConst.RANGE_NEGATIVE_48.value}%',
                      f'{ApiConst.RANGE_9.value}%~{ApiConst.RANGE_NEGATIVE_9.value}%',
                      f'{ApiConst.RANGE_48.value}%~{ApiConst.RANGE_9.value}%',
                      f'{ApiConst.RANGE_100.value}%~{ApiConst.RANGE_48.value}%']
time_list = [[1, 16, 99, 24, 3], [2, 14, 78, 33, 2], [4, 19, 88, 33, 8]]
continue_time_list = [[30, 40, 60, 30, 60], [20, 30, 54, 20, 49], [29, 39, 49, 20, 34]]
TRUE_LIST = [ApiConst.TRUE.value, True, "TRUE"]
FALSE_LIST = [ApiConst.FALSE.value, False, "FALSE"]
NONE_LIST = ["None", ""]
NAN_0_LIST = ["NAN", "", 0, "0"]


class FeatureFunc:
    @staticmethod
    def get_column_name(index):
        index = index + 5
        if index < 26:
            return string.ascii_uppercase[index]
        elif index < 702:
            return string.ascii_uppercase[(index // 26) - 1] + string.ascii_uppercase[index % 26]
        else:
            return string.ascii_uppercase[(index // 676) - 1] + FeatureFunc.get_column_name(index % 676 + 26)

    @staticmethod
    def date_list(sdate, edate):
        """
        sdate : str, YYYYMMDD
        edate : str, YYYYMMDD
        """
        date_list = []
        _sdate = dt.date(int(sdate[:4]), int(sdate[4:6]), int(sdate[6:8]))
        _edate = dt.date(int(edate[:4]), int(edate[4:6]), int(edate[6:8]))
        delta = dt.timedelta(days=1)
        while _sdate <= _edate:
            date_list.append(_sdate.strftime("%Y%m%d"))
            _sdate += delta
        return date_list

    @staticmethod
    def full_date(sdate, edate=None):
        if edate is None:
            res_sdate = datetime.strptime(sdate, "%Y%m%d").strftime("%Y-%m-%d 00:00:00")
            res_edate = datetime.strptime(sdate, "%Y%m%d").strftime("%Y-%m-%d 23:59:59")
        else:
            res_sdate = datetime.strptime(sdate, "%Y%m%d").strftime("%Y-%m-%d 00:00:00")
            res_edate = datetime.strptime(edate, "%Y%m%d").strftime("%Y-%m-%d 23:59:59")
        return res_sdate, res_edate
    @staticmethod
    def get_series_data(data, column, to_float=False, decimal=2):
        if (column in data.keys()):
            res = (data[column])
            if (to_float) and isinstance(res, str):
                res = round(float(res), decimal)
            if pd.isna(res):
                res = None
        else:
         res = None
        return res

    @staticmethod
    def round_data(data, input_columns: list, decimal=2):
        existing_columns = [column for column in input_columns if column in data.columns]
        data[existing_columns] = data[existing_columns].round(decimal)
        return data

    @staticmethod
    def get_data_sum(data, column):
        if (column in data.columns) and (data[column] is not None):
            data[column] = data[column].astype(float).replace({None: 0, "None": 0, np.nan: 0})
            res = round(sum(data[column]), 2)
            if pd.isna(res):
                res = None
        else:
         res = None
        return res

    @staticmethod
    def to_strptime(value):
        if len(value) != 19:
            value = value[:19]
        res = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return res
    @staticmethod
    def to_boolean(value):
        value = str(value).upper()
        if value in TRUE_LIST:
            res = True
        else:
            res = False
        return res

    @staticmethod
    def sum_data_and_to_int(data, column):
        res = sum(map(FeatureFunc.to_int, FeatureFunc.none_list(data, column)))
        return res

    @staticmethod
    def to_int(value):
        if (value is None) or (value == 'None'):
            value = 0
        elif pd.isna(value):
            value = 0
        else:
            try:
                value = int(value)
            except:
                value = 0
        return value

    @staticmethod
    def to_float(value):
        if (value is None) or (value == 'None'):
            value = 0
        elif pd.isna(value):
            value = 0
        else:
            try:
                value = float(value)
            except:
                value = 0
        return value

    @staticmethod
    def replace_nan_to_0(value):
        if np.isnan(value):
            value = 0
        return value

    @staticmethod
    def replace_nan(value):
        if (value is not None) and (value != 'None'):
            if np.isnan(value):
                value = None
        return value

    @staticmethod
    def result_dict(logger, pd_data):
        pd_data = pd_data.replace({np.nan: None})
        for column in pd_data.columns:
            if column[-2:] == 'id':
                pd_data[column] = pd_data[column].astype(str)
        logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))
        pd_res = pd_data.to_dict('records')
        return pd_res

    @staticmethod
    def delete_file(logger, filepaths: list):
        for filepath in filepaths:
            if os.path.exists(filepath):
                logger.debug(f'delete file: {filepath}')
                os.remove(filepath)
                if os.path.exists(filepath):
                    logger.error(f'delete file is not success, {filepath} still exists.')

    @staticmethod
    def none_list(data, column, lens=None):
        if not lens:
            lens = len(data)

        res = list(data[column]) if (not data.empty) and (column in data.columns) and (not data[column].empty) else [None] * lens
        return res
    @staticmethod
    def none_value(data, column):
        res = data[column].reset_index(drop=True)[0] if (not data.empty) and (column in data.columns) and (not data[column].empty) else 0
        return res

    @staticmethod
    def empty_list(data, column):
        res = list(data[column]) if (not data.empty) and (column in data.columns) else list()
        return res

    @staticmethod
    def str_to_datetime(datetime_str):
        res = datetime.strptime(datetime_str, '%H:%M:%S.%f')
        return res

    @staticmethod
    def pd_data_add_null_24(data, just_hour=False):
        for time in range(0, 24):
            if just_hour:
                time = BidCalculate.time_judge_vs_rjust(str(time), just_hour=True)
            else:
                time = str(time).rjust(2, '0')
                time = BidCalculate.time_judge(str(time))
            if time not in list(data[ApiConst.TIME.value]):
                row = [time if column == ApiConst.TIME.value else None for column in data.columns]
                data.loc[f"new_{time.replace(':', '')}"] = row
        data = data.sort_values(by=[ApiConst.TIME.value]).reset_index(drop=True)
        return data


class BidCalculate:
    @staticmethod
    def service_indicators(service, exacutive_rate):
        indicators = None
        if exacutive_rate is not None:
            if (service == ApiConst.SPINNING_RESERVE.value) or (service == ApiConst.SUPPLEMENT_RESERVE.value):
                if exacutive_rate >= 0.95:
                    indicators = 1
                elif (exacutive_rate < 0.95) and (exacutive_rate >= 0.85):
                    indicators = 0.7
                elif (exacutive_rate < 0.85) and (exacutive_rate >= 0.70):
                    indicators = 0
                elif exacutive_rate < 0.70:
                    if service == ApiConst.SPINNING_RESERVE.value:
                        indicators = -240
                    elif service == ApiConst.SUPPLEMENT_RESERVE.value:
                        indicators = -24
            else:
                if exacutive_rate >= 0.95:
                    indicators = 1
                elif (exacutive_rate < 0.95) and (exacutive_rate >= 0.85):
                    indicators = 0.85
                elif (exacutive_rate < 0.85) and (exacutive_rate >= 0.75):
                    indicators = 0.75
                elif (exacutive_rate < 0.75) and (exacutive_rate >= 0.70):
                    indicators = 0
                elif exacutive_rate < 0.70:
                    indicators = 0.75
        return indicators

    @staticmethod
    def income(service_indicators, close_capacity, close_capacity_pay, performance_pay, total_time, electricity_pay, actually=False):
        if not actually:
            service_indicators = 1
        service_indicators = FeatureFunc.to_int(service_indicators)
        electricity_pay = FeatureFunc.to_int(electricity_pay)
        income_money = (close_capacity_pay + (performance_pay * close_capacity)) * total_time * service_indicators + electricity_pay
        return income_money

    @staticmethod
    def capacity_pay(data, capacity):
        capacity_pay_one = FeatureFunc.replace_nan(sum(map(
            FeatureFunc.to_int, FeatureFunc.none_list(data, ApiConst.CAPACITY_PAY.value))))
        capacity_pay = capacity * capacity_pay_one
        return FeatureFunc.replace_nan_to_0(capacity_pay)

    @staticmethod
    def performance_pay(service, performance_level):
        pay = 0
        if service in regulation_list:
            if performance_level == 1:
                pay = 350
            elif performance_level == 2:
                pay = 275
            elif performance_level == 3:
                pay = 200
            elif performance_level == 4:
                pay = 125
            elif performance_level == 5:
                pay = 50
        elif service == ApiConst.SPINNING_RESERVE.value:
            if performance_level == 1:
                pay = 100
            elif performance_level == 2:
                pay = 60
            elif performance_level == 3:
                pay = 40
        return pay

    @staticmethod
    def capacity(status, communication_list: list, implement_list: list, capacity_list: list):
        # one case code one status
        capacity_sum = 0
        if status == True:
            for communication, implement, capacity in zip(communication_list, implement_list, capacity_list):
                if (communication == 1) and (implement == 1):
                    capacity_sum = capacity_sum + capacity
        return capacity_sum

    @staticmethod
    def example(service):
        capacity_pay = None
        electricity_pay = None
        if service in regulation_list:
            capacity_pay = 600
            electricity_pay = None
        elif service == ApiConst.SPINNING_RESERVE.value:
            capacity_pay = 400
            electricity_pay = None
        elif service == ApiConst.SUPPLEMENT_RESERVE.value:
            capacity_pay = 350
            electricity_pay = 10000
        return capacity_pay, electricity_pay

    @staticmethod
    def day_total(data_list):
        res = 0
        for data in data_list:
            close_capacity_pay = FeatureFunc.to_int(data[ApiConst.CLOSE_CAPACITY_PAY.value])
            performance_pay = FeatureFunc.to_int(data[ApiConst.CLOSE_CAPACITY_PAY.value])
            service_indicators = FeatureFunc.to_int(data[ApiConst.SERVICE_INDICATORS.value])
            close_electricity_pay = FeatureFunc.to_int(data[ApiConst.CLOSE_ELECTRICITY_PAY.value])
            hour_total = ((close_capacity_pay + performance_pay) * service_indicators) + close_electricity_pay
            res = res + hour_total
        return res

    @staticmethod
    def judge_status_start_and_end(pd_cases_freq, time, status):
        res = 0
        if not pd_cases_freq.empty:
            for index in range(0, len(pd_cases_freq)):
                if time == pd_cases_freq[ApiConst.TIME.value][index].split(':')[0]:
                    _status = pd_cases_freq[ApiConst.STATUS.value][index]
                    if (status == ApiConst.START.value and _status == "true") or (status == ApiConst.END.value and _status == "false"):
                        res = 1
        return res

    @staticmethod
    def electricity(continue_time, close_capacity, service=None):
        # 調頻被轉
        pay = continue_time * close_capacity
        if service == ApiConst.SPINNING_RESERVE.value:
            pay = ((continue_time * 2 + 1/3) * close_capacity) / 2
        elif service == ApiConst.SUPPLEMENT_RESERVE.value:
            pay = ((continue_time * 2 + 1) * close_capacity) / 2
        return FeatureFunc.replace_nan_to_0(pay)

    @staticmethod
    def frequency(service, execution_freq):
        freq_resource_list = [0, 0, 0, 0, 0]
        total_duration_resource_list = [0, 0, 0, 0, 0]
        if service == ApiConst.DREG025.value:
            work_range = work_range_list_025
            if len(execution_freq) != 0:
                for execution_freq_resource in execution_freq:
                    # -52%~-100%, -9%~-52%, 9%~-9%, 52%~9%, 100%~52%
                    group = None
                    for _execution_freq in execution_freq_resource:
                        if _execution_freq > 60.14:
                            _group = 0
                        elif (_execution_freq > 60.02) and (_execution_freq <= 60.14):
                            _group = 1
                        elif (_execution_freq > 59.98) and (_execution_freq <= 60.02):
                            _group = 2
                        elif (_execution_freq > 59.86) and (_execution_freq <= 59.98):
                            _group = 3
                        else:  # _execution_freq <= 59.86
                            _group = 4
                        total_duration_resource_list[_group] = total_duration_resource_list[_group] + 1
                        if _group != group:
                            freq_resource_list[_group] = freq_resource_list[_group] + 1
                            group = _group
        else:
            work_range = work_range_list_05
            if len(execution_freq) != 0:
                for execution_freq_resource in execution_freq:
                    # -52%~-100%, -9%~-52%, 9%~-9%, 52%~9%, 100%~52%
                    freq_resource_list = [0, 0, 0, 0, 0]
                    total_duration_resource_list = [0, 0, 0, 0, 0]
                    group = None
                    for _execution_freq in execution_freq_resource:
                        if _execution_freq > 60.25:
                            _group = 0
                        elif (_execution_freq > 60.02) and (_execution_freq <= 60.25):
                            _group = 1
                        elif (_execution_freq > 59.98) and (_execution_freq <= 60.02):
                            _group = 2
                        elif (_execution_freq > 59.75) and (_execution_freq <= 59.98):
                            _group = 3
                        else:  # _execution_freq <= 59.75
                            _group = 4
                        total_duration_resource_list[_group] = total_duration_resource_list[_group] + 1
                        if _group != group:
                            freq_resource_list[_group] = freq_resource_list[_group] + 1
        return work_range, freq_resource_list, total_duration_resource_list

    @staticmethod
    def time_judge(time):
        if len(time) == 2:
            time = time + ":00:00"
        return time
    @staticmethod
    def time_judge_vs_rjust(time, no_min=False, just_hour=False):
        if not isinstance(time, str):
            time = str(time)
        if len(time) == 7:
            time = "0" + time
        if (len(time) == 2) or (len(time) == 1):
            time = str(time).rjust(2, '0')
            if not just_hour:
                if no_min:
                    time = time + ":00"
                else:
                    time = time + ":00:00"

        return time

    @staticmethod
    def exacutive_rate(service, frequency, power_actual, capacity, dispatching=False):
        # resource
        res = None
        if (power_actual == 0) or (dispatching is True):
            res = 100
        else:
            if (frequency is not None) and (power_actual is not None):
                output_power = BidCalculate.output_power(service, frequency, power_actual)
                if (service == ApiConst.DREG025.value) or (service == ApiConst.DREG05.value):
                    res = round(((1 - ((output_power - power_actual) / (capacity * 1000))) * 100), 2)
                else:
                    res = round(((abs(power_actual / (capacity * 1000))) * 100), 2)
        return res

    @staticmethod
    def output_power(service, frequency, power_actual):
        power = 0
        if service == ApiConst.DREG025.value:
            if frequency >= 60.25:  # -100%
                power = -100
            elif (frequency >= 60.14) and (frequency < 60.25):  # -100%~-52%
                a, b = BidCalculate.get_line_equ([60.25, 60.14], [-100, -52])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 60.02) and (frequency < 60.14):  # -52%~-9%
                a, b = BidCalculate.get_line_equ([60.14, 60.02], [-52, -9])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 59.98) and (frequency < 60.02):  # -9%~9%
                if power_actual >= 0:
                    power = 9
                else:
                    power = -9
            elif (frequency >= 59.86) and (frequency < 59.98):  # 9%~52%
                a, b = BidCalculate.get_line_equ([59.98, 59.86], [9, 52])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 59.75) and (frequency < 59.86):  # 52%~100%
                a, b = BidCalculate.get_line_equ([59.86, 59.75], [52, 100])
                power = BidCalculate.get_y(frequency, [a, b])
            else:  # 100%, <59.75
                power = 100
        else:
            if frequency >= 60.50:  # -100%
                power = -100
            elif (frequency >= 60.25) and (frequency < 60.50):  # -100%~-48%
                a, b = BidCalculate.get_line_equ([60.25, 60.14], [-100, -48])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 60.02) and (frequency < 60.25):  # -48%~-9%
                a, b = BidCalculate.get_line_equ([60.14, 60.02], [-48, -9])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 59.98) and (frequency < 60.02):  # -9%~9%
                if power_actual >= 0:
                    power = 9
                else:
                    power = -9
            elif (frequency >= 59.75) and (frequency < 59.98):  # 9%~48%
                a, b = BidCalculate.get_line_equ([59.98, 59.86], [9, 48])
                power = BidCalculate.get_y(frequency, [a, b])
            elif (frequency >= 59.50) and (frequency < 59.75):  # 48%~100%
                a, b = BidCalculate.get_line_equ([59.86, 59.75], [48, 100])
                power = BidCalculate.get_y(frequency, [a, b])
            else:  # 100%, <59.50
                power = 100
        return power

    # Return y by giving the lienar equaltion and the x
    @staticmethod
    def get_y(x, line_eq):
        a = line_eq[0]
        b = line_eq[1]
        return a * x + b

    # Get the linear equalition from p1 and p2
    @staticmethod
    def get_line_equ(p1, p2):
        # AX=B
        A = np.array([[p1[0], 1], [p2[0], 1]])
        B = np.array([p1[1], p2[1]])

        a, b = np.linalg.solve(A, B)
        return a, b

def permission_download_function(logger, fields, api_key):
    logger.info('check permission [operation]')
    user_info: UserData = session[token_module.auth_session_key]
    allow_field = user_info.user_field_permission.keys()
    has_permission = False
    for field in fields:
        if len(user_info.user_field_permission) > 0 and \
                field in allow_field and \
                user_info.user_field_permission[field][api_key]:
            has_permission = True
            break
    return has_permission

