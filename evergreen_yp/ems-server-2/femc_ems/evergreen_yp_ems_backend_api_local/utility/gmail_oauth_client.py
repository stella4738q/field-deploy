from __future__ import print_function
import base64
import os.path
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://mail.google.com/']


class SMTP_GmailOAuthClient:
    def __init__(self, auth_file_path):
        self.creds = None
        token_file = os.path.join(auth_file_path, 'token.json')
        credentials = os.path.join(auth_file_path, 'credentials.json')
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def create_message(self, sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def send_message(self, user_id, message):
        response_data = {
            'Success': True,
        }
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message)
                       .execute())
        except Exception as error:
            print(error)
            response_data = {
                'Success': False,
            }
        return response_data