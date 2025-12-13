from typing import List

import numpy as np
import pandas as pd


class ECI_Indicator:
    def __init__(self, col_name, cal_type, usl, lsl):
        self.col_name = col_name
        self.cal_type = cal_type
        self.usl = usl
        self.lsl = lsl


class ECI:
    def __init__(self, pd_data, rack_id):
        self.pd_data = pd_data
        self.rack_id = rack_id
        self.ici_list = None
        self.eci_list = None
        self.raw_list = None

    def to_json(self):
        return {
            'rack_id': self.rack_id,
            'ici_list': self.ici_list,
            'eci_list': self.eci_list,
            'raw_list': self.raw_list
        }

    def get_eci(self, vol_count=20, temp_count=68, threshold=0.1, rack_id=None):
        tot_column_list = self.pd_data.columns.values.tolist()
        merge_df = pd.DataFrame()
        group_column = []
        group_temp = []

        temp_group1 = []
        temp_group2 = []

        vol_pack_idx = 1
        tmp_pack_idx = 1
        for idx, column_name in enumerate(tot_column_list):
            if column_name.startswith('V'):
                if idx != 0 and idx % vol_count == 0:
                    if len(temp_group1) > 0:
                        group_column.append(temp_group1)
                        vol_pack_idx = vol_pack_idx + 1
                    temp_group1 = []
                temp_group1.append(column_name)

            elif column_name.startswith('T'):
                if idx != 0 and idx % temp_count == 0:
                    if len(temp_group2) > 0:
                        group_temp.append(temp_group2)
                        tmp_pack_idx = tmp_pack_idx + 1
                    temp_group2 = []
                # 添加溫度表頭
                temp_group2.append(column_name)

        # 添加最後一筆表頭
        if temp_group1:
            group_column.append(temp_group1)

        if temp_group2:
            group_temp.append(temp_group2)

        raw_data_list = []
        for idx, item in enumerate(group_column):
            vol_data = self.pd_data[item].values.tolist()
            name_idx = idx+1
            # 添加原始數據資訊(For 前端)
            temp_name = str(name_idx).rjust(2, "0")
            temp_raw_data = {
                'key': f'CSC{temp_name}',
                'rack_key': rack_id,
                'data': vol_data
            }
            raw_data_list.append(temp_raw_data)

            # 計算V ICI
            v_data = self.pd_data[item]
            serial = ((v_data.max(axis=1) - v_data.min(axis=1)) / (2 * v_data.mean(axis=1)))
            # serial = v_data.max(axis=1) - v_data.min(axis=1)
            ici = (serial - 0) / (threshold / 3)
            temp_df = pd.DataFrame(data=ici.tolist(), columns=[f'CSC{temp_name}'],
                                   index=pd.RangeIndex(start=0, stop=len(ici), step=1))
            if merge_df.empty:
                merge_df = temp_df
            else:
                merge_df = merge_df.merge(temp_df, left_index=True, right_index=True)

        if group_temp:
            temp_data = self.pd_data[group_temp[0]].values.tolist()
            temp_raw_data2 = {
                'key': 'T',
                'rack_key': rack_id,
                'data': temp_data
            }
            raw_data_list.append(temp_raw_data2)

            temp_data = self.pd_data[group_temp[0]]
            serial = ((temp_data.max(axis=1) - temp_data.min(axis=1)) / (2 * temp_data.mean(axis=1)))
            temp_ici = (serial - 0) / (1 / 3)
            temp_df = pd.DataFrame(data=temp_ici.tolist(), columns=['T'],
                                   index=pd.RangeIndex(start=0, stop=len(temp_ici), step=1))

            # # 置換ici 介於 +- 1之間
            # temp_df[f'P{idx + 1}_T'] = temp_df[f'P{idx + 1}_T'].apply(lambda x: 1 if x > 1 else -1 if x < -1 else x)
            if merge_df.empty:
                merge_df = temp_df
            else:
                merge_df = merge_df.merge(temp_df, left_index=True, right_index=True)

        col_list = merge_df.columns.to_list()
        eci_list = []
        ici_list = []
        key = 0
        for idx, data in merge_df.iterrows():
            key = key + 1
            rack_key = rack_id
            ici = data

            eci = 1 - np.mean(abs(ici))
            if pd.isnull(eci):
                eci = None

            ici_dic = dict(zip(col_list, ici.tolist()))

            ici_dic = dict(sorted(ici_dic.items(), key=lambda x: np.absolute(x[1]), reverse=True))
            ici_append = [{'key': key, 'value': None if pd.isnull(ici_dic[key]) else ici_dic[key]} for key in ici_dic.keys()]
            ici_list.append({'key': key, 'value': ici_append})
            eci_list.append({'key': key, 'rack_key': rack_key, 'value': eci})

        self.ici_list = ici_list
        self.eci_list = eci_list

        raw_list = []
        all_raw_list = []
        for idx, dic in enumerate(raw_data_list):
            for currentIdx, raw in enumerate(dic['data']):
                raw_list.append(
                    {
                        'key': currentIdx + 1,
                        'key2': dic['key'],
                        'rack_key': dic['rack_key'],
                        'data': [d if not np.isnan(d) else None for d in raw]
                    }
                )
            # all_raw_list.append(raw_list)
        self.raw_list = raw_list


class ESSECI:
    def __init__(self, eci_data_list: List[ECI]):
        self.eci_data_list = eci_data_list
        self.ici_list = list()
        self.eci_list = list()
        self.raw_list = list()
        self.eci_value_list = list()
        for i, eci in enumerate(eci_data_list):
            self.eci_value_list.append([item['value'] for item in eci.eci_list])

    def get_esseci(self):
        temp = np.asarray(self.eci_value_list)
        # min = temp.min(axis=0, keepdims=True)
        min_index = temp.argmin(axis=0)
        for idx, idx_value in enumerate(min_index):
            self.eci_list.append(self.eci_data_list[idx_value].eci_list[idx])
            self.ici_list.append(self.eci_data_list[idx_value].ici_list[idx])
            key1 = self.eci_data_list[idx_value].eci_list[idx]['key']
            key2 = self.eci_data_list[idx_value].eci_list[idx]['rack_key']
            raw_data = filter(lambda x: x['key'] == key1 and x['rack_key'] == key2, self.eci_data_list[idx_value].raw_list)
            self.raw_list.append(list(raw_data))