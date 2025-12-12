# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import base64

import numpy as np
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

class SystemAnnouncementDownload(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[get] system announcement download')
        try:
            _id = None

            if ApiConst.ID.value in request.args:
                _id = request.args[ApiConst.ID.value]

            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_announcement = dao.get_announcement(_id=_id)
            file = pd_announcement["file"].tolist()[0]
            fields = pd_announcement["fields"].tolist()[0]

            logger.info('check permission [operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) == 0 or \
                        fields not in allow_field or \
                        not user_info.user_field_permission[fields][PermissionConst.SYSTEM_ANNOUNCEMENT_DOWNLOAD_GET_DOWNLOAD.value]:
                    raise Exception('You dont have permission to access.')

            file_decode = base64.b64decode(file)

            return Response(file_decode)
        except Exception as e:
            raise e
