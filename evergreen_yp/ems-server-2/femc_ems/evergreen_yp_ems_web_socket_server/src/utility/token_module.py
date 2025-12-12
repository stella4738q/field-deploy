import datetime
import distutils.util
import os
import jwt

from distutils.util import strtobool
from functools import wraps

from flask import request, session

from src.constants.config_const import ConfigSession, SettingConfigConst, SecurityAuthConst
from src.constants.foler_and_file_const import FolderAndFileConst
from src.utility.logger import MyLogger
from src.utility.utils import EventMessage


class TokenModule:
    def __init__(self, config):
        self._config = config

        # init logger
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        config_setting = config[ConfigSession.SETTINGS.value]
        logging_level = str(config_setting[SettingConfigConst.LOGGING_LEVEL.value])
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()

        auth_setting = config[ConfigSession.SECURITY_AUTH.value]
        self.auth_header = auth_setting[SecurityAuthConst.REQUEST_HEADER.value]
        self.auth_security_key = auth_setting[SecurityAuthConst.SECRET_KEY.value]
        self.auth_session_key = auth_setting[SecurityAuthConst.SESSION_KEY.value]
        self.api_auth_enable = distutils.util.strtobool(auth_setting[SecurityAuthConst.AUTH_ENABLE.value])


def token_required(token_module: TokenModule):
    def out_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            result = EventMessage()
            token = None
            if token_module.auth_header.capitalize() in request.headers:
                token = request.headers[token_module.auth_header.capitalize()]
            if not token:
                if token_module.api_auth_enable:
                    result.Success = False
                    result.Msg = 'Token not found'
                    return result.to_dict()
                return f(*args, **kwargs)
            else:
                try:
                    # token check
                    data = jwt.decode(token, token_module.auth_security_key, verify=False,
                                      options={'verify_signature': False}, algorithms='HS256')
                    exp_data = datetime.datetime.utcfromtimestamp(data["exp_date"])
                    if token_module.api_auth_enable:
                        if datetime.datetime.utcnow() > exp_data:
                            raise Exception('Token is expired.')
                except Exception as e:
                    token_module.logger.error(e)
                    result.Success = False
                    result.Msg = f'Auth error: {str(e)}'
                    if 'Signature has expired' == str(e):
                        result.Msg = 'Token is expired.'
                    return result.to_dict()
                return f(*args, **kwargs)
        return decorator
    return out_decorator

