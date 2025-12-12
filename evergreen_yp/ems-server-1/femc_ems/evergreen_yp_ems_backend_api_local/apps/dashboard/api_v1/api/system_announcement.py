# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import base64
import numpy as np
from flask import request, make_response, jsonify, session

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.utils import FeatureFunc
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from dashboard_lib.geo_location import coordination
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.token_module import token_required, UserData
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes
from . import Resource


class SystemAnnouncement(Resource):

    @token_required(token_module)
    def get(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[get] system announcement')
        pd_res = []
        try:
            # check permission
            logger.info('check permission [query]')
            allow_field = None
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin:
                allow_field = [key for key in user_info.user_field_permission.keys()]
                if allow_field is None:
                    allow_field = list()

            start_time = None
            end_time = None
            fields = None
            content = None
            if 'start_time' in request.args and 'end_time' in request.args:
                start_time = request.args[ApiConst.START_TIME.value]
                end_time = request.args[ApiConst.END_TIME.value]
            if ApiConst.FIELDS.value in request.args:
                fields = request.args[ApiConst.FIELDS.value]
            if ApiConst.CONTENT.value in request.args:
                content = request.args[ApiConst.CONTENT.value]


            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_announcement(start_time=start_time, end_time=end_time, fields=fields,
                                           content=content, allow_field=allow_field)
            pd_data = pd_data.replace({np.nan: None})
            if not pd_data.empty:
                del pd_data['file']
            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def post(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[post] system announcement')
        pd_res = []
        try:
            payload = request.form
            _id = payload[ApiConst.ID.value] if 'id' in payload else None
            eventon = payload[ApiConst.EVENTON.value] if 'eventon' in payload else None
            fields = payload[ApiConst.FIELDS.value] if 'fields' in payload else None
            content = payload[ApiConst.CONTENT.value] if 'content' in payload else None
            createon = datetime.utcnow()
            file = request.files[ApiConst.FILE.value] if request.files else None
            modify_file = payload[ApiConst.MODIFY_FILE.value] if 'modify_file' in payload else None

            dao = StorageFactory(config).get_dao_factory().get_dao()

            encoded_string = None
            minetype = None
            filename = None
            if file:
                filename = secure_filename(file.filename)
                minetype = file.content_type
                file_read = file.read()
                blob = base64.b64encode(file_read)
                encoded_string = blob.decode('utf-8')
            else:
                if modify_file == "N":
                    filename = dao.get_announcement(_id=_id)[ApiConst.FILENAME.value].tolist()[0]
                    minetype = dao.get_announcement(_id=_id)[ApiConst.MINETYPE.value].tolist()[0]
                    encoded_string = dao.get_announcement(_id=_id)[ApiConst.FILE.value].tolist()[0]

            if _id:
                logger.info('check permission [modify-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                if not user_info.is_admin and not user_info.is_field_admin:
                    allow_field = user_info.user_field_permission.keys()
                    if len(user_info.user_field_permission) == 0 or \
                            fields not in allow_field or \
                            not user_info.user_field_permission[fields][PermissionConst.SYSTEM_ANNOUNCEMENT_POST_UPDATE.value]:
                        raise Exception('You dont have permission to access.')

                logger.info('update system announcement')
                if fields is not None:
                    pd_field = dao.get_fields(_id=fields)
                    field_name = pd_field[ApiConst.CODE.value].tolist()[0] + pd_field[ApiConst.NAME.value].tolist()[0]
                    pd_data = dao.update_announcement(_id, createon, eventon, fields, content,
                                                      encoded_string, minetype, filename, field_name)
            else:
                logger.info('check permission [add-operation]')
                user_info: UserData = session[token_module.auth_session_key]
                if not user_info.is_admin and not user_info.is_field_admin:
                    allow_field = user_info.user_field_permission.keys()
                    if len(user_info.user_field_permission) == 0 or \
                            fields not in allow_field or \
                            not user_info.user_field_permission[fields][PermissionConst.SYSTEM_ANNOUNCEMENT_POST_CREATE.value]:
                        raise Exception('You dont have permission to access.')

                logger.info('create system announcement')
                if fields is not None:
                    pd_field = dao.get_fields(_id=fields)
                    field_name = pd_field[ApiConst.CODE.value].tolist()[0] + pd_field[ApiConst.NAME.value].tolist()[0]
                    pd_data = dao.create_announcement(_id, createon, eventon, fields, content,
                                                      encoded_string, minetype, filename, field_name)

            pd_data = pd_data.replace({np.nan: None})
            if not pd_data.empty:
                del pd_data['file']

            logger.debug('\nraw data: \n{}\n'.format(pd_data.head(3)))

            pd_res = pd_data.to_dict('records')
            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message, 'data': pd_res}, 200, None

    @token_required(token_module)
    def delete(self):
        logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        logger.info('[del] system announcement')
        try:
            _id = request.get_json()[ApiConst.ID.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()
            fields = dao.get_announcement(_id=_id)['fields'].tolist()[0]

            logger.info('check permission [delete-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            if not user_info.is_admin and not user_info.is_field_admin:
                allow_field = user_info.user_field_permission.keys()
                if len(user_info.user_field_permission) == 0 or \
                        fields not in allow_field or \
                        not user_info.user_field_permission[fields][PermissionConst.SYSTEM_ANNOUNCEMENT_DELETE.value]:
                    raise Exception('You dont have permission to access.')

            dao.delete_announcement([_id])

            message = SUCCESS_MESSAGE
        except Exception as e:
            message = repr(e)
        return {'message': message}, 200, None