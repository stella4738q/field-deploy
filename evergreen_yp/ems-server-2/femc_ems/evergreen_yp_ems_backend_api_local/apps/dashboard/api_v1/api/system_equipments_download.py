# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os

from flask import send_file, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ConfigConstant, ApiConst, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]

class SystemEquipmentsDownload(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def get(self):
        self.logger.info('[get] system equipments download')
        try:
            # check permission
            self.logger.info('check permission [download-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_EQUIPMENTS_DOWNLOAD_GET_DOWNLOAD.value]:
                raise Exception('You dont have permission to access.')

            self.logger.info('get resources')
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_system_resource = dao.get_system_equipment()

            self.logger.info('save data to csv file')
            file_name = os.path.join(f'{temp_folder}', "system_equipments.csv")
            pd_system_resource.to_csv(file_name, encoding='utf-8-sig', index=False)
            return send_file(file_name, mimetype="text/csv", attachment_filename="system_equipments.csv",
                             as_attachment=True)
        except Exception as e:
            raise e
