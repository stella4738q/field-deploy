import datetime
import threading

import pandas as pd
from pyModbusTCP.client import ModbusClient
import time
from abc import ABC

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from apps.dashboard import config
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType
from dashboard_lib.iec61850.iec61850_const import DataType


class PCSController(ABC):
    def get_manual_discharge(self):
        ...

    def get_isolated_power_grid(self):
        ...

    def get_black_start(self):
        ...


class SunGrow(PCSController):
    def get_manual_discharge(self):
        return 123

    def get_isolated_power_grid(self):
        return 456

    def get_black_start(self):
        return 789


class Kelong(PCSController):
    def get_manual_discharge(self):
        return 4

    def get_isolated_power_grid(self):
        return 5

    def get_black_start(self):
        return 6


class BrandController:
    def __init__(self, brand_name):
        self.brand_name = brand_name

    def get_pcs_template(self) -> PCSController:
        if self.brand_name == "sun_grow":
            return SunGrow()
        elif self.brand_name == "KELONG":
            return Kelong()


"""""""""""""""""""""""""""""""""""""""
以下為為前端控制機器使用 Modbus
"""""""""""""""""""""""""""""""""""""""


class ModbusControlBase:

    def __init__(self, client: ModbusClient, customer, equipment_id=None):
        self.client = client
        self.customer = customer
        self.equipment_id = equipment_id
        ...

    def pcs_on_off(self, on_off):
        ...

    def pcs_set_mode(self, mode):
        ...

    def pcs_fault_reset(self, value):
        ...

    def pcs_set_power(self, value):
        ...

    def pcs_set_cc_cv(self, value):
        ...

    def bms_on_off(self, on_off):
        ...

    def bms_fault_reset(self, on_off):
        ...

    def bms_air_on_off(self, on_off, eq_id=None):
        ...

    def bms_fan_on_off(self, on_off, eq_id=None):
        ...

    def bms_dc_switch_on_off(self, on_off):
        ...

    def dcp_on_off(self, on_off, no):
        ...

    def sunctl_on_off(self, on_off):
        ...

    def fire_on_off(self, on_off):
        ...

    def acb_on_off(self, on_off):
        ...

    def emergency_on_off(self, on_off):
        ...

    # 功能開關相關
    def lc_black_start_on_off(self, on_off):
        ...

    def pcs_black_start_on_off(self, on_off):
        ...

    def get_black_start(self):
        ...

    def pcs_black_start_fault_reset(self):
        ...

    def inverter_on_off(self, on_off):
        ...

    def inverter_set_power_percent(self, power):
        ...

    def pump_on_off(self, on_off, equipment_id):
        ...

    def water_on_off(self, on_off, equipment_id):
        ...

    def sol_on_off(self, on_off, equipment_id):
        ...


# 控制太陽能開關
class PrimeVolt(ModbusControlBase):
    def inverter_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                # 0：關機；1：開機
                self.client.write_single_register(24577, 0)
            else:
                self.client.write_single_register(24577, 1)
        else:
            raise NotImplementedError

    def inverter_set_power_percent(self, power_percent):
        if self.customer and self.customer.lower() == 'advanced':
            _percent = convert_to_uint_16(power_percent)
            self.client.write_single_register(20528, 0)  # PureActivePower
            self.client.write_single_register(12293, _percent)
        else:
            raise NotImplementedError


class SolarEdge(ModbusControlBase):
    def inverter_on_off(self, on_off):
        raise NotImplementedError

    def inverter_set_power_percent(self, power_percent):
        if self.customer and self.customer.lower() == 'advanced':
            _percent = convert_to_uint_16(power_percent)
            self.client.write_single_register(61441, _percent)
        else:
            raise NotImplementedError


class FimerPCS(ModbusControlBase):
    @staticmethod
    def s32_to_u16(value):
        if value < 0:
            value = value + 0x1_0000_0000  # Convert back to unsigned value

        msb = (value >> 16) & 0xFFFF
        lsb = value & 0xFFFF

        return [msb, lsb]

    def pcs_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                # 開機
                # 功率設定為0
                self.client.write_single_register(42244, 0)

                # # 錯誤清除
                self.client.write_single_register(42241, 137)
                self.client.write_single_register(42241, 129)
                # 搭接電池
                self.client.write_single_register(42241, 135)

                # 可充放電功率設定 100%
                self.client.write_single_register(42250, 1100)
                self.client.write_single_register(42251, 1100)
            else:
                # 關機
                # 功率設定為0
                self.client.write_single_register(42244, 0)
                # 斷開電池
                self.client.write_single_register(42241, 129)
                # 關閉inverter
                # self.client.write_single_register(42241, 128)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                # 開機
                # 功率設定為0
                self.client.write_single_register(42244, 0)

                # # 錯誤清除
                self.client.write_single_register(42241, 137)
                self.client.write_single_register(42241, 129)
                # 搭接電池
                self.client.write_single_register(42241, 135)

                # 可充放電功率設定 100%
                self.client.write_single_register(42250, 1100)
                self.client.write_single_register(42251, 1100)
            else:
                # 關機
                # 功率設定為0
                self.client.write_single_register(42244, 0)
                # 斷開電池
                self.client.write_single_register(42241, 129)
                # 關閉inverter
                # self.client.write_single_register(42241, 128)
        else:
            raise NotImplementedError

    def pcs_set_power(self, value):
        if self.customer and self.customer.lower() == 'advanced':
            value = convert_to_uint_16(value)
            self.client.write_single_register(42244, value)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            value = convert_to_uint_16(value)
            self.client.write_single_register(42244, value)
        else:
            raise NotImplementedError

    def pcs_fault_reset(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            self.client.write_single_register(42241, 137)
            # self.client.write_single_register(42241, 8)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            self.client.write_single_register(42241, 137)
            # self.client.write_single_register(42241, 8)
        else:
            raise NotImplementedError

    def pcs_black_start_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                def delay_2min():
                    # 搭接電池
                    self.client.write_single_register(42241, 641)

                    time.sleep(130)  # 等待130秒後繼續動作

                    self.client.write_single_register(42241, 649)  # 故障清除
                    time.sleep(1)

                    self.client.write_single_register(42241, 645)
                    time.sleep(1)

                    # 搭接逆變器
                    self.client.write_single_register(42241, 647)

                status = self.client.read_holding_registers(42241)[0]
                # 已初始化過
                if status == 641:
                    self.client.write_single_register(42241, 649)  # 故障清除
                    time.sleep(1)
                    self.client.write_single_register(42241, 645)
                    time.sleep(1)
                    # 搭接逆變器
                    self.client.write_single_register(42241, 647)

                # 初始化
                else:
                    # 黑啟動開啟
                    # 設定參數
                    self.client.write_single_register(42254, 6900)  # 電壓
                    self.client.write_single_register(42255, 100)
                    self.client.write_single_register(42256, 6000)  # 頻率
                    self.client.write_single_register(42257, 100)

                    async_task = threading.Thread(target=delay_2min)
                    async_task.start()
            else:
                # 黑啟動關閉
                self.client.write_single_register(42241, 645)
                time.sleep(1)
                self.client.write_single_register(42241, 641)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                def delay_2min():
                    # 搭接電池
                    self.client.write_single_register(42241, 641)

                    time.sleep(130)  # 等待130秒後繼續動作

                    self.client.write_single_register(42241, 649)  # 故障清除
                    time.sleep(1)

                    self.client.write_single_register(42241, 645)
                    time.sleep(1)

                    # 搭接逆變器
                    self.client.write_single_register(42241, 647)

                status = self.client.read_holding_registers(42241)[0]
                # 已初始化過
                if status == 641:
                    self.client.write_single_register(42241, 649)  # 故障清除
                    time.sleep(1)
                    self.client.write_single_register(42241, 645)
                    time.sleep(1)
                    # 搭接逆變器
                    self.client.write_single_register(42241, 647)

                # 初始化
                else:
                    # 黑啟動開啟
                    # 設定參數
                    self.client.write_single_register(42254, 6900)  # 電壓
                    self.client.write_single_register(42255, 100)
                    self.client.write_single_register(42256, 6000)  # 頻率
                    self.client.write_single_register(42257, 100)

                    async_task = threading.Thread(target=delay_2min)
                    async_task.start()
            else:
                # 黑啟動關閉
                self.client.write_single_register(42241, 645)
                time.sleep(1)
                self.client.write_single_register(42241, 641)
        else:
            raise NotImplementedError

    def pcs_black_start_fault_reset(self):
        if self.customer and self.customer.lower() == 'advanced':
            self.client.write_single_register(42241, 655)
            time.sleep(1)
            self.client.write_single_register(42241, 647)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            self.client.write_single_register(42241, 655)
            time.sleep(1)
            self.client.write_single_register(42241, 647)
        else:
            raise NotImplementedError

    def emergency_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                # 功率設定為0
                self.client.write_single_register(42244, 0)
                # 斷開電池
                self.client.write_single_register(42241, 129)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                # 功率設定為0
                self.client.write_single_register(42244, 0)
                # 斷開電池
                self.client.write_single_register(42241, 129)
        else:
            raise NotImplementedError


class EticaBMU(ModbusControlBase):
    def bms_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'advanced':
            # 上下高壓控制指令:1:Power on, 2:power off
            if on_off:
                # 先重置錯誤，然後等20秒後在開
                self.client.write_single_register(501, 1)
                time.sleep(10)
                self.client.write_single_register(503, 1)
            else:
                self.client.write_single_register(503, 2)
        else:
            raise NotImplementedError

    def bms_fault_reset(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                # 0: Do not reset, 1: Reset
                self.client.write_single_register(501, 1)
        else:
            raise NotImplementedError

    def bms_air_on_off(self, on_off, eq_id=None):
        if self.customer and self.customer.lower() == 'advanced':
            # 空調遠端操作:0=OFF, 1=ON
            air_status = self.client.read_holding_registers(0)[0]
            binary_str = bin(air_status)[2:].zfill(4)
            air_a_state = binary_str[-1]
            air_b_state = binary_str[-2]

            if on_off:
                # air_on
                if str(eq_id).lower() == "air_a":
                    cmd = f'0b{air_b_state}{1}'
                    self.client.write_single_register(0, int(cmd, 2))
                elif str(eq_id).lower() == "air_b":
                    cmd = f'0b{1}{air_a_state}'
                    self.client.write_single_register(0, int(cmd, 2))
            else:
                # air_off
                if str(eq_id).lower() == "air_a":
                    cmd = f'0b{air_b_state}{0}'
                    self.client.write_single_register(0, int(cmd, 2))
                elif str(eq_id).lower() == "air_b":
                    cmd = f'0b{0}{air_a_state}'
                    self.client.write_single_register(0, int(cmd, 2))
        else:
            raise NotImplementedError

    def bms_fan_on_off(self, on_off, eq_id=None):
        if self.customer and self.customer.lower() == 'advanced':
            # 排風扇遠端操作:0=OFF, 1=ON
            fan_status = self.client.read_holding_registers(1)[0]
            binary_str = bin(fan_status)[2:].zfill(4)
            fan_a_state = binary_str[-1]
            fan_b_state = binary_str[-2]

            if on_off:
                # air_on
                if str(eq_id).lower() == "fan_a":
                    cmd = f'0b{fan_b_state}{1}'
                    self.client.write_single_register(1, int(cmd, 2))
                elif str(eq_id).lower() == "fan_b":
                    cmd = f'0b{1}{fan_a_state}'
                    self.client.write_single_register(1, int(cmd, 2))
            else:
                # air_off
                if str(eq_id).lower() == "fan_a":
                    cmd = f'0b{fan_b_state}{0}'
                    self.client.write_single_register(1, int(cmd, 2))
                elif str(eq_id).lower() == "fan_b":
                    cmd = f'0b{0}{fan_a_state}'
                    self.client.write_single_register(1, int(cmd, 2))
        else:
            raise NotImplementedError

    def bms_dc_switch_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                self.client.write_single_register(5, 2)
            else:
                self.client.write_single_register(5, 1)
        else:
            raise NotImplementedError


class HithiumBMU(ModbusControlBase):
    def bms_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'advanced':
            # 上下高壓控制指令:1:Power on, 2:power off
            if on_off:
                # 先重置錯誤，然後等20秒後在開
                self.client.write_single_register(501, 1)
                time.sleep(10)
                self.client.write_single_register(503, 1)
            else:
                self.client.write_single_register(503, 2)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            # 上下高壓控制指令:1:Power on, 2:power off
            if on_off:
                # 先重置錯誤，然後等20秒後在開
                self.client.write_single_register(501, 1)
                time.sleep(10)
                self.client.write_single_register(503, 1)
            else:
                self.client.write_single_register(503, 2)
        else:
            raise NotImplementedError

    def bms_fault_reset(self, on_off):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off:
                # 0: Do not reset, 1: Reset
                self.client.write_single_register(501, 1)
        elif self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                # 0: Do not reset, 1: Reset
                self.client.write_single_register(501, 1)
        else:
            raise NotImplementedError

    def dcp_on_off(self, on_off, address):
        if self.customer and self.customer.lower() == 'advanced':
            if on_off is True:
                # DCP 開啟前，先檢查電壓
                msg = self.client.read_coils(0, 3)
                dcp_1_on = msg[1]  # address 1
                dcp_2_on = msg[0]  # address 0

                if not dcp_1_on and not dcp_2_on:
                    pass  # 兩個都關閉，開一邊沒關係
                elif dcp_1_on or dcp_2_on:
                    if address == 1 and dcp_1_on is True:
                        return  # 開同一邊，不理會
                    elif address == 0 and dcp_2_on is True:
                        return  # 開同一邊，不理會
                    else:
                        # 開另一邊，要檢查電壓小於20V才開
                        keep_going = False
                        check_time = datetime.datetime.now()
                        while not keep_going:
                            dao = StorageFactory(config).get_dao_factory(using_db='filesystem').get_dao()
                            settings = FilesystemSettings(
                                target_name_list=f'lite_bmu_*', target_data=FolderType.Current, base_path=dao.base_path)
                            data: pd.DataFrame = dao.read(criteria=settings)
                            if not data.empty and 'voltage' in data.columns:
                                voltages = data['voltage'].dropna().to_list()
                                voltages.sort()

                                # 計算是否有任意兩筆之間差值超過 20
                                significant_diff = any(
                                    abs(voltages[i] - voltages[j]) > 20
                                    for i in range(len(voltages)) for j in range(i + 1, len(voltages))
                                )

                                if not significant_diff:
                                    keep_going = True

                            if (datetime.datetime.now() - check_time).total_seconds() > 30:
                                raise Exception("DCP電壓相差超過20V, 無法進行合併")
                            time.sleep(1)

            # DCO編號為1, 2, 3; 寫入位置為 0, 1, 2
            if on_off:
                self.client.write_single_coil(address, True)
            else:
                self.client.write_single_coil(address, False)
        else:
            raise NotImplementedError


class Adam6250MP(ModbusControlBase):
    def acb_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                self.client.write_single_coil(16, True)
                time.sleep(3)
                self.client.write_single_coil(16, False)
            else:
                self.client.write_single_coil(17, True)
                time.sleep(3)
                self.client.write_single_coil(17, False)
        else:
            raise NotImplementedError


class Adam6250Pump(ModbusControlBase):
    def pump_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                if equipment_id == 1:
                    self.client.write_single_coil(16, True)
                    time.sleep(3)
                    self.client.write_single_coil(16, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(18, True)
                    time.sleep(3)
                    self.client.write_single_coil(18, False)
            else:
                if equipment_id == 1:
                    self.client.write_single_coil(17, True)
                    time.sleep(3)
                    self.client.write_single_coil(17, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(19, True)
                    time.sleep(3)
                    self.client.write_single_coil(19, False)
        else:
            raise NotImplementedError


class Adam6250Sol(ModbusControlBase):
    def water_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                if equipment_id == 1:
                    self.client.write_single_coil(18, True)
                    time.sleep(3)
                    self.client.write_single_coil(18, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(22, True)
                    time.sleep(3)
                    self.client.write_single_coil(22, False)
            else:
                if equipment_id == 1:
                    self.client.write_single_coil(19, True)
                    time.sleep(3)
                    self.client.write_single_coil(19, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(23, True)
                    time.sleep(3)
                    self.client.write_single_coil(23, False)
        else:
            raise NotImplementedError

    def sol_on_off(self, on_off, equipment_id=None):
        if self.customer and self.customer.lower() == 'evergreen-yp':
            if on_off:
                if equipment_id == 1:
                    self.client.write_single_coil(16, True)
                    time.sleep(3)
                    self.client.write_single_coil(16, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(20, True)
                    time.sleep(3)
                    self.client.write_single_coil(20, False)
            else:
                if equipment_id == 1:
                    self.client.write_single_coil(17, True)
                    time.sleep(3)
                    self.client.write_single_coil(17, False)
                elif equipment_id == 2:
                    self.client.write_single_coil(21, True)
                    time.sleep(3)
                    self.client.write_single_coil(21, False)
        else:
            raise NotImplementedError


class BrandControl:
    def __init__(self, brand_name, client: ModbusClient, customer, equipment_id=None):
        self.brand_name = brand_name
        self.client = client
        self.customer = customer
        self.equipment_id = equipment_id

    def get_template(self, sequence=0) -> ModbusControlBase:
        if self.brand_name.lower() == "fimer":
            return FimerPCS(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "etica":
            return EticaBMU(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "prime_volt":
            return PrimeVolt(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "hithium":
            return HithiumBMU(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "solar_edge":
            return SolarEdge(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "adam-6250-mp":
            return Adam6250MP(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "adam-6250-pump":
            return Adam6250Pump(self.client, self.customer, self.equipment_id)

        elif self.brand_name.lower() == "adam-6250-sol":
            return Adam6250Sol(self.client, self.customer, self.equipment_id)

        else:
            raise Exception()


def convert_to_uint_16(value):
    if value == -1:
        return 65535
    elif value < 0:
        return 65536 + value
    else:
        return value


def convert_to_uint_32(value, byte_order: Endian):
    if byte_order == Endian.Big:
        msb_index = 0
        lsb_index = 1
    elif byte_order == Endian.Little:
        msb_index = 1
        lsb_index = 0
    else:
        raise NotImplementedError

    msb = (value >> (8 * msb_index)) & 0xFF
    lsb = (value >> (8 * lsb_index)) & 0xFF

    if byte_order == Endian.Big:
        uint_value = (msb << 8) | lsb
    else:
        uint_value = (lsb << 8) | msb

    return uint_value


def uint16_to_bf16(uint16_value):
    sign_bit = uint16_value >> 15
    exponent_bits = (uint16_value >> 7) & 0xFF
    fraction_bits = uint16_value & 0x7F
    bf16_value = (sign_bit << 15) | (exponent_bits << 7) | fraction_bits
    return bf16_value


"""""""""""""""""""""""""""""""""""""""
以下為為前端控制機器使用 IEC61850
"""""""""""""""""""""""""""""""""""""""


class IECControlBase:

    def __init__(self, client, customer, equipment_id=None):
        self.client = client
        self.customer = customer
        self.equipment_id = equipment_id
        ...

    def cb_on_off(self, on_off):
        ...


class ABBRef615(IECControlBase):
    def cb_on_off(self, on_off):
        if self.customer and self.customer.lower() == 'evergreen-yp':
            cb = {
                "open": "VCB_BESS_REF615CTRL/CBCSWI1.Pos.Oper.ctlVal",
                "close": "VCB_BESS_REF615CTRL/CBCSWI1.Pos.Oper.ctlVal"
            }
            if on_off:
                self.client.execute_control(cb["close"], 1)  # 閉合
            else:
                self.client.execute_control(cb["open"], 0)  # 切離
        else:
            raise NotImplementedError


class IECControl:
    def __init__(self, brand_name: str, client, customer, equipment_id=None):
        self.brand_name = brand_name
        self.client = client
        self.customer = customer
        self.equipment_id = equipment_id

    def get_template(self, sequence=0) -> IECControlBase:
        if self.brand_name.lower() == "abb_ref615":
            return ABBRef615(self.client, self.customer, self.equipment_id)

        else:
            raise Exception()

