import base64
import distutils
import logging
import os

import jwt
from distutils.util import strtobool

from dashboard_lib.constant import ConfigConstant
from logging_utils import Logger
from utility.api_response import ApiResponse

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad


class EDUtility:
    def __init__(self, config):
        self._config = config
        setting_config = config[ConfigConstant.APP.value]

        # init logger
        log_path = setting_config[ConfigConstant.LOG_PATH.value]
        self.logger = Logger().create('TokenModule', level=logging.INFO, log_path=log_path)

        # Auth
        self.auth_header = setting_config[ConfigConstant.REQUEST_HEADER.value]
        self.auth_security_key = setting_config[ConfigConstant.SECRET_KEY.value]
        self.auth_session_key = setting_config[ConfigConstant.SESSION_KEY.value]
        self.api_auth_enable = distutils.util.strtobool(setting_config[ConfigConstant.AUTH_ENABLE.value])

        # otp
        self.aes_key = setting_config[ConfigConstant.OTP_AES_KEY.value].ljust(16, '0')[:16].encode()

    def data_encrypt(self, data) -> ApiResponse:
        result = ApiResponse()
        try:
            encoded_jwt = jwt.encode(data, self.auth_security_key, algorithm="HS256")
            result.Data = encoded_jwt
        except Exception as e:
            self.logger.error(f'data encrypt error: {e}')
            result.Success = False
            result.Msg = str(e)
        return result

    def data_decrypt(self, token) -> ApiResponse:
        result = ApiResponse()
        try:
            data = jwt.decode(token, self.auth_security_key, algorithms=["HS256"])
            result.Data = data
        except Exception as e:
            self.logger.error(f'data decrypt error: {e}')
            result.Success = False
            result.Msg = str(e)
        return result

    def aes_encrypt(self, data):
        """
        AES 加密函數
        :param data: 要加密的資料
        :return: (iv_base64, encrypted_data_base64) 元組，包含 base64 編碼的 IV 和加密資料
        """
        # 生成 16 位元組的隨機 IV
        iv = os.urandom(16)

        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))

        # 轉換為 base64 字串
        iv_base64 = base64.b64encode(iv).decode()
        encrypted_data_base64 = base64.b64encode(encrypted_data).decode()

        return iv_base64, encrypted_data_base64

    def aes_decrypt(self, encrypted_data, iv):
        """
        解密資料
        :param encrypted_data: 加密的資料
        :param iv: 初始化向量
        :return: 解密後的字串
        """
        cipher = AES.new(self.aes_key, AES.MODE_CBC, base64.b64decode(iv))
        decrypted_data = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
        return decrypted_data.decode()
