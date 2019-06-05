from dataclasses import dataclass
from typing import Iterable, Optional, Dict
import datetime
import pickle
import os.path
import pathlib

import googleapiclient.discovery
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
import google.oauth2.credentials
import iso8601


# 環境変数にした方がよいですが、ブログではわかりやすいように表示しています
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class ServiceBuilder:
    @classmethod
    def renew_token(cls, credentials: google.oauth2.credentials.Credentials) -> google.oauth2.credentials.Credentials:
        # google.oauth2.credentials.Credentialsは外部APIのクラス
        if credentials.expired and credentials.refresh_token:
            # 外部APIに接続
            credentials.refresh(Request())
        else:
            # from_client_secrets_file returns google_auth_oauthlib.flow.Flow object
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server()
        # Save the credentials for the next run
        # with open('token.pickle', 'wb') as f:
        #     pickle.dump(credentials, f)
        return credentials

    @classmethod
    def build(cls, credentials: google.oauth2.credentials.Credentials) -> googleapiclient.discovery.Resource:
        """トークンを元にServiceを生成します
        """

        # If there are no (valid) credentials available, let the user log in.
        # TODO: 42-43はrenew_tokenの先頭の方がよい
        if not credentials.valid:
            credentials = cls.renew_token(credentials)
        
        # 外部APIに接続
        return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)


@dataclass
class Event:
    summary: str
    start: datetime.datetime
    end: datetime.datetime


class EventAdapter:
    @classmethod
    def from_google_api(cls, google_event: Dict) -> Event:
        """GoogleAPIから取得したDict型のイベント情報をEventオブジェクトに変換します

        Dict型のままだと利用しない情報も含まれている、かつネストが深くて使いづらいため

        iso8601について
        https://pypi.org/project/iso8601/
        """
        return Event(
            summary=google_event.get('summary'),
            start=iso8601.parse_date(google_event.get('start').get('dateTime')),
            end=iso8601.parse_date(google_event.get('start').get('dateTime'))
        )


class EventManager:
    @classmethod
    def fetch_events(cls, number: int, service: googleapiclient.discovery.Resource) -> Iterable[Event]:
        """Google Calendar APIからイベントを取得します。

        number: int 取得するイベントの最大数
        service: イベントを取得するResourceオブジェクト
        """
        # service = ServiceBuilder.build()
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return []
        return [EventAdapter.from_google_api(event) for event in events]
