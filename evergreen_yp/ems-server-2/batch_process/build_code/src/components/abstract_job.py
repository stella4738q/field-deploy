import distutils.util
import logging
from abc import ABCMeta
from datetime import datetime

from src.components.alarm_controller import AlarmController
from src.components.batch_result import BatchResult
from src.constants.config_const import LoggerConfigConst, SystemSettingConfigConst
from src.dao.dao_factory import StorageFactory


class AbstractJob(metaclass=ABCMeta):
    def __init__(self, source_dao, destination_dao, alarm_controller, log_config, settings_config,
                 input_start_date=None, input_end_date=None):
        self.input_start_date = input_start_date
        self.input_end_date = input_end_date
        self.start_date = None
        self.end_date = None
        self.alarm_controller: AlarmController = alarm_controller
        self.source_dao = source_dao
        self.destination_dao = destination_dao

        self.log_config = log_config
        self.logging_level = log_config[LoggerConfigConst.LOGGING_LEVEL.value]
        self.log_base_path = log_config[LoggerConfigConst.LOGGING_PATH.value]

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.logging_level)

        self.log_dao = None
        self.__init_logger_dao__()

        self.executor_id = settings_config[SystemSettingConfigConst.EXECUTOR_ID.value]
        self.creator = {
            "created_on": datetime.now(),
            "created_by": self.executor_id,
            "created_name": "batch_process"
        }
        self.modifier = {
            "modified_on": datetime.now(),
            "modified_by": self.executor_id,
            "modified_name": "batch_process"
        }

    def __init_logger_dao__(self):
        log_to_db = distutils.util.strtobool(self.log_config[LoggerConfigConst.LOG_TO_DB.value])
        if log_to_db:
            self.log_dao = StorageFactory(self.log_config).get_dao()

    def send_alarm(self, message):
        self.alarm_controller.send_message(message)

    def insert_log(self, result: BatchResult):
        if self.log_dao:
            result.finish_time = datetime.now()
            result.get_spend_time()
            self.log_dao.write_log(result)

    def get_bu_management_device_token(self, bu_id, dao_type=1, is_management=True, is_foreman=False):
        device_token_list = list()
        user_list = list()
        dao = self.source_dao if dao_type == 0 else self.destination_dao
        user_bu_df = dao.get_user_business_unit(bu_id, is_management=is_management, is_foreman=is_foreman)
        if not user_bu_df.empty:
            user_id = user_bu_df['user_id'].tolist()
            user_df = dao.get_users(_id=user_id)
            if not user_df.empty:
                device_token_list = user_df['device_token'].tolist()
                for idx, value in user_df.iterrows():
                    user_dict = {
                        "id": value['_id'],
                        "name": value['name'],
                        "read": False
                    }
                    user_list.append(user_dict)
        return device_token_list, user_list

    def initial_data(self):
        ...

    def execute(self):
        ...
