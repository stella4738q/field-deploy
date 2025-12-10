import datetime
import numpy as np
import pandas as pd
from src.model.protect import BmsProtectParam, BmsProtect, ProtectItems
from src.utility.data_logger import WarningData, Alarm
from src.constants.config_const import ConfigSession, SettingConfigConst
from src.constants.foler_and_file_const import FolderAndFileConst
from src.utility.logger import MyLogger
from src.dao.mongodb_dao import MongoDBDao


class ATSCKS_Protection:
    def __init__(self, main_config: dict, device_name: str, sub_device_name: str, device_data: dict):
        myLogger = MyLogger(self.__class__.__name__, 'error')
        myLogger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = myLogger.get()

        self.main_config = main_config
        self.field_id = main_config.get(ConfigSession.SETTINGS.value).get(SettingConfigConst.FIELD_ID.value)
        self.device_name = device_name
        self.sub_device_name = sub_device_name
        self.device_data = device_data
        self.final_warning_list = []
        self.alarm_list = []
        self.temp_data = {}

        self.mongo_dao = MongoDBDao(main_config=self.main_config)

        self.bms_protect = BmsProtect()
        self.bms_protect_param = None


    def check_protection(self):
        """客製化設備告警檢查"""
        self.final_warning_list = []
        self.temp_data = {}

        try:
            match self.device_name:
                case 'PCS_1':
                    if 'active_fault' in self.device_data.keys():
                        active_fault = self.device_data.get('active_fault')
                        def active_fault_code(value):
                            message = None
                            if value == 11776:
                                message = 'Over current'
                            elif value == 11778:
                                message = 'Short circuit, cannot be reset'
                            elif value == 11781:
                                message = 'BU current difference'
                            elif value == 11785:
                                message = 'DC short circuit'
                            elif value == 15873:
                                message = 'Frt Grid Fault'
                            elif value == 15876:
                                message = 'DC link over voltage'
                            elif value == 15877:
                                message = 'DC link under voltage'
                            elif value == 15878:
                                message = 'BU DC link difference'
                            elif value == 15879:
                                message = 'BU voltage difference'
                            elif value == 15880:
                                message = 'LSU charging'
                            elif value == 15882:
                                message = 'LSU charging bus bar'
                            elif value == 15885:
                                message = 'Over voltage Fault'
                            elif value == 15886:
                                message = 'Under voltage fault'
                            elif value == 15888:
                                message = 'DC unbalance fault'
                            elif value == 19971:
                                message = 'Excess temperature'
                            elif value == 19972:
                                message = 'Excess temperature difference'
                            elif value == 19975:
                                message = 'Control board temperature'
                            elif value == 24067:
                                message = 'XSTO circuit open'
                            elif value == 24069:
                                message = 'Rating ID mismatch'
                            elif value == 24071:
                                message = 'PU communication'
                            elif value == 24072:
                                message = 'Power unit lost'
                            elif value == 24077:
                                message = 'PU communication configuration'
                            elif value == 24078:
                                message = 'Reduced run'
                            elif value == 24079:
                                message = 'PU state feedback'
                            elif value == 24082:
                                message = 'Bamu configuration'
                            elif value == 24084:
                                message = 'Measurement circuit temperature'
                            elif value == 24085:
                                message = 'Over temperature hw'
                            elif value == 28168:
                                message = 'Memory Unit Detached'
                            elif value == 28185:
                                message = 'Synchronization fault'
                            elif value == 28186:
                                message = 'Rating ID fault'
                            elif value == 28187:
                                message = 'Backup/Restore Timeout'
                            elif value == 28188:
                                message = 'Fast power off'
                            elif value == 32257:
                                message = 'Panel loss'
                            elif value == 32266:
                                message = 'Over frequency'
                            elif value == 32267:
                                message = 'FBA A communication'
                            elif value == 32268:
                                message = 'FBA B communication'
                            elif value == 36352:
                                message = 'Over voltage fault'
                            elif value == 36353:
                                message = 'Under voltage fault'
                            elif value == 36354:
                                message = 'Over frequency fault'
                            elif value == 36355:
                                message = 'Under frequency fault'
                            elif value == 36356:
                                message = 'Sliding over voltage fault'
                            elif value == 36357:
                                message = 'Rate of change of frequency fault'
                            elif value == 37121:
                                message = 'Over temperature'
                            elif value == 37123:
                                message = 'Excess humidity'
                            elif value == 37124:
                                message = 'Grounding current sudden change'
                            elif value == 37125:
                                message = 'Residual current'
                            elif value == 37126:
                                message = 'Grounding circuit over voltage'
                            elif value == 37127:
                                message = 'Insulation resistance'
                            elif value == 37128:
                                message = 'Reverse current'
                            elif value == 37129:
                                message = 'DC Over current'
                            elif value == 37130:
                                message = 'External fault 1'
                            elif value == 37131:
                                message = 'External fault 2'
                            elif value == 37132:
                                message = 'External fault 3'
                            elif value == 37137:
                                message = 'Module 1 main air channel fan fail'
                            elif value == 37138:
                                message = 'Module 2 main air channel fan fail'
                            elif value == 37141:
                                message = 'Module 1 LCL fan fail'
                            elif value == 37142:
                                message = 'Module 2 LCL fan fail'
                            elif value == 37145:
                                message = 'Fan status feedback M1'
                            elif value == 37146:
                                message = 'Fan status feedback M2'
                            elif value == 37149:
                                message = 'Temperature sensor fail'
                            elif value == 37150:
                                message = 'Test fault'
                            elif value == 37151:
                                message = 'Humidity sensor failure'
                            elif value == 37152:
                                message = 'AC contactor failed to open'
                            elif value == 37153:
                                message = 'AC contactor failed to close'
                            elif value == 37154:
                                message = 'Open AC contactor'
                            elif value == 37155:
                                message = 'Closed AC contactor'
                            elif value == 37156:
                                message = 'DC contactor opening'
                            elif value == 37157:
                                message = 'DC contactor closing'
                            elif value == 37158:
                                message = 'Open DC contactor'
                            elif value == 37159:
                                message = 'Closed DC contactor'
                            elif value == 37160:
                                message = 'DC switch open'
                            elif value == 37161:
                                message = 'MV transformer gas discharge fault'
                            elif value == 37162:
                                message = 'MV side phase lost fault'
                            elif value == 37163:
                                message = 'MV transformer overpressure fault'
                            elif value == 37164:
                                message = 'MV breaker opened fault'
                            elif value == 37165:
                                message = 'MV transformer vacuum fault'
                            elif value == 37166:
                                message = 'MV transformer low oil level fault'
                            elif value == 37167:
                                message = 'MV transformer temperature fault'
                            elif value == 37168:
                                message = 'Main circuit SPD'
                            elif value == 37169:
                                message = 'DC fuse'
                            elif value == 37170:
                                message = '48 V power supply'
                            elif value == 37171:
                                message = '48 V buffer'
                            elif value == 37172:
                                message = '24 V buffer'
                            elif value == 37173:
                                message = 'Aux circuit breaker'
                            elif value == 37174:
                                message = 'LCL pressure sensor'
                            elif value == 37175:
                                message = 'AC door'
                            elif value == 37176:
                                message = 'DC door'
                            elif value == 37177:
                                message = 'Smoke detector'
                            elif value == 37178:
                                message = 'LCL overheat'
                            elif value == 37179:
                                message = 'Not supported PLC HW configuration'
                            elif value == 37180:
                                message = 'AC switch open'
                            elif value == 37181:
                                message = 'AC switch closed'
                            elif value == 37184:
                                message = 'AC breaker tripped'
                            elif value == 37185:
                                message = 'AC breaker closing'
                            elif value == 37186:
                                message = 'AC breaker opening'
                            elif value == 37200:
                                message = 'Transfer trip'
                            elif value == 37201:
                                message = 'Shutdown'
                            elif value == 37202:
                                message = 'DC input current deviation'
                            elif value == 37203:
                                message = 'Blown DC input fuse'
                            elif value == 37204:
                                message = 'DC input current measurement faulty'
                            elif value == 37205:
                                message = 'MV Breaker opening'
                            elif value == 37206:
                                message = 'DC current measurement faulty'
                            elif value == 37207:
                                message = 'SCADA communication lost'
                            elif value == 37208:
                                message = 'SCADA communication timeout'
                            elif value == 37375:
                                message = 'Solar SW'
                            else:
                                if value != 0:
                                    message = ''

                            if message is not None:
                                self.set_warning_data(
                                    level=2,
                                    code=f'{self.device_name}_FAULT_{value}',
                                    name=f'{self.device_name}錯誤, 代碼: {value}, 說明: {message}'
                                )
                        active_fault_code(active_fault)
                                                
                    if 'igbt_temp_m1' in self.device_data.keys():
                        igbt_temp_m1 = self.device_data.get('igbt_temp_m1')
                        if 95 <= igbt_temp_m1 <= 105:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}_IGBT_TEMP_M1',
                                name=f'{self.device_name}_M1_IGBT溫度 >95度',
                            )
                        elif igbt_temp_m1 > 105:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_IGBT_TEMP_M1',
                                name=f'{self.device_name}_M1_IGBT溫度 >105度'
                            )

                    if 'ctrl_section_temp' in self.device_data.keys():
                        ctrl_section_temp = self.device_data.get('ctrl_section_temp')
                        if 87 <= ctrl_section_temp <= 97:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}_CTRL_SECTION_TEMP',
                                name=f'{self.device_name}_控制區段溫度 >97度',
                            )
                        elif ctrl_section_temp > 97:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_CTRL_SECTION_TEMP',
                                name=f'{self.device_name}_控制區段溫度 >97度'
                            )

                    if 'cabinet_temp_m1' in self.device_data.keys():
                        cabinet_temp_m1 = self.device_data.get('cabinet_temp_m1')
                        if 70 <= cabinet_temp_m1 <= 80:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}_CABINET_TEMP_M1',
                                name=f'{self.device_name}_M1儲能櫃溫度 >70度',
                            )
                        elif cabinet_temp_m1 > 80:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_CABINET_TEMP_M1',
                                name=f'{self.device_name}_M1儲能櫃溫度 >80度'
                            )

                    if 'lcl_section_temp_m1' in self.device_data.keys():
                        lcl_section_temp_m1 = self.device_data.get('lcl_section_temp_m1')
                        if 90 <= lcl_section_temp_m1 <= 100:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}_LCL_SECTION_TEMP_M1',
                                name=f'{self.device_name}_M1_LCL溫度 >90度',
                            )
                        elif lcl_section_temp_m1 > 100:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_LCL_SECTION_TEMP_M1',
                                name=f'{self.device_name}_M1_LCL溫度 >100度'
                            )

                    if 'humidity' in self.device_data.keys():
                        humidity = self.device_data.get('humidity')
                        if humidity >= 95:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_INVERTER_HUMIDITY',
                                name=f'{self.device_name}_逆變器濕度 >95%'
                            )

                    charge_energy_keys = {'kwh_energy_charged_to_battery', 'mwh_energy_charged_to_battery', 'gwh_energy_charged_to_battery'}
                    if charge_energy_keys.issubset(self.device_data.keys()):
                        kwh = self.device_data.get('kwh_energy_charged_to_battery')
                        mwh = self.device_data.get('mwh_energy_charged_to_battery')
                        gwh = self.device_data.get('gwh_energy_charged_to_battery')
                        self.temp_data['total_charge_capacity'] = kwh + mwh * 1000 + gwh * 1000000

                    discharge_energy_keys = {'kwh_energy_discharged_from_battery', 'mwh_energy_discharged_from_battery', 'gwh_energy_discharged_from_battery'}
                    if discharge_energy_keys.issubset(self.device_data.keys()):
                        kwh = self.device_data.get('kwh_energy_discharged_from_battery')
                        mwh = self.device_data.get('mwh_energy_discharged_from_battery')
                        gwh = self.device_data.get('gwh_energy_discharged_from_battery')
                        self.temp_data['total_discharge_capacity'] = kwh + mwh * 1000 + gwh * 1000000

                    if 'dc_input_current_m1' in self.device_data.keys():
                        dc_input_current_m1 = self.device_data.get('dc_input_current_m1')
                        self.temp_data['dc_current_avg'] = np.sum(dc_input_current_m1)

                    if 'inverter_main_status' in self.device_data.keys():
                        inverter_main_status = int(self.device_data.get('inverter_main_status'))
                        actions_tw = {
                            1: '準備開啟',
                            1 << 1: '故障',
                            1 << 2: '告警',
                            1 << 4: '電網穩定',
                            1 << 5: 'DC電壓正常啟動',
                            1 << 6: '禁止啟動',
                            1 << 7: '減少運轉',
                            1 << 10: '受限',
                            1 << 11: '併網',
                            1 << 12: '電池已連接'
                        }
                        rtn_list = []
                        for key, format_string in actions_tw.items():
                            if inverter_main_status & key:
                                rtn_list.append(format_string)
                                if key == 2:
                                    self.set_warning_data(2, f"{self.device_name}_INVERTER_FAULT", f"{self.device_name}_PCS故障")
                                elif key == 4:
                                    self.set_warning_data(1, f"{self.device_name}_INVERTER_WARNING", f"{self.device_name}_PCS告警")
                                elif key == 64:
                                    self.set_warning_data(2, f"{self.device_name}_INVERTER_START_INHIBITED", f"{self.device_name}_PCS啟動受限")
                                elif key == 1024:
                                    self.set_warning_data(1, f"{self.device_name}_INVERTER_POWER_LIMITED", f"{self.device_name}_PCS輸出功率受限")
                        self.temp_data['inverter_main_status'] = '/'.join(rtn_list)

                    if 'env_status' in self.device_data.keys():
                        env_status = int(self.device_data.get('env_status'))
                        if env_status & 2 == 1:
                            self.set_warning_data(1, f"{self.device_name}_OVER_TEMP", f"{self.device_name}_偵測到溫度過高")
                        if env_status & 4 == 1:
                            self.set_warning_data(1, f"{self.device_name}_COLD_TEMP", f"{self.device_name}_偵測到溫度過低")
                        if env_status & 8 == 1:
                            self.set_warning_data(1, f"{self.device_name}_EXCESS_HUMIDITY", f"{self.device_name}_偵測到濕度過高")
                        if env_status & 16 == 1:
                            self.set_warning_data(0, f"{self.device_name}_CABINET_HEATING_ON", f"{self.device_name}_櫥櫃加熱啟動")
                        if env_status & 32 == 1:
                            self.set_warning_data(1, f"{self.device_name}_HOT_AMBIENT_TEMP", f"{self.device_name}_超過最高環境溫度")
                        if env_status & 64 == 1:
                            self.set_warning_data(1, f"{self.device_name}_COLD_POWER_TEMP", f"{self.device_name}_冷功率溫度已降低")
                        if env_status & 128 == 0:
                            self.set_warning_data(1, f"{self.device_name}_SMOKE_DETECTOR_STATUS", f"{self.device_name}_煙霧偵測器狀態非啟動")

                    if 'inverter_inhibits_1' in self.device_data.keys():
                        inverter_inhibits_1 = int(self.device_data.get('inverter_inhibits_1'))
                        if inverter_inhibits_1 & 1 == 1:
                            self.set_warning_data(2, f"{self.device_name}_OPERATION_DISABLED", f"{self.device_name}_操作停用")
                        if inverter_inhibits_1 & 2 == 1:
                            self.set_warning_data(2, f"{self.device_name}_EXTERNAL_STOP_SIGNAL", f"{self.device_name}_外部停止訊號")
                        if inverter_inhibits_1 & 4 == 1:
                            self.set_warning_data(2, f"{self.device_name}_SYSTEM_FAULT", f"{self.device_name}_錯誤")
                        if inverter_inhibits_1 & 8 == 1:
                            self.set_warning_data(0, f"{self.device_name}_CONFIGURATION_NOT_COMPLETE", f"{self.device_name}_配置未完成")
                        if inverter_inhibits_1 & 16 == 1:
                            self.set_warning_data(1, f"{self.device_name}_LOW_AMBIENT_TEMPERATURE", f"{self.device_name}_環境溫度過低")
                        if inverter_inhibits_1 & 32 == 1:
                            self.set_warning_data(1, f"{self.device_name}_LOW_POWER_SECTION_TEMPERATURE", f"{self.device_name}_功率部分溫度過低")
                        if inverter_inhibits_1 & 64 == 1:
                            self.set_warning_data(1, f"{self.device_name}_HIGH_AMBIENT_TEMPERATURE", f"{self.device_name}_環境溫度過高")
                        if inverter_inhibits_1 & 128 == 1:
                            self.set_warning_data(1, f"{self.device_name}_EXCESS_HUMIDITY", f"{self.device_name}_濕度過高")
                        if inverter_inhibits_1 & 256 == 1:
                            self.set_warning_data(2, f"{self.device_name}_PLC_LINK_LOST", f"{self.device_name}_PLC連結失敗")
                        if inverter_inhibits_1 & 16384 == 1:
                            self.set_warning_data(0, f"{self.device_name}_GRID_UNSTABLE", f"{self.device_name}_電網不穩定")
                        if inverter_inhibits_1 & 32768 == 1:
                            self.set_warning_data(0, f"{self.device_name}_GRID_DELAY", f"{self.device_name}_電網延遲")

                    if 'inverter_inhibits_2' in self.device_data.keys():
                        inverter_inhibits_2 = int(self.device_data.get('inverter_inhibits_2'))
                        if inverter_inhibits_2 & 4 == 1:
                            self.set_warning_data(0, f"{self.device_name}_OPEN_DOOR", f"{self.device_name}_門禁開啟")
                        if inverter_inhibits_2 & 8 == 1:
                            self.set_warning_data(1, f"{self.device_name}_POWER_MODULE_NOT_READY", f"{self.device_name}_功率模組未就緒")
                        if inverter_inhibits_2 & 16 == 1:
                            self.set_warning_data(1, f"{self.device_name}_LOW_INPUT_VOLTAGE", f"{self.device_name}_輸入電壓過低")
                        if inverter_inhibits_2 & 32 == 1:
                            self.set_warning_data(1, f"{self.device_name}_HIGH_INPUT_VOLTAGE", f"{self.device_name}_輸入電壓過高")
                        if inverter_inhibits_2 & 128 == 1:
                            self.set_warning_data(2, f"{self.device_name}_GROUNDING_FAULT", f"{self.device_name}_接地異常")
                        if inverter_inhibits_2 & 256 == 1:
                            self.set_warning_data(2, f"{self.device_name}_INSULATION_RESISTANCE_FAULT", f"{self.device_name}_絕緣阻抗異常")
                        if inverter_inhibits_2 & 512 == 1:
                            self.set_warning_data(1, f"{self.device_name}_AC_DISCONNECTION_DEVICE_OPEN", f"{self.device_name}_交流斷開裝置打開")

                case "DCU_1":
                    ...

                case 'TR':
                    if 'temperature' in self.device_data.keys():
                        alarm_temp = 105
                        warn_temp = 95
                        if warn_temp <= self.device_data.get('temperature') < alarm_temp:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}_OVER_TEMP',
                                name=f'{self.device_name}_油溫大於：{warn_temp}°C，請注意'
                            )
                        elif self.device_data.get('temperature') >= alarm_temp:
                            self.set_warning_data(
                                level=2,
                                code=f'{self.device_name}_OVER_TEMP',
                                name=f'{self.device_name}_油溫大於：{alarm_temp}°C，嚴重異常'
                            )
                            
                case 'VDF_1':
                    if 'status' in self.device_data.keys():
                        status = self.device_data.get('status')
                        running_status = str.split(status,':')[1].replace(' ','') # 去除空格
                        is_running =  True if running_status == '運轉中' else False 
                        self.temp_data['is_running'] = is_running
                
                case 'BMU_1':
                    if self.sub_device_name != "":
                        # 更新 BMS 保護參數及是否啟用客製化保護
                        self.update_custom_protect_status()

                        if self.use_custom_protect:
                            # 電芯欠壓
                            if 'min_cell_voltage' in self.device_data.keys():
                                min_cell_voltage = self.device_data.get('min_cell_voltage')
                                if min_cell_voltage <= self.bms_protect_param.cell_volt_min_l2:
                                    self.set_warning_data(
                                        level=2,
                                        code=f'{self.sub_device_name}_CELL_UNDER_VOLT_SERIOUS',
                                        name=f'{self.sub_device_name}_電芯欠壓_嚴重'
                                    )
                                elif self.bms_protect_param.cell_volt_min_l2 < min_cell_voltage <= self.bms_protect_param.cell_volt_min_l1:
                                    self.set_warning_data(
                                        level=1,
                                        code=f'{self.sub_device_name}_CELL_UNDER_VOLT_MEDIUM',
                                        name=f'{self.sub_device_name}_電芯欠壓_中度'
                                    )
                                elif self.bms_protect_param.cell_volt_min_l1 < min_cell_voltage <= self.bms_protect_param.cell_volt_min_l0:
                                    self.set_warning_data(
                                        level=0,
                                        code=f'{self.sub_device_name}_CELL_UNDER_VOLT_SLIGHT',
                                        name=f'{self.sub_device_name}_電芯欠壓_輕微'
                                    )

                            # 電芯過壓
                            if 'max_cell_voltage' in self.device_data.keys():
                                max_cell_voltage = self.device_data.get('max_cell_voltage')
                                if self.bms_protect_param.cell_volt_max_l2 <= max_cell_voltage:
                                    self.set_warning_data(
                                        level=2,
                                        code=f'{self.sub_device_name}_CELL_OVER_VOLT_SERIOUS',
                                    name=f'{self.sub_device_name}_電芯過壓_嚴重'
                                )
                                elif self.bms_protect_param.cell_volt_max_l1 <= max_cell_voltage < self.bms_protect_param.cell_volt_max_l2:
                                    self.set_warning_data(
                                        level=1,
                                        code=f'{self.sub_device_name}_CELL_OVER_VOLT_MEDIUM',
                                        name=f'{self.sub_device_name}_電芯過壓_中度'
                                    )
                                elif self.bms_protect_param.cell_volt_max_l0 <= max_cell_voltage < self.bms_protect_param.cell_volt_max_l1:
                                    self.set_warning_data(
                                        level=0,
                                        code=f'{self.sub_device_name}_CELL_OVER_VOLT_SLIGHT',
                                        name=f'{self.sub_device_name}_電芯過壓_輕微'
                                    )

                            # Rack過流
                            if 'current' in self.device_data.keys():
                                current = abs(self.device_data.get('current'))
                                if current >= self.bms_protect_param.current_max_l2:
                                    self.set_warning_data(
                                        level=2,
                                        code=f'{self.sub_device_name}_OVER_CURRENT_SERIOUS',
                                        name=f'{self.sub_device_name}_過流_嚴重'
                                    )
                                elif self.bms_protect_param.current_max_l1 <= current < self.bms_protect_param.current_max_l2:
                                    self.set_warning_data(
                                        level=1,
                                        code=f'{self.sub_device_name}_OVER_CURRENT_MEDIUM',
                                        name=f'{self.sub_device_name}_過流_中度'
                                    )
                                elif self.bms_protect_param.current_max_l0 <= current < self.bms_protect_param.current_max_l1:
                                    self.set_warning_data(
                                        level=0,
                                        code=f'{self.sub_device_name}_OVER_CURRENT_SLIGHT',
                                        name=f'{self.sub_device_name}_過流_輕微'
                                    )

                            # 電芯過溫
                            if 'max_cell_temperature' in self.device_data.keys():
                                max_cell_temperature = self.device_data.get('max_cell_temperature')
                                if max_cell_temperature >= self.bms_protect_param.cell_temp_max_l2:
                                    self.set_warning_data(
                                        level=2,
                                        code=f'{self.sub_device_name}_CELL_OVER_TEMP_SERIOUS',
                                        name=f'{self.sub_device_name}_電芯高溫_嚴重'
                                    )
                                elif self.bms_protect_param.cell_temp_max_l1 <= max_cell_temperature < self.bms_protect_param.cell_temp_max_l2:
                                    self.set_warning_data(
                                        level=1,
                                        code=f'{self.sub_device_name}_CELL_OVER_TEMP_MEDIUM',
                                        name=f'{self.sub_device_name}_電芯高溫_中度'
                                    )
                                elif self.bms_protect_param.cell_temp_max_l0 <= max_cell_temperature < self.bms_protect_param.cell_temp_max_l1:
                                    self.set_warning_data(
                                        level=0,
                                        code=f'{self.sub_device_name}_CELL_OVER_TEMP_SLIGHT',
                                        name=f'{self.sub_device_name}_電芯高溫_輕微'
                                    )

                            # 電芯低溫
                            if 'min_cell_temperature' in self.device_data.keys():
                                min_cell_temperature = self.device_data.get('min_cell_temperature')
                                if min_cell_temperature <= self.bms_protect_param.cell_temp_min_l2:
                                    self.set_warning_data(
                                        level=2,
                                        code=f'{self.sub_device_name}_CELL_LOW_TEMP_SERIOUS',
                                        name=f'{self.sub_device_name}_電芯低溫_嚴重'
                                    )
                                elif self.bms_protect_param.cell_temp_min_l1 >= min_cell_temperature > self.bms_protect_param.cell_temp_min_l2:
                                    self.set_warning_data(
                                        level=1,
                                        code=f'{self.sub_device_name}_CELL_LOW_TEMP_MEDIUM',
                                        name=f'{self.sub_device_name}_電芯低溫_中度'
                                    )
                                elif self.bms_protect_param.cell_temp_min_l0 >= min_cell_temperature > self.bms_protect_param.cell_temp_min_l1:
                                    self.set_warning_data(
                                        level=0,
                                        code=f'{self.sub_device_name}_CELL_LOW_TEMP_SLIGHT',
                                        name=f'{self.sub_device_name}_電芯低溫_輕微'
                                    )
                
                case 'UPS':   
                    alarm_soc = 30.0
                    alarm_temp = 65.0
                    if 'input_voltage' in self.device_data.keys() and 'input_freq' in self.device_data.keys() and 'soc' in self.device_data.keys() :
                        if ((self.device_data.get('input_voltage') == 0 or self.device_data.get('input_freq') == 0) and self.device_data.get('soc') <= alarm_soc):
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}電量不足',
                                name=f'{self.device_name}電量低於{alarm_soc}%, 請注意電源是否中斷'
                            )
                    if 'temp' in self.device_data.keys():
                        if self.device_data.get('temp') > alarm_temp:
                            self.set_warning_data(
                                level=1,
                                code=f'{self.device_name}溫度過高',
                                name=f'{self.device_name}溫度過高({self.device_data.get("temp")}), 請確認是否異常'
                            )
                
                case default:
                    self.logger.warning(f"Device {self.device_name} does not have custom protection checks implemented.")
            
            if len(self.final_warning_list) > 0:
                self.temp_data['warning'] = self.final_warning_list

            return self.temp_data
        except Exception as e:
            self.logger.error(f"ATSCKS check protect error: {e}")
            return self.temp_data

    
    def update_custom_protect_status(self):
        """更新客製化保護參數及是否啟用客製化保護"""
        # 讀取是否啟用客製化告警用於VPC
        self.bms_protect_param = BmsProtectParam()

        cursor = self.mongo_dao.find_many('system_settings', query={'key': 'custom_protect'})
        df = pd.DataFrame(list(cursor))
        if not df.empty:
            self.use_custom_protect = df.iloc[0]['value']
        else:
            self.use_custom_protect = False

        if self.use_custom_protect:
            cursor = self.mongo_dao.find_many(collection_name='custom_protect', query={})
            df = pd.DataFrame(list(cursor))
            if not df.empty:
                for idx, row in df.iterrows():
                    key = row['key']
                    value = row['value']
                    try:
                        if key in self.bms_protect_param.__dict__.keys():
                            self.bms_protect_param.__setattr__(key, value)
                    except AttributeError:
                        self.logger.warning(f"BmsProtectParam 沒有屬性: '{key}'")


    def set_warning_data(self, level: int, code: str, name: str):
        """
        設置警告數據
        """
        warningData = WarningData(
            level=level,
            code=code,
            name=name,
            start_time=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8))
        )
        self.final_warning_list.append(warningData.encode())



