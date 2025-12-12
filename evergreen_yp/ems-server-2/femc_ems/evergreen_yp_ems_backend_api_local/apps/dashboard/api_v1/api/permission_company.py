# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import numpy as np
from flask import request, make_response, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard.constant import ApiConst, SUCCESS_MESSAGE
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from apps.dashboard import token_module
from utility.api_response import ApiResponse
from utility.token_module import token_required
from . import Resource


class PermissionCompany(Resource):

    @token_required(token_module)
    def get(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('EMS API', level=logging_level, log_path=log_path)
        logger.info('[get] company')
        try:
            _id = request.args[ApiConst.ID.value] if ApiConst.ID.value in request.args else None
            name = request.args[ApiConst.NAME.value] if ApiConst.NAME.value in request.args else None

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            pd_data = dao.get_company(_id, name)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)

        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def post(self):
        rtn_data = ApiResponse()
        rtn_data.Data = list()
        logger = Logger().create('EMS API', level=logging_level, log_path=log_path)
        logger.info('[post] company')
        try:
            payload = request.get_json()
            _id = payload[ApiConst.ID.value] if ApiConst.ID.value in payload else None
            name = payload[ApiConst.NAME.value]
            address = payload[ApiConst.ADDRESS.value] if ApiConst.ADDRESS.value in payload else None
            telephone = payload[ApiConst.TELEPHONE.value] if ApiConst.TELEPHONE.value in payload else None
            fax = payload[ApiConst.FAX.value] if ApiConst.FAX.value in payload else None
            contact = payload[ApiConst.CONTACT.value] if ApiConst.CONTACT.value in payload else None
            contact_telephone = payload[ApiConst.CONTACT_TELEPHONE.value] if ApiConst.CONTACT_TELEPHONE.value in payload else None
            no = payload[ApiConst.NO.value] if ApiConst.NO.value in payload else None

            # get data
            dao = StorageFactory(config).get_dao_factory().get_dao()
            if _id:
                logger.info('update company')
                pd_data = dao.update_company(_id, name, address, telephone, fax, contact, contact_telephone, no)
            else:
                logger.info('create company')
                pd_data = dao.create_company(name, address, telephone, fax, contact, contact_telephone, no)
            if not pd_data.empty:
                pd_data = pd_data.replace({np.nan: None})
                rtn_data.Data = pd_data.to_dict('records')
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    @token_required(token_module)
    def delete(self):
        rtn_data = ApiResponse()
        logger = Logger().create('EMS API', level=logging_level, log_path=log_path)
        logger.info('[delete] company')
        try:
            _id = request.get_json()[ApiConst.ID.value]

            dao = StorageFactory(config).get_dao_factory().get_dao()
            dao.delete_company([_id])
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = repr(e)
        return make_response(jsonify(rtn_data.serialized), 200)
