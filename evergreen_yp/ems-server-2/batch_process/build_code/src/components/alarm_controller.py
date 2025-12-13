import datetime
import distutils.util
from abc import ABC, abstractmethod

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.constants import alarm_const
from src.constants.config_const import SlackConfigConst


class AlarmController:
    def __init__(self, config):
        self.slack_handler = SlackMsgr(config)

    def send_message(self, message):
        utc_now = datetime.datetime.utcnow()
        local_now = (utc_now + datetime.timedelta(hours=8))
        text = """
                {notify}
                :red_circle: {title}
                *Dag Execution Time*: {exec_date}
                *Message*: {message}
            """.format(
            notify='' if self.slack_handler.notify_who is None else self.slack_handler.notify_who,
            title=self.slack_handler.title,
            exec_date=local_now.strftime('%Y-%m-%d %H:%M:%S'),
            message=message
        )
        self.slack_handler.send(text)


class AbstractMsgr(ABC):
    @abstractmethod
    def send(self, message: str, **kwargs):
        pass

    @abstractmethod
    def file_upload(self, file_path, **kwargs):
        pass


class SlackMsgr(AbstractMsgr):
    def __init__(self, config):
        self.title = config[SlackConfigConst.TITLE.value]
        self.enable = distutils.util.strtobool(config[SlackConfigConst.ENABLE.value])
        slack_bot_token = config[SlackConfigConst.SLACK_BOT_TOKEN.value]
        self.client = WebClient(slack_bot_token)
        self.channel = config[SlackConfigConst.CHANNEL.value]
        notify_who_data = config[SlackConfigConst.NOTIFY_WHO.value]
        notify_who = [f'<@{alarm_const.MemberID.__getitem__(s.strip()).value}>' for s in notify_who_data.split(',')]
        self.notify_who = ','.join(notify_who)

    def send(self, message: str, **kwargs):
        channel = self.channel
        try:
            if self.enable:
                response = self.client.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            # # You will get a SlackApiError if "ok" is False
            # assert e.response['error']  # str like 'invalid_auth', 'channel_not_found'
            print(repr(e))
            raise

    def file_upload(self, file_path, **kwargs):
        channel = kwargs.get('channel')
        try:
            response = self.client.files_upload(channels=channel, file=file_path, title="Uploaded file:")
        except SlackApiError as e:
            # assert e.response['error']
            print(repr(e))
            raise
