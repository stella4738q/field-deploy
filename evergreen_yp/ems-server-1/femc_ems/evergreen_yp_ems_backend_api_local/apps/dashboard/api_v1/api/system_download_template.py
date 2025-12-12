# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
from flask import request, send_file

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required
from . import Resource


class SystemDownloadTemplate(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system template')
        pd_res = []
        try:
            template_id = request.args.get(ApiConst.TEMPLATE_ID.value, None)
            if not template_id:
                raise Exception('範本ID為必要項目')

            file_path = f'templates/{template_id}'

            if not os.path.exists(file_path):
                raise Exception(f'找不到對應範本: {template_id}')

            return_data = io.BytesIO()
            with open(file_path, 'rb') as fo:
                return_data.write(fo.read())
            return_data.seek(0)

            return send_file(
                return_data, mimetype="text/csv",
                as_attachment=True, attachment_filename=os.path.basename(file_path))
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None
