import datetime
from typing import List

import numpy as np
import pandas as pd


class RackInfo:
    def __init__(self, data_time, rack_name, data):
        self.data_time: datetime = data_time
        self.name = rack_name
        self.data = data


def get_bmu_data(data_time, rack_data: pd.DataFrame, indicator, level, target_rack, target_pack):
    rtn_data_list: List[RackInfo] = list()
    if rack_data.empty:
        return rtn_data_list

    if level == 'rack':
        if indicator == 'temp':
            rtn_data_list = [
                RackInfo(data_time, getattr(i, 'equipment_id'), getattr(i, 'rack_avg_cell_temperature'))
                for i in rack_data.itertuples(index=False)
            ]
        elif indicator == 'voltage':
            rtn_data_list = [
                RackInfo(data_time, getattr(i, 'equipment_id'), getattr(i, 'rack_voltage'))
                for i in rack_data.itertuples(index=False)
            ]
        elif indicator == 'current':
            rtn_data_list = [
                RackInfo(data_time, getattr(i, 'equipment_id'), getattr(i, 'rack_current'))
                for i in rack_data.itertuples(index=False)
            ]

    elif level in ['pack', 'cell']:
        # 過濾特定 rack
        pack_df = pd.DataFrame()
        rack_data = rack_data[rack_data['rack_no'] == int(target_rack)]
        if not rack_data.empty:
            packs_dict = rack_data.iloc[0]['packs']
            pack_df = pd.DataFrame(packs_dict)
            if not pack_df.empty and target_pack:
                pack_df = pack_df[pack_df['pack_no'] == int(target_pack)]
        if pack_df.empty:
            return rtn_data_list

        if indicator == 'temp':
            if not target_pack:
                # pack level
                rtn_data_list = [
                    RackInfo(
                        data_time,
                        f"pack_{getattr(i, 'pack_no')}",
                        round(np.mean(getattr(i, 'cell_temp')), 2))
                    for i in pack_df.itertuples(index=False)
                ]
            else:
                # cell level
                rtn_data_list = [
                    RackInfo(data_time, f"cell_{idx + 1}", round(d, 2))
                    for idx, d in enumerate(pack_df.iloc[0]['cell_temp'])
                ]
        elif indicator == 'voltage':
            if not target_pack:
                # pack level
                rtn_data_list = [
                    RackInfo(
                        data_time,
                        f"pack_{getattr(i, 'pack_no')}",
                        round(np.mean(getattr(i, 'cell_volt')), 3))
                    for i in pack_df.itertuples(index=False)
                ]
            else:
                volt_list = pack_df.iloc[0]['cell_volt']
                # cell level
                rtn_data_list = [
                    RackInfo(
                        data_time,
                        f"cell_{idx + 1}",
                        value)
                    for idx, value in enumerate(volt_list)
                ]

    return rtn_data_list


def replace_json_string(json_string):
    return json_string.replace("]'", "]")\
        .replace("'[", "[")\
        .replace("false", 'False')\
        .replace("true", 'True')\
        .replace("null", 'None')
