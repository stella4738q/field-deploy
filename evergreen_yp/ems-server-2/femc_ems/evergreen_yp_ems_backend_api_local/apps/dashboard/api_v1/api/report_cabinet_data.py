# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import calendar
import io
import os
import pathlib
import subprocess
import uuid

import pandas as pd
import sys
from datetime import datetime, timedelta

import numpy as np
from flask import request, session, make_response, jsonify, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.equipment_type import EquipmentType
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.token_module import token_required, UserData
from . import Resource


class CabinetReportData(Resource):
    """
    報表資訊
    - 日、月、年報查詢
    - 檔案下載
    """
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
    temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]
    doc_folder = config[ConfigConstant.APP.value][ConfigConstant.DOC_FOLDER.value]
    device_type = 'web'

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = None
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[get] report data')
        try:
            # 0:日報, 1:月報, 2:年報
            report_type = request.args.get(ApiConst.TYPE.value, None)
            if report_type is None:
                raise Exception('報表類型為必要項目')
            report_type = int(report_type)

            start_dt = request.args.get(ApiConst.START_DATE.value, None)
            if start_dt:
                if report_type == 0:
                    start_dt = datetime.strptime(start_dt, '%Y%m%d')
                elif report_type == 1:
                    year = int(start_dt[0:4])
                    month = int(start_dt[4:6])
                    start_dt = datetime(year, month, 1)
                else:
                    year = int(start_dt[0:4])
                    start_dt = datetime(year, 1, 1)
            else:
                start_dt = None

            end_dt = request.args.get(ApiConst.END_DATE.value, None)
            if end_dt:
                if report_type == 0:
                    end_dt = datetime.strptime(end_dt, '%Y%m%d')\
                        .replace(hour=23, minute=59, second=59, microsecond=999999)
                elif report_type == 1:
                    year = int(end_dt[0:4])
                    month = int(end_dt[4:6])
                    _, last_day = calendar.monthrange(year, month)
                    end_dt = datetime(year, month, last_day, 23, 59, 59, 999999)
                else:
                    year = int(end_dt[0:4])
                    end_dt = datetime(year, 12, 31, 23, 59, 59, 999999)
            else:
                end_dt = None

            order_field = request.args.get(ApiConst.ORDER_FIELD.value, 'date_time')
            order_type = request.args.get(ApiConst.ORDER_TYPE.value, 'asc')
            page = request.args.get(ApiConst.PAGE.value, 1)
            page = int(page)

            limit = request.args.get(ApiConst.LIMIT.value, 10)
            limit = int(limit)

            offset = (int(page) - 1) * int(limit)

            # get data
            if report_type == 0:
                pd_data = self.dao.get_daily_report(
                    start_date=start_dt, end_date=end_dt,
                    order_field=order_field, order_type=order_type, limit=limit, offset=offset)
            elif report_type == 1:
                pd_data = self.dao.get_monthly_report(
                    start_date=start_dt, end_date=end_dt,
                    order_field=order_field, order_type=order_type, limit=limit, offset=offset)
            else:
                pd_data = self.dao.get_yearly_report(
                    start_date=start_dt, end_date=end_dt,
                    order_field=order_field, order_type=order_type, limit=limit, offset=offset)

            total_count = pd_data['total_count']
            tmp_df = pd_data['data']
            if not tmp_df.empty:
                tmp_df = tmp_df.replace({np.nan: None})
                tmp_df['type'] = report_type

                tmp_df['date_time'] = pd.to_datetime(tmp_df['date_time'])
                tmp_df['date_time'] = tmp_df['date_time'].view('int64') // 10**9
                rtn_data.Data = {
                    'total_count': int(total_count),
                    'data': tmp_df.to_dict('records')
                }
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('[post] export report')
        try:
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.CABINET_REPORTS_POST_DOWNLOAD.value]:
                raise Exception('你沒有權限下載')

            payload = request.get_json()

            self.device_type = payload.get(ApiConst.DEVICE_TYPE.value, "web")

            use_pcs_key = payload.get(ApiConst.USE_PCS_KEY.value, False)
            pcs_in_key = 'bms_charge_capacity'
            pcs_out_key = 'bms_discharge_capacity'
            if use_pcs_key:
                pcs_in_key = 'pcs_charge_capacity'
                pcs_out_key = 'pcs_discharge_capacity'

            # 0:日報, 1:月報, 2:年報
            report_type = payload.get(ApiConst.TYPE.value, None)
            if report_type is None:
                raise Exception('報表類型為必要項目')

            target_year = payload.get(ApiConst.YEAR.value, None)
            if target_year:
                target_year = int(target_year)

            target_month = payload.get(ApiConst.MONTH.value, None)
            if target_month:
                target_month = int(target_month)

            target_day = payload.get(ApiConst.DAY.value, None)
            if target_day:
                target_day = int(target_day)

            if report_type == 0:
                if target_year is None or target_month is None or target_day is None:
                    raise Exception("報表參數錯誤")
                return self.export_daily_report(target_year, target_month, target_day, pcs_in_key, pcs_out_key)

            elif report_type == 1:
                if target_year is None or target_month is None:
                    raise Exception("報表參數錯誤")
                return self.export_monthly_report(target_year, target_month, pcs_in_key, pcs_out_key)

            else:
                if target_year is None:
                    raise Exception("報表參數錯誤")
                return self.export_yearly_report(target_year, pcs_in_key, pcs_out_key)

        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    def export_daily_report(self, year, month, day, in_key, out_key):
        doc_base_name = '晉瑜企業利澤廠儲能系統-日報表'
        is_windows = True if sys.platform == 'win32' or os.name == 'nt' else False
        target_folder = self.temp_folder
        data_frame = self.dao.export_daily_report(year=year, month=month, day=day)
        if not data_frame.empty:
            data = data_frame.iloc[0]['data_list']
            file_list = []

            data_frame = pd.DataFrame(data)
            uid = uuid.uuid4()
            doc_name = f'{uid}_{doc_base_name}.docx' if is_windows else f'{uid}_{doc_base_name}.odt'
            pdf_name = f'{uid}_{doc_base_name}.pdf'
            doc_save_path = os.path.join(target_folder, doc_name)
            pdf_save_path = os.path.join(target_folder, pdf_name)
            template_path = os.path.join(self.doc_folder, doc_base_name + ('.docx' if is_windows else '.odt'))

            # 替代參數設定
            context = {
                'year': year,
                'month': month,
                'day': day
            }
            items = data_frame.to_dict(orient='records')
            for x in range(24):  # 固定24小時
                c_item = list(filter(lambda q: q['hour'] == x, items))
                if c_item:
                    context[f"pcs_exp_{x}"] = round(float(c_item[0][out_key]), 1)
                    context[f"pcs_imp_{x}"] = round(float(c_item[0][in_key]), 1)
                    context[f"me_exp_{x}"] = round(float(c_item[0]['meter_discharge_capacity']), 1)
                    context[f"me_imp_{x}"] = round(float(c_item[0]['meter_charge_capacity']), 1)
                    context[f"soc_{x}"] = round(float(c_item[0]['soc']), 1)
                    context[f"tmp_{x}"] = round(float(c_item[0]['container_temp']), 1)
                else:
                    context[f"pcs_exp_{x}"] = 0.0
                    context[f"pcs_imp_{x}"] = 0.0
                    context[f"me_exp_{x}"] = 0.0
                    context[f"me_imp_{x}"] = 0.0
                    context[f"soc_{x}"] = 0.0
                    context[f"tmp_{x}"] = 0.0
            pcs_out_total = data_frame[out_key].sum()
            pcs_in_total = data_frame[in_key].sum()
            meter_in_total = data_frame['meter_charge_capacity'].sum()
            meter_out_total = data_frame['meter_discharge_capacity'].sum()

            context['tot_pcs_exp'] = round(float(pcs_out_total), 1)
            context['tot_pcs_imp'] = round(float(pcs_in_total), 1)
            context['tot_me_exp'] = round(float(meter_out_total), 1)
            context['tot_me_imp'] = round(float(meter_in_total), 1)

            context['pcs_ratio'] = round(float(pcs_out_total/pcs_in_total) * 100, 1) if pcs_in_total != 0 else '-'
            context['me_ratio'] = round(float(meter_out_total/meter_in_total) * 100, 1) if meter_in_total != 0 else '-'

            self.replace_parameter(template_path, doc_save_path, context)
            pdf_file = self.export_docx_to_pdf_file(doc_save_path, pdf_save_path)
            file_list.append(pdf_file)

            return self.process_file(file_list, target_folder, doc_name)
        else:
            return None

    def export_monthly_report(self, year, month, in_key, out_key):
        doc_base_name = '晉瑜企業利澤廠儲能系統-月報表'
        is_windows = True if sys.platform == 'win32' or os.name == 'nt' else False
        target_folder = self.temp_folder
        data_frame = self.dao.export_monthly_report(year=year, month=month)
        if not data_frame.empty:
            data = data_frame.iloc[0]['data_list']
            file_list = []

            data_frame = pd.DataFrame(data)
            uid = uuid.uuid4()
            doc_name = f'{uid}_{doc_base_name}.docx' if is_windows else f'{uid}_{doc_base_name}.odt'
            pdf_name = f'{uid}_{doc_base_name}.pdf'
            doc_save_path = os.path.join(target_folder, doc_name)
            pdf_save_path = os.path.join(target_folder, pdf_name)
            template_path = os.path.join(self.doc_folder, doc_base_name + ('.docx' if is_windows else '.odt'))

            # 替代參數設定
            context = {
                'year': year,
                'month': month
            }

            items = data_frame.to_dict(orient='records')
            for x in range(1, 32):  # 固定31天
                c_item = list(filter(lambda q: q['day'] == x, items))
                if c_item:
                    context[f"pcs_exp_{x}"] = round(float(c_item[0][out_key]), 1)
                    context[f"pcs_imp_{x}"] = round(float(c_item[0][in_key]), 1)
                    context[f"me_exp_{x}"] = round(float(c_item[0]['meter_discharge_capacity']), 1)
                    context[f"me_imp_{x}"] = round(float(c_item[0]['meter_charge_capacity']), 1)
                else:
                    context[f"pcs_exp_{x}"] = 0.0
                    context[f"pcs_imp_{x}"] = 0.0
                    context[f"me_exp_{x}"] = 0.0
                    context[f"me_imp_{x}"] = 0.0

            pcs_out_total = data_frame[out_key].sum()
            pcs_in_total = data_frame[in_key].sum()
            meter_in_total = data_frame['meter_charge_capacity'].sum()
            meter_out_total = data_frame['meter_discharge_capacity'].sum()

            context['tot_pcs_exp'] = round(float(pcs_out_total), 1)
            context['tot_pcs_imp'] = round(float(pcs_in_total), 1)
            context['tot_me_exp'] = round(float(meter_out_total), 1)
            context['tot_me_imp'] = round(float(meter_in_total), 1)

            context['pcs_ratio'] = round(float(pcs_out_total/pcs_in_total) * 100, 1) if pcs_in_total != 0 else '-'
            context['me_ratio'] = round(float(meter_out_total/meter_in_total) * 100, 1) if meter_in_total != 0 else '-'

            self.replace_parameter(template_path, doc_save_path, context)
            pdf_file = self.export_docx_to_pdf_file(doc_save_path, pdf_save_path)
            file_list.append(pdf_file)

            return self.process_file(file_list, target_folder, doc_name)
        else:
            return None

    def export_yearly_report(self, year, in_key, out_key):
        doc_base_name = '晉瑜企業利澤廠儲能系統-年報表'
        is_windows = True if sys.platform == 'win32' or os.name == 'nt' else False
        target_folder = self.temp_folder
        data_frame = self.dao.export_yearly_report(year=year)
        if not data_frame.empty:
            data = data_frame.iloc[0]['data_list']
            file_list = []

            data_frame = pd.DataFrame(data)
            uid = uuid.uuid4()
            doc_name = f'{uid}_{doc_base_name}.docx' if is_windows else f'{uid}_{doc_base_name}.odt'
            pdf_name = f'{uid}_{doc_base_name}.pdf'
            doc_save_path = os.path.join(target_folder, doc_name)
            pdf_save_path = os.path.join(target_folder, pdf_name)
            template_path = os.path.join(self.doc_folder, doc_base_name + ('.docx' if is_windows else '.odt'))

            # 替代參數設定
            context = {
                'year': year
            }

            items = data_frame.to_dict(orient='records')
            for x in range(1, 13):  # 固定12個月
                c_item = list(filter(lambda q: q['month'] == x, items))
                if c_item:
                    context[f"pcs_exp_{x}"] = round(float(c_item[0][out_key]), 1)
                    context[f"pcs_imp_{x}"] = round(float(c_item[0][in_key]), 1)
                    context[f"me_exp_{x}"] = round(float(c_item[0]['meter_discharge_capacity']), 1)
                    context[f"me_imp_{x}"] = round(float(c_item[0]['meter_charge_capacity']), 1)
                else:
                    context[f"pcs_exp_{x}"] = 0.0
                    context[f"pcs_imp_{x}"] = 0.0
                    context[f"me_exp_{x}"] = 0.0
                    context[f"me_imp_{x}"] = 0.0

            pcs_out_total = data_frame[out_key].sum()
            pcs_in_total = data_frame[in_key].sum()
            meter_in_total = data_frame['meter_charge_capacity'].sum()
            meter_out_total = data_frame['meter_discharge_capacity'].sum()

            context['tot_pcs_exp'] = round(float(pcs_out_total), 1)
            context['tot_pcs_imp'] = round(float(pcs_in_total), 1)
            context['tot_me_exp'] = round(float(meter_out_total), 1)
            context['tot_me_imp'] = round(float(meter_in_total), 1)

            context['pcs_ratio'] = round(float(pcs_out_total/pcs_in_total) * 100, 1) if pcs_in_total != 0 else '-'
            context['me_ratio'] = round(float(meter_out_total/meter_in_total) * 100, 1) if meter_in_total != 0 else '-'

            self.replace_parameter(template_path, doc_save_path, context)
            pdf_file = self.export_docx_to_pdf_file(doc_save_path, pdf_save_path)
            file_list.append(pdf_file)

            return self.process_file(file_list, target_folder, doc_name)
        else:
            return None

    @staticmethod
    def replace_parameter(template_file, output_file, context: dict):
        if sys.platform == 'win32' or os.name == 'nt':
            from docxtpl import DocxTemplate
            doc = DocxTemplate(template_file)
            doc.render(context)
            doc.save(output_file)
        else:
            param_keys = dict()
            for key, value in zip(context.keys(), context.values()):
                param_keys['{{' + key + '}}'] = value
            from odf import text, teletype
            from odf.opendocument import load
            doc = load(template_file)
            paragraphs = doc.getElementsByType(text.P)

            for paragraph in paragraphs:
                old_text = teletype.extractText(paragraph)
                if old_text.find('{{') == -1:
                    continue

                if old_text in param_keys.keys():
                    # 完整抓到 ex: {{business_unit_name}}
                    paragraph.childNodes = []
                    old_text = old_text.replace(old_text, str(param_keys[old_text]))
                    teletype.addTextToElement(paragraph, old_text)
                else:
                    # 混一起 ex: {{year}}年{{month}}月{{day}}日
                    found = False
                    for key, value in param_keys.items():
                        if key in old_text:
                            old_text = old_text.replace(key, str(value))
                            found = True
                    if found:
                        paragraph.childNodes = []
                        teletype.addTextToElement(paragraph, old_text)
                    else:
                        # 散落在子項，組合起來在找
                        text_list = []
                        for obj in paragraph.childNodes:
                            if type(obj).__name__ == "Text":
                                text_list.append(obj.data)
                        old_text = ''.join(text_list)
                        for key, value in param_keys.items():
                            if key in old_text:
                                old_text = old_text.replace(key, str(value))
                        paragraph.childNodes = []
                        teletype.addTextToElement(paragraph, old_text)
            doc.save(output_file)

    @staticmethod
    def export_docx_to_pdf_file(input_file, output_file):
        if sys.platform == 'win32' or os.name == 'nt':
            import win32com.client
            import pythoncom
            from docx2pdf import convert
            win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())
            # to pdf
            convert(input_file, output_file)
            pythoncom.CoUninitialize()
        else:
            target_folder = pathlib.Path(output_file).parent
            # to pdf
            cmd = ['libreoffice', '--headless', '--convert-to', 'pdf', input_file, '--outdir', target_folder]
            subprocess.call(cmd)
        os.remove(input_file)
        return output_file

    @staticmethod
    def merger_pdf(file_list, folder):
        from PyPDF2 import PdfWriter
        pdf_merger = PdfWriter()

        for f_name in file_list:
            pdf_merger.append(f_name)
        pdf_merger.write(f'{folder}/output.pdf')

        for f_name in file_list:
            os.remove(f_name)
        return f'{folder}/output.pdf'

    @staticmethod
    def app_response(file):
        import base64
        rtn_data = ApiResponse()
        with open(file, 'rb') as fo:
            rtn_data.data = bytes.decode(base64.b64encode(fo.read()), 'utf-8')
        os.remove(file)
        return make_response(jsonify(rtn_data.serialized), 200)

    def process_file(self, file_list: list, target_folder, filename):
        file_count = len(file_list)
        if file_count == 1:
            file = file_list[0]
        else:
            file = self.merger_pdf(file_list, target_folder)

        if self.device_type == 'app':
            return self.app_response(file)
        else:
            download_name = f'{filename}.pdf'
            mimetype = "application/pdf"
            return_data = io.BytesIO()
            with open(file, 'rb') as fo:
                return_data.write(fo.read())
            return_data.seek(0)
            os.remove(file)
            return send_file(
                return_data, mimetype=mimetype,
                as_attachment=True, attachment_filename=download_name)
