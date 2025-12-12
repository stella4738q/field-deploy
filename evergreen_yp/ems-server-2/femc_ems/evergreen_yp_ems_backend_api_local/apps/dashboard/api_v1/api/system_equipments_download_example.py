# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import base64

import numpy as np
import pandas as pd
from flask import request, make_response, jsonify, send_file, Response, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.geo_location import coordination
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from werkzeug.utils import secure_filename
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant, PermissionConst
from datetime import datetime
import mimetypes
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]

class SystemEquipmentsDownloadExample(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system equipments download example')
        try:
            # check permission
            self.logger.info('check permission [download-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_EQUIPMENTS_DOWNLOAD_EXAMPLE_GET_DOWNLOAD.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('define dataframe column names')
            pd_data = pd.DataFrame(columns=['_id', 'parent_id', 'case_id', 'field_id', 'code', 'equipment_type',
                               'name', 'brand', 'ip', 'port', 'capacity'])

            self.logger.info('save example to csv file')
            file_name = os.path.join(f'{temp_folder}', "system_equipments_example.csv")
            pd_data.to_csv(file_name, encoding='utf-8-sig', index=False)
            return send_file(file_name, mimetype="text/csv", attachment_filename="system_equipments_example.csv",
                             as_attachment=True)
        except Exception as e:
            raise e
