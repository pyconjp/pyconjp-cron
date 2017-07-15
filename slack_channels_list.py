#!/usr/bin/env python
'''
Slackのチャンネル一覧を生成する
'''

from slacker import Slacker

from google_api import get_sheets_service
import settings


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
            'name': channel['name'],
            'topic': channel['topic']['value'],
            'purpose': channel['purpose']['value'],
            'members': channel['num_members'],
        }
        channels.append(channel_info)
    return channels


def main():
    '''
    Slackのチャンネル一覧情報を取得する
    '''
    channels = get_channels_list()
    for channel in channels:
        print(channel['name'])
    #print(channels)


if __name__ == '__main__':
    main()
