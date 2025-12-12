import os
import jwt
from distutils.util import strtobool
from src.constants.config_const import ConfigSession, SettingConfigConst, SocketServerConst
from src.constants.foler_and_file_const import FolderAndFileConst
from src.utility.logger import MyLogger
from src.utility.utils import EventMessage


class EDUtility:
    def __init__(self, config):
        self.config = config

        # init logger
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        config_setting = config[ConfigSession.SETTINGS.value]
        logging_level = str(config_setting[SettingConfigConst.LOGGING_LEVEL.value])
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()

        # cert_key
        socket_setting = config[ConfigSession.WEB_SOCKET_SERVER.value]
        self.cert_key = socket_setting[SocketServerConst.CERT_KET.value]

    def data_encrypt(self, data) -> EventMessage:
        result = EventMessage()
        try:
            encoded_jwt = jwt.encode(data, self.cert_key, algorithm="HS256")
            result.Data = encoded_jwt
        except Exception as e:
            self.logger.error(f'data encrypt error: {e}')
            result.Success = False
            result.Message = str(e)
        return result

    def data_decrypt(self, token) -> EventMessage:
        result = EventMessage()
        try:
            data = jwt.decode(token, self.cert_key, algorithms=["HS256"])
            result.Data = data
        except Exception as e:
            self.logger.error(f'data decrypt error: {e}')
            result.Success = False
            result.Message = str(e)
        return result
