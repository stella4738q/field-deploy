from enum import Enum


class ConfigSession(Enum):
    SETTINGS = 'SETTINGS'
    SLACK_MESSAGE = 'SLACK_MESSAGE'
    LOGGER = 'LOGGER'
    SMTP = 'SMTP'
    FCM = 'FCM'


class SystemSettingConfigConst(Enum):
    JOB_ID = 'job_id'
    SOURCE = 'source'
    DESTINATION = 'destination'
    USE_SCHEDULE = 'use_schedule'
    SCHEDULE_TYPE = 'schedule_type'
    CRON_DAY_OF_WEEK = 'cron_day_of_week'
    CRON_HOUR = 'cron_hour'
    CRON_MINUTE = 'cron_minute'
    CRON_SECOND = 'cron_second'
    INTERVAL_UNIT = 'interval_unit'
    INTERVAL_VALUE = 'interval_value'
    EXECUTOR_ID = 'executor_id'


class IntervalUnit(Enum):
    YEAR = 'year'
    MONTH = 'month'
    DAY = 'day'
    MINUTES = 'minutes'
    HOURS = 'hours'
    SECONDS = 'seconds'


class ScheduleType(Enum):
    CRON = 'cron'
    INTERVAL = 'interval'


class LoggerConfigConst(Enum):
    LOGGING_LEVEL = 'logging_level'
    LOGGING_PATH = 'logging_path'
    LOG_TO_DB = 'log_to_db'


class DBType(Enum):
    MONGO = 'mongo'
    ORACLE = 'oracle'
    MSSQL = 'mssql'
    FILESYSTEM = 'filesystem'


class DataBaseConfigConst(Enum):
    DB_TYPE = 'db_type'
    URI = 'uri'
    PORT = 'port'
    USERNAME = 'username'
    PASSWORD = 'password'
    DATABASE_NAME = 'database_name'
    SID = 'sid'
    SCHEMA_NAME = 'schema_name'
    REPLICASET = 'replicaset'
    REPLICASET_LIST = 'replicaset_list'
    LIB_DIR = 'lib_dir'


class SlackConfigConst(Enum):
    TITLE = 'title'
    ENABLE = 'enable'
    SLACK_BOT_TOKEN = 'slack_bot_token'
    CHANNEL = 'channel'
    NOTIFY_WHO = 'notify_who'


class SMTPConfigConst(Enum):
    ACCOUNT = 'account'
    PASSWORD = 'password'
    PORT = 'port'
    IP = 'ip'
    TLS = 'tls'


class FCMConfigConst(Enum):
    TOKEN_PATH = 'token_path'
