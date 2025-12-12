# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from base64 import b64encode
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

import pyotp
import qrcode
from flask import request, session, make_response, jsonify

from apps.dashboard import config, log_path, logging_level
from apps.dashboard import token_module
from apps.dashboard.constant import ApiConst
from dashboard_lib.dao_factory import StorageFactory
from logging_utils.logger import Logger
from utility.api_response import ApiResponse
from utility.edutil import EDUtility
from utility.smtp import SMTP
from utility.token_module import token_required, UserData
from . import Resource

issuer = 'femc'


class PermissionUserTwoFactorAuth(Resource):
    logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
    dao = StorageFactory(config).get_dao_factory().get_dao()

    @token_required(token_module)
    def post(self):
        logger = Logger().create('EMS API', level=logging_level, log_path=log_path)
        logger.info('permission_user_two_factor_auth')
        rtn_data = ApiResponse()
        rtn_data.Data = ''

        try:
            user_info: UserData = session[token_module.auth_session_key]
            user_id = user_info.user_id

            payload = request.get_json()
            if ApiConst.ENABLE.value in payload and payload[ApiConst.ENABLE.value] != "":
                enable = bool(payload[ApiConst.ENABLE.value])
            else:
                raise Exception("參數錯誤.")

            accept_submit = payload.get(ApiConst.ACCEPT_SUBMIT.value, False)

            if accept_submit:
                user = self.dao.get_users(_id=user_id)
                if user.empty:
                    raise Exception("找不到使用者。")
                else:
                    user = user.iloc[0]
                    iv = user['temp_iv']
                    two_factor_secret_key = user['temp_two_factor_secret_key']
                    message = self.dao.token_update_user_otp(
                        _id=user_id, iv=iv, two_factor_secret_key=two_factor_secret_key, enable_two_factor=True)
                    if message:
                        raise Exception(message)
            else:
                if enable:
                    secret_key = self.generate_secret_key()
                    totp_uri = f"otpauth://totp/{issuer}:{user_id}?secret={secret_key}&issuer={issuer}"
                    qr_buffer, qr_base64 = self.generate_qr_code_base64(totp_uri)

                    iv, encrypted_secret_key = EDUtility(config).aes_encrypt(secret_key)
                    message = self.dao.token_update_user_otp(
                        _id=user_id, temp_iv=iv, temp_two_factor_secret_key=encrypted_secret_key)
                    if message:
                        raise Exception(message)

                    msg, user_email, subject = self.email_format(user_id, qr_buffer)
                    if user_email is not None and user_email != "":
                        rtn_data = (SMTP(config, [user_email]).send_email(subject, message=msg))

                    rtn_data.Data = f'data:image/png;base64,{qr_base64}'
                else:
                    message = self.dao.token_update_user_otp(
                        _id=user_id, iv='', two_factor_secret_key='', enable_two_factor=False)

                    if message:
                        raise Exception(message)
        except Exception as e:
            rtn_data.Success = False
            rtn_data.Msg = str(e)
        return make_response(jsonify(rtn_data.serialized), 200)

    def email_format(self, _user_id, _qr_buffer):
        user_email = ''
        pd_user = self.dao.get_users(_id=_user_id)
        if not pd_user.empty and ApiConst.EMAIL.value in pd_user.columns:
            user_email = pd_user[ApiConst.EMAIL.value][0]
        else:
            return None, None, None

        msg = MIMEMultipart()
        subject = '[ 福能能源管理平台兩階段驗證 ]'
        current_date = datetime.now().strftime("%Y-%m-%d")
        from_content = f"""
                       <html>
                           <body>
                               <p>您好，你於 {current_date} 啟用兩階段驗證，</p>
                               <p>請使用 Google Authenticator 或 Microsoft Authenticator 掃描下方QR Code ，以取得登入驗證碼。</p>
                               <img src="cid:qr_code_image" alt="QR Code">
                           </body>
                       </html>
                       """
        msg.attach(MIMEText(from_content, 'html'))

        # qrcode 圖片加到訊息
        img = MIMEImage(_qr_buffer.getvalue())
        img.add_header('Content-ID', '<qr_code_image>')
        img.add_header('Content-Disposition', 'inline', filename='qrcode.png')
        msg.attach(img)

        return msg, user_email, subject

    @staticmethod
    def generate_qr_code_base64(data):
        qr = qrcode.main.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_buffer = BytesIO()
        img.save(qr_buffer, format="PNG")  # noqa
        qr_buffer.seek(0)

        qr_base64 = b64encode(qr_buffer.getvalue()).decode()
        return qr_buffer, qr_base64

    @staticmethod
    def generate_secret_key():
        """生成一個新的秘密金鑰"""
        return pyotp.random_base32()
