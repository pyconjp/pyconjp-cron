#!/usr/bin/env python
'''
Slackのチャンネル一覧を生成する
'''

from slacker import Slacker

import settings
from google_api import get_sheets_service

# チャンネル一覧を書き込むスプレッドシートのID
SHEET_ID = '1Z93vxxC6zdSunO52-9hQpeGpBqQeFPIPLn2ayPRmtJY'


def get_channels_list():
    '''
    Slackのチャンネル一覧から必要な情報を返す

    https://api.slack.com/methods/channels.list
    '''
    slack = Slacker(settings.SLACK_TOKEN)
    r = slack.channels.list(exclude_archived=True)
    channels = []
    for channel in r.body['channels']:
        channel_info = {
            'id': channel['id'],
            'name': '#' + channel['name'],
            'topic': channel['topic']['value'],
            'purpose': channel['purpose']['value'],
            'members': channel['num_members'],
        }
        channels.append(channel_info)
    return channels


def store(channels):
    '''
    Slackのチャンネル情報をGoogleスプレッドシートに書き込む

    https://docs.google.com/spreadsheets/d/1Z93vxxC6zdSunO52-9hQpeGpBqQeFPIPLn2ayPRmtJY/edit#gid=0
    '''

    values = []
    # チャンネル情報を配列にする
    KEYS = ('name', 'id', 'members', 'purpose', 'topic')
    for channel in channels:
        # 辞書からKEYSに従った順番に値を取り出す
        values.append([channel[k] for k in KEYS])
    data = [
        {
            'range': 'A2:E100',
            'values': values,
        }
    ]
    body = {
        'valueInputOption': 'RAW',
        'data': data,
    }
    service = get_sheets_service()
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body).execute()


def main():
    '''
    Slackのチャンネル一覧情報を取得する
    '''
    # チャンネル一覧を取得
    channels = get_channels_list()
    # チャンネルの情報をスプレッドシートに書き出す
    store(channels)


if __name__ == '__main__':
    main()
