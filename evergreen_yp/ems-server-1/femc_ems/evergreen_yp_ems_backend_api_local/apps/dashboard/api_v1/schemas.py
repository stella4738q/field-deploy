# -*- coding: utf-8 -*-
import copy
import six
from jsonschema import RefResolver


class RefNode(object):

    def __init__(self, data, ref):
        self.ref = ref
        self._data = data

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        return self._data.__setitem__(key, value)

    def __getattr__(self, key):
        return self._data.__getattribute__(key)

    def __iter__(self):
        return self._data.__iter__()

    def __repr__(self):
        return repr({'$ref': self.ref})

    def __eq__(self, other):
        if isinstance(other, RefNode):
            return self._data == other._data and self.ref == other.ref
        elif six.PY2:
            return object.__eq__(other)
        elif six.PY3:
            return object.__eq__(self, other)
        else:
            return False

    def __deepcopy__(self, memo):
        return RefNode(copy.deepcopy(self._data), self.ref)

    def copy(self):
        return RefNode(self._data, self.ref)

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###

base_path = '/api/v1'

definitions = {'definitions': {}, 'parameters': {}}

validators = {
    ('fields', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('fields', 'DELETE'): {'args': {'required': [], 'properties': {'uid': {'schema': {'type': 'string'}}}}},
    ('quality_sbspm', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'equipment_id': {'schema': {'type': 'string'}}, 'datetime': {'schema': {'type': 'string'}}, 'n_data': {'schema': {'type': 'integer'}}}}},
    ('system_bid_winning', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'datetime': {'schema': {'type': 'string'}}}}},
    ('system_bid_winning_curve', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'datetime': {'schema': {'type': 'string'}}}}},
    ('system_bid_amount', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}}}},
    ('system_scheduling_balanced', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'bid_id': {'schema': {'type': 'string'}}, 'equipment_id': {'schema': {'type': 'string'}}, 'datetime': {'schema': {'type': 'integer'}}, 'order': {'schema': {'type': 'integer'}}}}},
    ('alert_historical', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'equipment_id': {'schema': {'type': 'string'}}, 'level': {'schema': {'type': 'string'}}, 'start_time': {'schema': {'type': 'string'}}, 'end_time': {'schema': {'type': 'string'}}, 'order_field': {'schema': {'type': 'string'}}, 'order_type': {'schema': {'type': 'string'}}, 'limit': {'$ref': '#/components/parameters/PageLimit'}, 'page': {'$ref': '#/components/parameters/PageOffset'}}}},
    ('alert_historical_export', 'GET'): {'args': {'required': ['field_id'], 'properties': {'field_id': {'schema': {'type': 'string'}}, 'equipment_id': {'schema': {'type': 'string'}}, 'level': {'schema': {'type': 'string'}}, 'start_time': {'schema': {'type': 'string'}}, 'end_time': {'schema': {'type': 'string'}}}}},
    ('permission_user', 'GET'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}, 'name': {'schema': {'type': 'string'}}, 'email': {'schema': {'type': 'string'}}, 'mobile': {'schema': {'type': 'string'}}, 'is_admin': {'schema': {'type': 'string'}}, 'account': {'schema': {'type': 'string'}}, 'enable': {'schema': {'type': 'string'}}}}},
    ('permission_user', 'DELETE'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}}}},
    ('permission_user_field', 'GET'): {'args': {'required': [], 'properties': {'user_id': {'schema': {'type': 'string'}}}}},
    ('permission_user_field', 'DELETE'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}}}},
    ('permission_role', 'GET'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}, 'name': {'schema': {'type': 'string'}}, 'enable': {'schema': {'type': 'string'}}}}},
    ('permission_role', 'DELETE'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}}}},
    ('permission_user_role', 'GET'): {'args': {'required': [], 'properties': {'user_id': {'schema': {'type': 'string'}}}}},
    ('permission_user_role', 'DELETE'): {'args': {'required': [], 'properties': {'id': {'schema': {'type': 'string'}}}}},
    ('permission_user_role_by_role_id', 'DELETE'): {'args': {'required': [], 'properties': {'role_id': {'schema': {'type': 'string'}}}}},
    ('permission_menu_item', 'GET'): {'args': {'required': [], 'properties': {}}},
    ('geo_location', 'GET'): {'args': {'required': [], 'properties': {'address': {'schema': {'type': 'string'}}}}},
    ('modbus_access_data', 'GET'): {'args': {'required': [], 'properties': {'type': {'schema': {'type': 'string'}}}}},
    ('modbus_control', 'POST'): {'args': {'required': [], 'properties': {'type': {'schema': {'type': 'string'}}}}},
    ('iec61850_control', 'POST'): {'args': {'required': [], 'properties': {'type': {'schema': {'type': 'string'}}}}},
    ('modbus_emergency', 'POST'): {'args': {'required': [], 'properties': {'type': {'schema': {'type': 'string'}}}}},
    ('modbus_control_check', 'GET'): {'args': {'required': [], 'properties': {'type': {'schema': {'type': 'string'}}}}},
    ('system_step_scenario', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('system_step_scenario', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('system_step_scenario', 'DELETE'): {'args': {'required': [], 'properties': {'case_id': {'schema': {'type': 'string'}}}}},
    ('system_equipments', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('system_equipments', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('system_equipments', 'DELETE'): {'args': {'required': [], 'properties': {'case_id': {'schema': {'type': 'string'}}}}},
    ('system_equipments_download', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_equipments_download_example', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_equipments_upload', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_scenario_schedule', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('system_scenario_schedule', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('system_scenario_schedule', 'DELETE'): {'args': {'required': [], 'properties': {'case_id': {'schema': {'type': 'string'}}}}},
    ('afc_monitor', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('afc_command', 'GET'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('afc_command', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('afc_monitor_export', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('system_step_scenario_export', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('bms_get_data', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('pcs_get_data', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('pcs_get_data_export', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('get_rack_trand_data', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('get_rack_trand_data_export', 'POST'): {'args': {'required': [], 'properties': {'date': {'schema': {'type': 'string'}}}}},
    ('notify_token', 'GET'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}},'name': {'schema': {'type': 'string'}},'token': {'schema': {'type': 'string'}}}}},
    ('notify_token', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('notify_rule', 'GET'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}},'name': {'schema': {'type': 'string'}},'notify_code': {'schema': {'type': 'string'}},'description': {'schema': {'type': 'string'}},'notify_type': {'schema': {'type': 'string'}},'afc': {'schema': {'type': 'string'}},'dip_sup': {'schema': {'type': 'string'}},'edreg': {'schema': {'type': 'string'}}, 'solar': {'schema': {'type': 'string'}}, 'optimization': {'schema': {'type': 'string'}}}}},
    ('notify_rule', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('notify_by_case_id', 'GET'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('notify_by_case_id', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('notify_setting', 'GET'): {'args': {'required': [], 'properties': {'case_id': {'schema': {'type': 'string'}}}}},
    ('notify_setting', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('notify_log', 'GET'): {'args': {'required': [], 'properties': {'datetime': {'schema': {'type': 'string'}},'start_date': {'schema': {'type': 'string'}},'end_date': {'schema': {'type': 'string'}},'case_name': {'schema': {'type': 'string'}},'rule_name': {'schema': {'type': 'string'}},'token_name': {'schema': {'type': 'string'}}, 'rule_id': {'schema': {'type': 'string'}},'token_id': {'schema': {'type': 'string'}},'case_id': {'schema': {'type': 'string'}},'success': {'schema': {'type': 'string'}}}}},
    ('femc_msg_token', 'GET'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}, 'name': {'schema': {'type': 'string'}}, 'token': {'schema': {'type': 'string'}}}}},
    ('femc_msg_token', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('femc_msg_rule', 'GET'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}, 'name': {'schema': {'type': 'string'}}, 'notify_code': {'schema': {'type': 'string'}}, 'description': {'schema': {'type': 'string'}}, 'notify_type': {'schema': {'type': 'string'}}, 'afc': {'schema': {'type': 'string'}}, 'dip_sup': {'schema': {'type': 'string'}}, 'edreg': {'schema': {'type': 'string'}}, 'solar': {'schema': {'type': 'string'}}, 'optimization': {'schema': {'type': 'string'}}}}},
    ('femc_msg_rule', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('femc_msg_setting', 'GET'): {'args': {'required': [], 'properties': {'case_id': {'schema': {'type': 'string'}}}}},
    ('femc_msg_setting', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}},
    ('femc_msg_log', 'GET'): {'args': {'required': [], 'properties': {'datetime': {'schema': {'type': 'string'}}, 'start_date': {'schema': {'type': 'string'}}, 'end_date': {'schema': {'type': 'string'}}, 'case_name': {'schema': {'type': 'string'}}, 'rule_name': {'schema': {'type': 'string'}}, 'token_name': {'schema': {'type': 'string'}}, 'rule_id': {'schema': {'type': 'string'}}, 'token_id': {'schema': {'type': 'string'}}, 'case_id': {'schema': {'type': 'string'}}, 'success': {'schema': {'type': 'string'}}}}},
    ('permission_login_info', 'GET'): {'args': {'required': [], 'properties': {'name': {'schema': {'type': 'string'}}}}},
    ('permission_login_info', 'DELETE'): {'args': {'required': [], 'properties': {'_id': {'schema': {'type': 'string'}}}}}
}

filters = {
    ('fields', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('fields', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('fields', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('quality_sbspm', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('alert_real_time', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('alert_historical', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('alert_historical', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('alert_historical_export', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_login', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_reset', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_change_password', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_field', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_field', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_field', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_role', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_role', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_role', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_role', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_role', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_role', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_role_by_role_id', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_menu_item', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_user_two_factor_auth', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('geo_location', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('modbus_access_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('modbus_access_data', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_storage_setting', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_storage_setting', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_electric_setting', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_electric_setting', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_electric_operation_report', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_step_scenario', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_step_scenario', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_step_scenario', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_scenario_schedule', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('afc_monitor', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('afc_monitor', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('afc_command', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('afc_command', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('afc_monitor_export', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_step_scenario_export', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('ems_essci', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('meter_get_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('meter_get_data_export', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('modbus_emergency', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('pcs_get_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('pcs_get_data_export', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('pcs_get_data_export', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('get_rack_trand_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('get_rack_trand_data_export', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_token', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_token', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_token', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_rule', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_rule', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_rule', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_setting', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_setting', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_setting', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('notify_log', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('operation_mode', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_dropdown', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('bms_get_data_export', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('bms_get_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_demand', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('data_export_async', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('data_export_async', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('power_control_settings', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('power_control_settings', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('report_cabinet_data', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('report_cabinet_data', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('report_cabinet_chart_data', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('chart_history', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('chart_history_sun', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('dashboard_sun', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('inverter_get_data', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('dashboard_sun_db', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('chart_history_sun_db', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_token', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_token', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_token', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_rule', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_rule', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_rule', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_setting', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_setting', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_setting', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('femc_msg_log', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_custom_protect', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('system_custom_protect', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_login_info', 'GET'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('permission_login_info', 'DELETE'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
    ('iec61850_control', 'POST'): {200: {'headers': None, 'schema': None}, 400: {'headers': None, 'schema': None}},
}

scopes = {
}

resolver = RefResolver.from_schema(definitions)

class Security(object):

    def __init__(self):
        super(Security, self).__init__()
        self._loader = lambda: []

    @property
    def scopes(self):
        return self._loader()

    def scopes_loader(self, func):
        self._loader = func
        return func

security = Security()


def merge_default(schema, value, get_first=True, resolver=None):
    type_defaults = {
        'integer': 9573,
        'string': 'something',
        'object': {},
        'array': [],
        'boolean': False
    }

    results = normalize(schema, value, type_defaults, resolver=resolver)
    if get_first:
        return results[0]
    return results


def normalize(schema, data, required_defaults=None, resolver=None):
    if required_defaults is None:
        required_defaults = {}
    errors = []

    class DataWrapper(object):

        def __init__(self, data):
            super(DataWrapper, self).__init__()
            self.data = data

        def get(self, key, default=None):
            if isinstance(self.data, dict):
                return self.data.get(key, default)
            return getattr(self.data, key, default)

        def has(self, key):
            if isinstance(self.data, dict):
                return key in self.data
            return hasattr(self.data, key)

        def keys(self):
            if isinstance(self.data, dict):
                return list(self.data.keys())
            return list(getattr(self.data, '__dict__', {}).keys())

        def get_check(self, key, default=None):
            if isinstance(self.data, dict):
                value = self.data.get(key, default)
                has_key = key in self.data
            else:
                try:
                    value = getattr(self.data, key)
                except AttributeError:
                    value = default
                    has_key = False
                else:
                    has_key = True
            return value, has_key

    def _merge_dict(src, dst):
        for k, v in six.iteritems(dst):
            if isinstance(src, dict):
                if isinstance(v, dict):
                    r = _merge_dict(src.get(k, {}), v)
                    src[k] = r
                else:
                    src[k] = v
            else:
                src = {k: v}
        return src

    def _normalize_dict(schema, data):
        result = {}
        if not isinstance(data, DataWrapper):
            data = DataWrapper(data)

        _schema = schema.get('properties')
        if _schema is None:
            _keys = list(data.data.keys())
            _properties = dict()
            for k in _keys:
                if type(data.data[k]) is dict:
                    _properties[k] = dict(type='object')
                elif type(data.data[k]) is str:
                    _properties[k] = dict(type='string')
                elif type(data.data[k]) is list:
                    _properties[k] = dict(type='array')
                else:
                    _properties[k] = dict(type='default')
            schema['properties'] = _properties

        for _schema in schema.get('allOf', []):
            rs_component = _normalize(_schema, data)
            _merge_dict(result, rs_component)

        for key, _schema in six.iteritems(schema.get('properties', {})):
            # set default
            type_ = _schema.get('type', 'object')

            # get value
            value, has_key = data.get_check(key)
            if has_key or '$ref' in _schema:
                result[key] = _normalize(_schema, value)
            elif 'default' in _schema:
                result[key] = _schema['default']
            elif key in schema.get('required', []):
                if type_ in required_defaults:
                    result[key] = required_defaults[type_]
                else:
                    errors.append(dict(name='property_missing',
                                       message='`%s` is required' % key))

        additional_properties_schema = schema.get('additionalProperties', False)
        if additional_properties_schema is not False:
            aproperties_set = set(data.keys()) - set(result.keys())
            for pro in aproperties_set:
                result[pro] = _normalize(additional_properties_schema, data.get(pro))

        return result

    def _normalize_list(schema, data):
        result = []
        if hasattr(data, '__iter__') and not isinstance(data, (dict, RefNode)):
            for item in data:
                result.append(_normalize(schema.get('items'), item))
        elif 'default' in schema:
            result = schema['default']
        return result

    def _normalize_default(schema, data):
        if data is None:
            return schema.get('default')
        else:
            return data

    def _normalize_ref(schema, data):
        if resolver == None:
            raise TypeError("resolver must be provided")
        ref = schema.get(u"$ref")
        scope, resolved = resolver.resolve(ref)
        if resolved.get('nullable', False) and not data:
            return {}
        return _normalize(resolved, data)

    def _normalize(schema, data):
        if schema is True or schema == {}:
            return data
        if not schema:
            return None
        funcs = {
            'object': _normalize_dict,
            'array': _normalize_list,
            'default': _normalize_default,
            'ref': _normalize_ref
        }
        type_ = schema.get('type', 'object')
        if type_ not in funcs:
            type_ = 'default'
        if schema.get(u'$ref', None):
            type_ = 'ref'

        return funcs[type_](schema, data)

    return _normalize(schema, data), errors
