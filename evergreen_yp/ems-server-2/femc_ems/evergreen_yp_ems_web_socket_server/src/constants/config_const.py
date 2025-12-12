from enum import Enum


class ConfigSession(Enum):
    SETTINGS = 'SETTINGS'
    WEB_SOCKET_SERVER = 'WEB_SOCKET_SERVER'
    LINE_NOTIFY = 'LINE_NOTIFY'
    FEMC_NOTIFY = 'FEMC_NOTIFY'


class SettingConfigConst(Enum):
    LOGGING_LEVEL = 'logging_level'
    USE_SIM_DATA = 'use_sim_data'
    FILE_TIMEOUT_CHECK = 'file_timeout_check'
    ENV_CONTROLLER = 'env_controller'
    LOAD_FIXED_ATTR = 'load_fixed_attr'


class SocketServerConst(Enum):
    SERVER_HOST = 'host'
    SERVER_PORT = 'port'
    CERT_KET = 'cert_key'
    SSL = 'ssl'
    CERT_PATH = 'cert_path'


class SecurityAuthConst(Enum):
    SECRET_KEY = 'secret_key'
    SESSION_KEY = 'session_key'
    AUTH_ENABLE = 'auth_enable'
    REQUEST_HEADER = 'request_header'


class DestinationConfigConst(Enum):
    SOURCE_TYPE = 'source_type'
    MODBUS_PARSER = 'modbus_parser'
    RACK_COUNT = 'rack_count'
    HOST = 'host'
    PORT = 'port'
    USERNAME = 'username'
    PASSWORD = 'password'
    DATABASE_NAME = 'database_name'


class LineNotifyConst(Enum):
    TITLE = 'title'
    ENABLE = 'enable'
    URL = 'url'
    TOKEN = 'token'
    SHARE_TOKEN_PATH = 'share_token_path'


class FemcMessageConst(Enum):
    TITLE = 'title'
    ENABLE = 'enable'
    SECRET_KEY = 'secret_key'
    HEADER_KEY = 'header_key'
    URL = 'url'
