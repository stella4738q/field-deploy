# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os

import numpy as np
import pandas as pd
from flask import send_file
from flask import request, g, session
from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ConfigConstant, SUCCESS_MESSAGE, ApiConst, PermissionConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.token_module import token_required, UserData
from . import Resource

temp_folder = config[ConfigConstant.APP.value][ConfigConstant.TEMP_FOLDER.value]


class SystemEquipmentsUpload(Resource):
    dao = StorageFactory(config).get_dao_factory().get_dao()
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)

    @token_required(token_module)
    def post(self):
        self.logger.info('[get] system equipments upload')
        result = True
        message = SUCCESS_MESSAGE
        try:
            # check permission
            self.logger.info('check permission [upload-operation]')
            user_info: UserData = session[token_module.auth_session_key]
            field = config[ConfigConstant.APP.value][ApiConst.FIELD_ID.value]
            allow_field = user_info.user_field_permission.keys()
            if len(user_info.user_field_permission) > 0 and \
                    field not in allow_field or \
                    not user_info.user_field_permission[field][
                        PermissionConst.SYSTEM_EQUIPMENTS_DOWNLOAD_EXAMPLE_GET_DOWNLOAD.value]:
                raise Exception('You dont have permission to access.')

            file = request.files[ApiConst.FILE.value]
            file_read = file.read()
            file_read_str = file_read.decode("utf-8-sig")

            if '\r\n' in file_read_str:
                data_list = file_read_str.split('\r\n')
            else:
                data_list = file_read_str.split('\n')

            self.logger.info('check dataframe column names')
            if data_list[0] != "_id,parent_id,case_code,field_id,code,equipment_type,name,brand,ip,port,capacity":
                raise Exception('please enter the example format')

            case_code = [data.split(',')[2] for data in data_list[1:-1]]
            case_id_list = list()
            for code in case_code:
                case_id = self.dao.get_local_cases(code=code)['_id'].tolist()[0]
                case_id_list.append(case_id)

            _id_list = list()
            parent_id_list = list()
            field_id_list = list()
            code_list = list()
            equipment_type_list = list()
            name_list = list()
            brand_list = list()
            ip_list = list()
            port_list = list()
            capacity_list = list()

            for data in data_list[1:-1]:
                data = data.split(',')
                if len(data) == 11:
                    _id = data[0]
                    parent_id = data[1]
                    field_id = data[3]
                    code = data[4]
                    equipment_type = data[5]
                    name = data[6]
                    brand = data[7]
                    ip = data[8]
                    port = data[9]
                    capacity = data[10]

                    _id_list.append(_id)
                    parent_id_list.append(parent_id)
                    field_id_list.append(field_id)
                    code_list.append(code)
                    equipment_type_list.append(equipment_type)
                    name_list.append(name)
                    brand_list.append(brand)
                    ip_list.append(ip)
                    port_list.append(port)
                    capacity_list.append(capacity)

            data_dict = {ApiConst.ID_.value: _id_list, ApiConst.PARENT_ID.value: parent_id_list,
                         ApiConst.CASE_ID.value: case_id_list, ApiConst.FIELD_ID.value: field_id_list,
                         ApiConst.CODE.value: code_list, ApiConst.EQUIPMENT_TYPE.value: equipment_type_list,
                         ApiConst.NAME.value: name_list, ApiConst.BRAND.value: brand_list,
                         ApiConst.IP.value: ip_list, ApiConst.PORT.value: port_list,
                         ApiConst.CAPACITY.value: capacity_list}
            df = pd.DataFrame(data_dict)
            df = df.replace({np.nan: None})
            self.logger.debug('\nraw data: \n{}\n'.format(df.head(3)))

            # del resource
            self.logger.info('clear equipments current data')
            self.dao.del_local_equipment()
            # write resource
            self.logger.info('update resource')
            rtn_msg = self.dao.update_local_equipments(df)

            if rtn_msg.lower() != "success":
                message = rtn_msg
                result = False

        except Exception as e:
            message = repr(e)
            result = False
        return {'success': result, 'message': message}, 200, None
