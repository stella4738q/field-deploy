# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import copy
import datetime

import jwt
from bson import ObjectId
import pyotp
from flask import request, make_response, jsonify

from apps.dashboard import config, log_path, logging_level, token_module, single_login
from apps.dashboard.constant import ApiConst, ConfigConstant
from dashboard_lib.constant import ConfigConstant
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.api_response import TokenResponse
from utility.edutil import EDUtility
from . import Resource


class PermissionUserLogin(Resource):

    """
    限制每個帳號只能一處登入(admin 身份除外)
    登入需寫入table: login info
    """

    def post(self):
        logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)
        logger.info('permission user login')
        response_data = TokenResponse()
        try:
            payload = request.get_json()
            # 0:雲端, 1:地端, 2:SSO
            login_type = payload[ApiConst.TYPE.value]
            dao = StorageFactory(config).get_dao_factory().get_dao()

            if login_type == 0 or login_type == 1:
                account = payload[ApiConst.ACCOUNT.value]
                password = payload[ApiConst.PASSWORD.value]
                result = dao.user_login(account, password)
                if not result['Success']:
                    raise Exception(result['Msg'])
                user_info = result['UserInfo']
            elif login_type == 2:
                if not token_module.auth_header.capitalize() in request.headers:
                    raise Exception('could not verify authorization, login required.')
                token = request.headers[token_module.auth_header.capitalize()]
                data = jwt.decode(token, token_module.auth_security_key, verify=False,
                                  options={'verify_signature': False}, algorithms='HS256')
                exp_data = datetime.datetime.fromtimestamp(data["exp_date"])
                if token_module.api_auth_enable:
                    if datetime.datetime.utcnow() > exp_data:
                        raise Exception('Token is expired.')
                del data['exp_date']
                user_info = data
            else:
                raise Exception('login type error.')

            if user_info.get('enable_otp'):
                response_data.Otp = True

                pd_user = dao.get_users(_id=user_info['id'])
                # 表示需要進入兩階段驗證
                if ApiConst.OTP.value in payload and payload[ApiConst.OTP.value] != "" \
                        and payload[ApiConst.OTP.value] is not None:
                    otp = payload[ApiConst.OTP.value]
                else:
                    raise Exception("登入成功，您需要兩階段驗證，請輸入OTP")

                encrypted_secret_key = pd_user[ApiConst.TWO_FACTOR_SECRET_KEY.value][0]
                iv = pd_user[ApiConst.IV.value][0]
                if not encrypted_secret_key or not iv:
                    raise Exception("該使用者已啟用兩階段驗證 但並未成功")

                # 解密密鑰
                secret_key = EDUtility(config).aes_decrypt(encrypted_secret_key, iv)
                # 驗證 OTP
                totp = pyotp.TOTP(secret_key)
                if not totp.verify(otp):
                    raise Exception("無效的OTP")

            need_create_login_info = False
            account = None
            if single_login and not user_info['is_admin']:
                # 檢查帳號是否存在login_info中，有的話表示已經登入過
                user_id = user_info['id']
                user = dao.get_users(_id=user_id).iloc[0]
                account = user['account']
                target = dao.get_login_info(login_account=account)
                if not target.empty:
                    raise Exception("E003：此帳號目前被其他裝置登入。")
                user_info['login_info_id'] = str(ObjectId())
                need_create_login_info = True

            if login_type == 0:
                exp_data = datetime.datetime.utcnow() + datetime.timedelta(minutes=token_module.api_auth_life)
                token_info = copy.deepcopy(user_info)
                token_info[ApiConst.EXP_DATE.value] = datetime.datetime.timestamp(exp_data)
                result = EDUtility(config).data_encrypt(token_info)
                if result.Success:
                    response_data.UserInfo = user_info
                    response_data.Token = result.Data
                else:
                    raise Exception(f'System error. msg: {result.Msg}')
            else:
                current_field = config[ConfigConstant.APP.value][ConfigConstant.FIELD_ID.value]
                # get user data
                user_id = user_info['id']
                user = dao.get_users(_id=user_id).iloc[0]
                if not user['is_admin']:
                    field_permission = dao.get_user_fields(user_id=user_id)
                    if field_permission.empty or current_field not in field_permission['field_id'].tolist():
                        raise Exception('user had no permission to visit the field.')

                exp_data = datetime.datetime.utcnow() + datetime.timedelta(minutes=token_module.api_auth_life)
                token_info = copy.deepcopy(user_info)
                token_info[ApiConst.EXP_DATE.value] = datetime.datetime.timestamp(exp_data)
                result = EDUtility(config).data_encrypt(token_info)
                if result.Success:
                    response_data.UserInfo = user_info
                    response_data.Token = result.Data
                    response_data.FieldId = current_field
                else:
                    raise Exception(f'System error. msg: {result.Msg}')

            if need_create_login_info:
                # 新增 login_info
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_address and ',' in ip_address:
                    ip_address = ip_address.split(',')[0].strip()
                dao.create_login_info(
                    _id=user_info['login_info_id'], account=account, ip_address=ip_address, token=result.Data)

        except Exception as e:
            response_data.Success = False
            response_data.Msg = str(e)
        return make_response(jsonify(response_data.serialized), 200)
