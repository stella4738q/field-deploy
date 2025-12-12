# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import datetime

from flask import request, session, make_response, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, ConfigConstant, PermissionConst, SUCCESS_MESSAGE
from apps.dashboard.utils import FeatureFunc
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class SystemElectricSetting(Resource):
    """
    用電大戶，電價設定:
    從雲端設定後同步下來，因此不做Create，只做 set 動作
    """
    logger = Logger().create('Local EMS API - system electricity price', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def get(self):
        def get_use_name(row):
            rtn_name = ''
            if row['is_set']:
                _data = row['data']
                current = next((item for item in _data if item['is_set'] == 1), None)
                if current:
                    rtn_name = f"{current['volt_type']}-{current['time_step']}"
            return rtn_name

        def get_week_holidays_dates():
            result_list = []
            today = datetime.datetime.today()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            # 取休假日
            current_year = self.dao.get_taipower_holidays(datetime.datetime.today().year)
            if not current_year.empty:
                holidays = current_year.iloc[0]['holidays']
                for i in range(7):
                    if (start_of_week + datetime.timedelta(days=i)).strftime('%Y-%m-%d') in holidays:
                        result_list.append(i+1)
            return result_list

        self.logger.info('[get] SystemElectricityPrice')
        message = SUCCESS_MESSAGE
        data = None
        try:
            _id = request.args.get(ApiConst.ID_.value, None)
            is_set = request.args.get(ApiConst.IS_SET.value, None)
            pd_data = self.dao.get_electricity_price(_id=_id)
            if not pd_data.empty and ApiConst.DATA.value in pd_data.columns:
                # 添加目前使用中的名稱
                pd_data['use_name'] = pd_data.apply(get_use_name, axis=1)

                if is_set:
                    pd_data = pd_data[pd_data['is_set'] == 1]
                    data = pd_data.iloc[0].to_dict()
                    # 篩選類別
                    data['data'] = [_d for _d in data['data'] if _d['is_set'] == 1]
                    # 取得一週離峰日
                    data['data'][0]['holidays'] = get_week_holidays_dates()
                elif _id is None:
                    pd_data = pd_data.drop(columns=[ApiConst.DATA.value])
                    data = pd_data.to_dict('records')
                else:
                    data = pd_data.to_dict('records')
        except Exception as e:
            message = str(e)
        return {'message': message, 'data': data}, 200, None

    @token_required(token_module)
    def post(self):
        self.logger.info('[post]')
        message = SUCCESS_MESSAGE
        data = list()
        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            permissions = user_info.user_field_permission

            if field not in permissions or not permissions[field].get(
                    PermissionConst.SYSTEMS_ELECTRIC_SETTING_POST_UPDATE.value, False):
                raise Exception('You dont have permission to access.')

            payload = request.get_json()
            _id = payload[ApiConst.ID_.value]
            is_set = payload.get(ApiConst.IS_SET.value, None)
            data = payload.get(ApiConst.DATA.value, None)

            if not _id:
                raise Exception("Missing required field: ID")

            ele_price = self.dao.get_electricity_settings()

            current_df = self.dao.get_electricity_price(_id=_id)
            if current_df.empty:
                raise Exception('找不到相關電價資訊')

            if is_set is not None:
                if str(ele_price['_id']) == _id:
                    if not is_set:
                        raise Exception("預設電價不可取消，如需更改，請至另一筆紀錄直接進行設定")
                elif is_set:
                    self.logger.info('clear electricity price set')
                    self.dao.clear_electricity_price_set()

            self.logger.info('update electricity price')
            pd_data = self.dao.update_electricity_price(_id=_id, is_set=is_set, data=data)
            data = pd_data.to_dict('records')
        except Exception as e:
            message = str(e)
            data = None
        return {'message': message, 'data': data}, 200, None
