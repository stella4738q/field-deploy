# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from flask import request, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from . import Resource
from dashboard_lib.eci import ECI
from dashboard_lib.filesystem.file_system_dao import FilesystemSettings, FolderType, FileExtension


class EMSEssci(Resource):
    """
    取得ESSCI報表, 儲能櫃頁面中使用
    """

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('Get EMS ESSCI')
        rtn_data = None
        try:
            # check permission
            logger.info('check permission [query]')
            user_info: UserData = session[token_module.auth_session_key]
            field_id = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            if not user_info.is_admin:
                if field_id not in user_info.user_field_permission.keys():
                    raise Exception('you dont have permission to access.')

            # get data
            essci_key = None
            if ApiConst.ESSCI_KEY.value in request.args:
                essci_key = request.args[ApiConst.ESSCI_KEY.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_essci(essci_key=essci_key)
            if not pd_data.empty:
                rtn_data = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)

        return {'message': message, 'data': rtn_data}, 200, None
