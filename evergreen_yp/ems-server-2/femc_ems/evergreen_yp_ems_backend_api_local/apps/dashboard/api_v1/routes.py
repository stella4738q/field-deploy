# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###
from __future__ import absolute_import

from .api.bid_sbspm_chart import BidSbspmChart
from .api.bms_get_data_export import BmsGetDataExport
from .api.bms_get_data import BmsGetData
from .api.chart_history import ChartHistory
from .api.chart_history_sun import ChartHistorySun
from .api.chart_history_sun_db import ChartHistorySunDB
from .api.dashboard_sun import DashboardSun
from .api.dashboard_sun_db import DashboardSunDB
from .api.data_export_async import DataExportAsync
from .api.electric_schedule import ElectricSchedule
from .api.electric_schedule_detail import ElectricScheduleDetail
from .api.ems_essci import EMSEssci
from .api.iec61850_control import IEC61850Control
from .api.inverter_get_data import InverterGetData
from .api.meter_get_data import MeterGetData
from .api.meter_get_data_export import MeterGetDataExport
from .api.modbus_control import ModbusControl
from .api.modbus_emergency import ModbusEmergency
from .api.operation_mode import OperationMode
from .api.pcs_get_data import PCSGetData
from .api.pcs_get_data_export import PCSDataExport
from .api.alert_real_time import AlertRealTime
from .api.alert_historical import AlertHistorical
from .api.alert_historical_export import AlertHistoricalExport
from .api.permission_user import PermissionUser
from .api.permission_user_login import PermissionUserLogin
from .api.permission_user_reset import PermissionUserReset
from .api.permission_user_change_password import PermissionUserChangePassword
from .api.permission_role import PermissionRole
from .api.permission_user_role import PermissionUserRole
from .api.permission_menu_item import PermissionMenuItem
from .api.permission_user_field import PermissionUserField
from .api.permission_user_two_factor_auth import PermissionUserTwoFactorAuth
from .api.power_control_schedule import PowerControlSchedule
from .api.power_control_settings import PowerControlSettings
from .api.report_cabinet_chart_data import CabinetReportChartData
from .api.report_cabinet_data import CabinetReportData
from .api.system_demand import SystemDemand
from .api.system_download_template import SystemDownloadTemplate
from .api.system_dropdown import SystemDropdown
from .api.system_storage_setting import SystemStorageSetting
from .api.system_electric_setting import SystemElectricSetting
from .api.system_equipments import SystemEquipments
from .api.afc_monitor import AFCMonitor
from .api.afc_command import AFCCommand
from .api.afc_monitor_export import AFCMonitorExport
from .api.system_step_scenario import SystemStepScenario
from .api.fields import Fields
from .api.get_rack_trand_data import GetRackTrandData
from .api.get_rack_trand_data_export import GetRackTrandDataExport
from .api.taipower_holidays import TaipowerHolidays
from .api.get_notify_token import GETNotifytoken
from .api.get_notify_rule import GETNotifyrule
from .api.notify_setting import NotifySetting
from .api.get_notify_log import NotifyLog
from .api.get_femc_msg_token import GETFemcmsgToken
from .api.get_femc_msg_rule import GETFemcmsgRule
from .api.get_femc_msg_setting import GETFemcmsgSetting
from .api.get_femc_msg_log import GETFemcmsgLog
from .api.custom_protect_setting import CustomProtectSetting
from .api.permission_login_info import PermissionLoginInfo

routes = [
    dict(resource=Fields, urls=['/fields'], endpoint='fields'),
    dict(resource=AlertRealTime, urls=['/alert/real_time'], endpoint='alert_real_time'),
    dict(resource=AlertHistorical, urls=['/alert/historical'], endpoint='alert_historical'),
    dict(resource=AlertHistoricalExport, urls=['/alert/historical_export'], endpoint='alert_historical_export'),
    dict(resource=PermissionUser, urls=['/permission/user'], endpoint='permission_user'),
    dict(resource=PermissionUserLogin, urls=['/permission/user/login'], endpoint='permission_user_login'),
    dict(resource=PermissionUserReset, urls=['/permission/user/reset'], endpoint='permission_user_reset'),
    dict(resource=PermissionUserChangePassword, urls=['/permission/user/change_password'], endpoint='permission_user_change_password'),
    dict(resource=PermissionRole, urls=['/permission/role'], endpoint='permission_role'),
    dict(resource=PermissionUserRole, urls=['/permission/user/role'], endpoint='permission_user_role'),
    dict(resource=PermissionMenuItem, urls=['/permission/menu/item'], endpoint='permission_menu_item'),
    dict(resource=PermissionUserField, urls=['/permission/user/field'], endpoint='permission_user_field'),
    dict(resource=PermissionUserTwoFactorAuth, urls=['/permission/user_two_factor_auth'], endpoint='permission_user_two_factor_auth'),
    dict(resource=ModbusControl, urls=['/modbus/control'], endpoint='modbus_control'),
    dict(resource=IEC61850Control, urls=['/iec61850/control'], endpoint='iec61850_control'),
    dict(resource=ModbusEmergency, urls=['/modbus/emergency'], endpoint='modbus_emergency'),
    dict(resource=SystemStorageSetting, urls=['/system/storage_setting'], endpoint='system_storage_setting'),
    dict(resource=SystemElectricSetting, urls=['/system/electric_setting'], endpoint='system_electric_setting'),
    dict(resource=SystemEquipments, urls=['/system/equipments'], endpoint='system_resources'),
    dict(resource=EMSEssci, urls=['/ems/essci'], endpoint='ems_essci'),
    dict(resource=MeterGetData, urls=['/meter/get_data'], endpoint='meter_get_data'),
    dict(resource=MeterGetDataExport, urls=['/meter/get_data_export'], endpoint='meter_get_data_export'),
    dict(resource=BidSbspmChart, urls=['/bid/sbspm/chart'], endpoint='bid_sbspm_chart'),
    dict(resource=PCSGetData, urls=['/pcs/get_data'], endpoint='pcs_get_data'),
    dict(resource=PCSDataExport, urls=['/pcs/get_data_export'], endpoint='pcs_get_data_export'),
    dict(resource=BmsGetData, urls=['/bms/get_data'], endpoint='bms_get_data'),
    dict(resource=BmsGetDataExport, urls=['/bms/get_data_export'], endpoint='bms_get_data_export'),
    dict(resource=AFCMonitor, urls=['/afc/monitor'], endpoint='afc_monitor'),
    dict(resource=AFCCommand, urls=['/afc/command'], endpoint='afc_command'),
    dict(resource=AFCMonitorExport, urls=['/afc/monitor_export'], endpoint='afc_monitor_export'),
    dict(resource=SystemStepScenario, urls=['/system/step_scenario'], endpoint='system_step_scenario'),
    dict(resource=ElectricSchedule, urls=['/electric/schedule'], endpoint='electric_schedule'),
    dict(resource=ElectricScheduleDetail, urls=['/electric/schedule_detail'], endpoint='electric_schedule_detail'),
    dict(resource=PowerControlSchedule, urls=['/power_control/schedule'], endpoint='power_control_schedule'),
    dict(resource=GetRackTrandData, urls=['/get/rack_trand_data'], endpoint='get_rack_trand_data'),
    dict(resource=GetRackTrandDataExport, urls=['/get/rack_trand_data/export'], endpoint='get_rack_trand_data_export'),
    dict(resource=SystemDownloadTemplate, urls=['/system/download_template'], endpoint='system_download_template'),
    dict(resource=TaipowerHolidays, urls=['/taipower_holidays'], endpoint='taipower_holidays'),
    dict(resource=GETNotifytoken, urls=['/notify/token'], endpoint='notify_token'),
    dict(resource=GETNotifyrule, urls=['/notify/rule'], endpoint='notify_rule'),
    dict(resource=NotifySetting, urls=['/notify/setting'], endpoint='notify_setting'),
    dict(resource=NotifyLog, urls=['/notify/log'], endpoint='notify_log'),
    dict(resource=OperationMode, urls=['/operation_mode'], endpoint='operation_mode'),
    dict(resource=SystemDropdown, urls=['/system/dropdown'], endpoint='system_dropdown'),
    dict(resource=SystemDemand, urls=['/system/demand'], endpoint='system_demand'),
    dict(resource=DataExportAsync, urls=['/data/export_async'], endpoint='data_export_async'),
    dict(resource=PowerControlSettings, urls=['/power_control/settings'], endpoint='power_control_settings'),
    dict(resource=CabinetReportData, urls=['/report/cabinet_data'], endpoint='report_cabinet_data'),
    dict(resource=CabinetReportChartData, urls=['/report/cabinet_chart_data'], endpoint='report_cabinet_chart_data'),
    dict(resource=ChartHistory, urls=['/chart/history'], endpoint='chart_history'),
    dict(resource=ChartHistorySun, urls=['/chart/history_sun'], endpoint='chart_history_sun'),
    dict(resource=DashboardSun, urls=['/dashboard/sun'], endpoint='dashboard_sun'),
    dict(resource=InverterGetData, urls=['/inverter/get_data'], endpoint='inverter_get_data'),
    dict(resource=DashboardSunDB, urls=['/dashboard/sun_db'], endpoint='dashboard_sun_db'),
    dict(resource=ChartHistorySunDB, urls=['/chart/history_sun_db'], endpoint='chart_history_sun_db'),
    dict(resource=GETFemcmsgToken, urls=['/femc_msg/token'], endpoint='femc_msg_token'),
    dict(resource=GETFemcmsgRule, urls=['/femc_msg/rule'], endpoint='femc_msg_rule'),
    dict(resource=GETFemcmsgSetting, urls=['/femc_msg/setting'], endpoint='femc_msg_setting'),
    dict(resource=GETFemcmsgLog, urls=['/femc_msg/log'], endpoint='femc_msg_log'),
    dict(resource=CustomProtectSetting, urls=['/system/custom_protect'], endpoint='system_custom_protect'),
    dict(resource=PermissionLoginInfo, urls=['/permission/login_info'], endpoint='permission_login_info')
]
