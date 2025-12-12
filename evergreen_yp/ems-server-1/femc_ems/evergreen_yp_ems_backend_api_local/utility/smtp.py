import base64
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart

from email.header import Header
from logging_utils.logger import Logger
from utility.api_response  import ApiResponse
from apps.dashboard.constant import ConfigConstant
from apps.dashboard import log_path, logging_level


class SMTP:
    def __init__(self, config, receivers):
        self.config = config
        self.logger = Logger().create('Local EMS API', level=logging_level, log_path=log_path)
        self.receivers = receivers

    def send_email(self, subject, message):
        rtn_result = ApiResponse()
        try:
            account = self.config[ConfigConstant.APP.value][ConfigConstant.EMAIL_ACCOUNT.value]
            password = self.config[ConfigConstant.APP.value][ConfigConstant.EMAIL_PASSWORD.value]
            smtp_ip = "smtp.gmail.com"
            smtp_port = 587
            smtp_tls = 1

            if self.receivers is None or len(self.receivers) == 0:
                raise ValueError('There are empty receivers to send email.')

            if smtp_ip is None or smtp_port is None or account is None or password is None:
                raise ValueError('SMTP settings error, lose some parameter. (server, port, account or password)')

            msg = MIMEMultipart()
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = account
            msg['To'] = ', '.join(self.receivers)
            msg.attach(message)

            _smtp = None
            try:
                if smtp_tls:
                    self.logger.info('Connect with SSL')
                    try:
                        _smtp = smtplib.SMTP(host=smtp_ip, port=smtp_port)
                        _smtp.ehlo()
                    except (ValueError, ConnectionError) as ex:
                        self.logger(f"normal link smtp error: {ex}, try ssl.")
                        _smtp = smtplib.SMTP_SSL(host=smtp_ip, port=smtp_port)

                else:
                    self.logger.info('Connect smtp')
                    _smtp = smtplib.SMTP(host=smtp_ip, port=smtp_port)
                    _smtp.starttls()

                if smtp_port == 587:
                    _smtp.starttls(context=ssl.create_default_context())

                _smtp.ehlo()
                _smtp.login(user=account, password=password)
                _smtp.sendmail(from_addr=account, to_addrs=self.receivers, msg=msg.as_string())
                self.logger.info('Send email success.')
            except (ValueError, ConnectionError) as ex:
                rtn_result.success = False
                message = f"SMTP exception: {str(ex)}"
                rtn_result.msg = message
            finally:
                if _smtp:
                    _smtp.quit()
        except (ValueError, ConnectionError) as ex:
            self.logger.error(repr(ex))
            rtn_result.success = False
            rtn_result.msg = str(ex)
        return rtn_result

    def test_email(self, subject, message):
        self.send_email(subject, message)