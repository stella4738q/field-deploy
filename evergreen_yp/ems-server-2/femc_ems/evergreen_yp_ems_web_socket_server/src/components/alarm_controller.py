import os

import copy
import datetime
import json
import requests
from abc import ABC, abstractmethod
from itertools import groupby

from src.constants.config_const import ConfigSession, FemcMessageConst, SettingConfigConst, LineNotifyConst
from src.utility.logger import MyLogger


class ApiResponse:
    def __init__(self, success=True, message='Success', data=None):
        self.success = success
        self.message = message
        self.data = data

    @property
    def serialized(self):
        return self.__dict__


class WarningData:
    def __init__(self, level=0, code=None, name=None, time=None):
        self.level = level
        self.code = code
        self.name = name
        self.start_tme: datetime = time

    def encode(self):
        return {
            "level": self.level,
            "code": self.code,
            "name": self.name,
            "start_tme": str(self.start_tme)
        }


class AlarmController:
    def __init__(self, config):
        self.line_notify_handler = LineNotify(config)
        self.femc_msg_handler = FemcNotify(config)
        self.alarm_summary = list()

        config_setting = config[ConfigSession.SETTINGS.value]
        logging_level = str(config_setting[SettingConfigConst.LOGGING_LEVEL.value])
        my_logger = MyLogger(self.__class__.__name__, logging_level)
        self.logger = my_logger.get()

    def reset_message(self):
        self.alarm_summary = list()

    def add_message(self, code, message):
        utc_now = datetime.datetime.utcnow()
        local_now = (utc_now + datetime.timedelta(hours=8))
        current_time = local_now.strftime("%Y/%m/%d %H:%M:%S")
        wd = WarningData(2, code, message, current_time)
        self.alarm_summary.append(wd)

    def send_message(self, message):
        if self.line_notify_handler.enable:
            text = f"[{self.line_notify_handler.title}]\n{message}"
            self.line_notify_handler.send(text)

        if self.femc_msg_handler.enable:
            text = f"[{self.femc_msg_handler.title}]\n{message}"
            self.femc_msg_handler.send(text)

    def get_alarm_summary(self):
        if len(self.alarm_summary) > 0:
            data_sort = sorted(self.alarm_summary, key=lambda x: x.code)
            group_value = groupby(data_sort, key=lambda x: x.code)
            group_data = [(key, list(group)) for key, group in group_value]
            return group_data
        else:
            return list()


class AbstractMsgr(ABC):
    @abstractmethod
    def send(self, message: str, **kwargs):
        pass

    @abstractmethod
    def file_upload(self, file_path, **kwargs):
        pass


class LineNotify(AbstractMsgr):
    """
    表情貼圖清單：https://developers.line.biz/en/docs/messaging-api/sticker-list/
    """
    def __init__(self, config):
        line_notify_config = config.get(ConfigSession.LINE_NOTIFY.value, None)
        if line_notify_config is not None:
            # Ttile
            self.title = line_notify_config.get(LineNotifyConst.TITLE.value, '')
            # Enable
            self.enable = line_notify_config[LineNotifyConst.ENABLE.value] == '1'
            # url
            self.url = line_notify_config[LineNotifyConst.URL.value]
            # Token
            self.token = line_notify_config[LineNotifyConst.TOKEN.value]
            # UseShareFile
            self.share_token_path = line_notify_config.get(LineNotifyConst.SHARE_TOKEN_PATH.value, None)
        else:
            self.enable = False

    def send(self, message: str, **kwargs):
        try:
            headers = {'Authorization': 'Bearer ' + self.token}
            data = {
                'message': message,
                # 'stickerPackageId': '6136',
                # 'stickerId': '10551376'
            }
            requests.post(self.url, headers=headers, data=data)

            if self.share_token_path:
                with open(os.path.join(self.share_token_path, "line_notify.txt"), 'r') as file:
                    token = file.read()

                if token.strip():
                    temp_token = [t.strip() for t in token.split(',')]
                    for tk in temp_token:
                        headers = {'Authorization': 'Bearer ' + tk}
                        data = {
                            'message': message
                        }
                        requests.post(self.url, headers=headers, data=data)
        except Exception as e:
            print(repr(e))

    def file_upload(self, file_path, **kwargs):
        raise NotImplementedError


class FemcNotify(AbstractMsgr):
    def __init__(self, config):
        femc_config = config.get(ConfigSession.FEMC_NOTIFY.value, None)
        if femc_config is not None:
            self.enable = femc_config[FemcMessageConst.ENABLE.value] == '1'
            self.title = femc_config.get(FemcMessageConst.TITLE.value, '')
            self.url = femc_config[FemcMessageConst.URL.value]
            self.header_key = femc_config[FemcMessageConst.HEADER_KEY.value]
            self.secret_key = femc_config[FemcMessageConst.SECRET_KEY.value]
            self.headers = {'Content-Type': 'application/json', self.header_key: self.secret_key}
            self.message_template = {
              "msg_type": "A",
              "subject": self.title,
              "content": None
            }
        else:
            self.enable = False

    def send(self, message: str, **kwargs) -> ApiResponse:
        return_data = ApiResponse()
        try:
            send_msg = copy.deepcopy(self.message_template)
            send_msg['content'] = message  # noqa
            params = json.dumps(send_msg)
            response = requests.post(url=self.url, data=params, headers=self.headers, verify=False)
            contents = response.content.decode("utf-8").replace("'", '"')
            data_dict = json.loads(contents)
            resp_data = ApiResponse(**data_dict)
            if resp_data.success:
                return_data.data = resp_data.data
            else:
                raise Exception(resp_data.message)
        except Exception as e:
            return_data.success = False
            return_data.msg = str(e)
        return return_data

    def file_upload(self, file_path, **kwargs):
        raise NotImplementedError
