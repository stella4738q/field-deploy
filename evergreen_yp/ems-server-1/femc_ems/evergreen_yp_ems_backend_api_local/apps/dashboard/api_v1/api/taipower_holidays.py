# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import pandas as pd

import io
import os
from flask import request, send_file, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, ConfigConstant, PermissionConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource


class TaipowerHolidays(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] taipower holidays')
        pd_res = []
        try:
            year = request.args.get(ApiConst.YEAR.value, None)
            if not year:
                raise Exception('目標年為必要項目')

            holidays_df = self.dao.get_taipower_holidays(year)
            if not holidays_df.empty:
                pd_res = {
                    'year': year,
                    'data': holidays_df['holidays'][0]
                }
            else:
                pd_res = {
                    'year': year,
                    'data': []
                }

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        user_info: UserData = session[token_module.auth_session_key]
        pd_res = []
        try:
            year = request.form.get(ApiConst.YEAR.value, None)
            action = request.form.get(ApiConst.ACTION.value, None)
            if not year:
                raise Exception('年份為必要條件')

            if action not in ['0', '1']:
                raise Exception('執行類別錯誤')

            # 0: download, 1: upload
            if action == '0':
                self.logger.info('[post] download holidays')
                holidays_df = self.dao.get_taipower_holidays(year)
                if not holidays_df.empty:
                    date = holidays_df['holidays'][0]
                    data = [{'Year': int(d[:4]), 'Month': int(d[5:7]), 'Day': int(d[-2:])} for d in date]
                    df = pd.DataFrame(data)

                    csv_buffer = io.BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)

                    return send_file(
                        csv_buffer, mimetype="text/csv", as_attachment=True,
                        attachment_filename=os.path.basename(f'{year}_holidays.csv'))

            elif action == '1':
                field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                        not user_info.user_field_permission[field][
                            PermissionConst.TAIPOWER_HOLIDAYS_UPDATE.value]:
                    raise Exception('You dont have permission to access.')

                if 'file' not in request.files:
                    raise Exception('未上傳檔案')

                file = request.files[ApiConst.FILE.value]
                if file.filename == '':
                    raise Exception('找不到相關檔案')

                self.logger.info('[post] upload holidays')
                date_list = list()
                df = pd.read_csv(file)
                if not df.empty:
                    df['combine_date'] = df.apply(
                        lambda x: f"{str(x['Year'])}-{str(x['Month']).rjust(2, '0')}-{str(x['Day']).rjust(2, '0')}",
                        axis=1)
                    date_list = df['combine_date'].tolist()

                # 先全部刪除
                self.dao.delete_taipower_holidays(year)

                # 重新填入
                self.dao.create_taipower_holidays(year, date_list)

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None