import numpy as np
import pandas as pd

from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType


class MeterMapper:
    def __init__(self, meter_brand, pd_data):
        self.meter_brand: str = meter_brand
        self.original_df: pd.DataFrame = pd_data
        self.meter_column = [
            'data_time', 'field_id', 'case_id', 'resource_id', 'equipment_id', 'parent_id',
            'frequency',
            'voltage_a', 'voltage_b', 'voltage_c',
            'current_a', 'current_b', 'current_c',
            'active_power', 'reactive_power', 'apparent_power', 'power_factor',
            'energy_imp', 'energy_exp', 'line_voltage_avg',
            # 需量累積, 選用
            'accu_demand_kw',
        ]

    def transfer_to_template(self):
        if self.meter_brand.lower() == "ion-9000":
            pass
        elif self.meter_brand.lower() == "pm5650":
            self.original_df = self.original_df[
                [
                    "data_time",
                    "field_id",
                    "case_id",
                    "resource_id",
                    "equipment_id",
                    "parent_id",
                    "frequency",
                    "total_power_factor",
                    "i_phs_a",
                    "i_phs_b",
                    "i_phs_c",
                    "i_avg",
                    "v_phs_a",
                    "v_phs_b",
                    "v_phs_c",
                    "v_avg",
                    "p_total",
                    "q_total",
                    "s_total",
                    "total_power_factor",
                    "active_energy_delivered",
                    "active_energy_received"
                ]
            ]
            self.original_df = self.original_df.rename(columns={
                'i_phs_a': 'current_a',
                'i_phs_b': 'current_b',
                'i_phs_c': 'current_c',
                'i_avg': 'current_average',
                'v_phs_a': 'voltage_a',
                'v_phs_b': 'voltage_b',
                'v_phs_c': 'voltage_c',
                'v_avg': 'line_voltage_avg',
                'p_total': 'active_power',
                'q_total': 'reactive_power',
                's_total': 'apparent_power',
                'total_power_factor': 'power_factor',
                'active_energy_received': 'energy_imp',
                'active_energy_delivered': 'energy_exp'
            })
        elif self.meter_brand.lower() == "pm335":
            self.original_df = self.original_df.drop([
                'voltage_a',
                'voltage_b',
                'voltage_c',
                'line_voltage_avg'
            ], axis=1)
            self.original_df = self.original_df.rename(columns={
                'voltage_ab': 'voltage_a',
                'voltage_bc': 'voltage_b',
                'voltage_ca': 'voltage_c',
                'voltage_avg': 'line_voltage_avg',
                'total_active_power': 'active_power',
                'total_reactive_power': 'reactive_power',
                'total_apparent_power': 'apparent_power',
                'total_power_factor': 'power_factor',
                'ac_energy_imp': 'energy_imp',
                'ac_energy_exp': 'energy_exp'
            })
        elif self.meter_brand.lower() == "pm135":
            self.original_df = self.original_df.drop([
                'voltage_a',
                'voltage_b',
                'voltage_c',
                'line_voltage_avg'
            ], axis=1)
            self.original_df = self.original_df.rename(columns={
                'voltage_ab': 'voltage_a',
                'voltage_bc': 'voltage_b',
                'voltage_ca': 'voltage_c',
                'voltage_avg': 'line_voltage_avg',
                'total_active_power': 'active_power',
                'total_reactive_power': 'reactive_power',
                'total_apparent_power': 'apparent_power',
                'total_power_factor': 'power_factor',
                'ac_energy_imp': 'energy_imp',
                'ac_energy_exp': 'energy_exp'
            })
        elif self.meter_brand.lower() == "pm7360":
            self.original_df = self.original_df.drop([
                'voltage_a',
                'voltage_b',
                'voltage_c',
                'line_voltage_avg'
            ], axis=1)
            self.original_df = self.original_df.rename(columns={
                'voltage_ab': 'voltage_a',
                'voltage_bc': 'voltage_b',
                'voltage_ca': 'voltage_c',
                'voltage_avg': 'line_voltage_avg',
                'total_active_power': 'active_power',
                'total_reactive_power': 'reactive_power',
                'total_apparent_power': 'apparent_power',
                'total_power_factor': 'power_factor',
                'ac_energy_imp': 'energy_imp',
                'ac_energy_exp': 'energy_exp',
                # 需量累積, 選用
                'accu_demand_kw': 'accu_demand_kw'
            })
        elif self.meter_brand.lower() == "eba43":
            self.original_df = self.original_df.rename(columns={
                'voltage_ab': 'voltage_a',
                'voltage_bc': 'voltage_b',
                'voltage_ca': 'voltage_c',
                # 'voltage_avg': 'line_voltage_avg',
                'total_active_power': 'active_power',
                'total_reactive_power': 'reactive_power',
                'total_apparent_power': 'apparent_power',
                'total_power_factor': 'power_factor',
                'ac_energy_imp': 'energy_imp',
                'ac_energy_exp': 'energy_exp'
            })
        elif self.meter_brand.lower() == "m1m30":
            self.original_df = self.original_df.drop([
                'voltage_a',
                'voltage_b',
                'voltage_c',
                'line_voltage_avg'
            ], axis=1)
            self.original_df = self.original_df.rename(columns={
                'voltage_ab': 'voltage_a',
                'voltage_bc': 'voltage_b',
                'voltage_ca': 'voltage_c',
                'voltage_avg': 'line_voltage_avg',
                'total_active_power': 'active_power',
                'total_reactive_power': 'reactive_power',
                'total_apparent_power': 'apparent_power',
                'total_power_factor': 'power_factor',
                'ac_energy_imp': 'energy_imp',
                'ac_energy_exp': 'energy_exp'
            })

        # 排除掉目標欄位不存在項目者
        col_list = self.original_df.columns.tolist()
        current_col = [col for col in self.meter_column if col in col_list]
        return self.original_df[current_col]
