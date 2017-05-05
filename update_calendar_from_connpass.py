#!/usr/bin/python
"""
PyCon JP、PyCon JP スタッフのconnpassイベント情報を PyCon JP のGoogleカレンダー
に登録する

* https://pyconjp.connpass.com/ connpassグループID 137
* https://pyconjp-staff.connpass.com/ connpassグループID 1671

* PyCon JP カレンダーID: bsn2855fnbngs1itml66l28ml8@group.calendar.google.com

* connpass API: https://connpass.com/about/api/
"""

from datetime import datetime

import requests
from dateutil import parser
from pytz import timezone


# 以下のタイトルを含むイベントは登録対象から外す
NG_WORDS = ('懇親会', 'spicy-food部', 'Meat')


def is_ok_title(title):
    """
    タイトルにNGワードを含んでいないかを確認する

    :param str title: イベントのタイトル
    :return: True: 含んでいない(OK)、False: 含んでいる(NG)
    """
    for word in NG_WORDS:
        if word in title:
            return False
    return True


def register_event_to_calendar(event):
    """
    イベント情報を PyCon JP カレンダーに登録する

    :param dict event: イベント情報
    """
    event_id = event['event_id'] # イベントID
    title = event['title'] # タイトル
    description = event['description'] # 概要
    event_url = event['event_url'] # connpass.com上のURL
    started_at = parser.parse(event['started_at']) # 開催日時
    ended_at = parser.parse(event['ended_at']) # 終了日時
    address = event['address'] # 開催場所
    place = event['place'] # 開催会場
    # TODO: description をテキストにしたい
    # https://pypi.python.org/pypi/html2text/2016.9.19

    
def main():
    # 現在日時を取得
    jst_now = datetime.now().astimezone(timezone('Asia/Tokyo'))
    for series_id in 137, 1671:
        # connpass の API を実行する
        params = {
            'series_id': series_id
        }
        r = requests.get('https://connpass.com/api/v1/event/', params=params)
        # イベント情報を取得
        for event in r.json().get('events'):
            # 1日以内に更新されていなければ対象外
            updated_at = parser.parse(event['updated_at'])
            delta = jst_now - updated_at
            if delta.days > 0:
                continue

            # 開始日時が設定されていなければ対象外
            if not event['started_at']:
                continue

            # 開始日時が未来のイベントでタイトルがOKのものを対象とする
            started_at = parser.parse(event['started_at'])
            if jst_now < started_at and is_ok_title(event['title']):
                # イベントを PyCon JP カレンダーに登録する
                register_event_to_calendar(event)


if __name__ == '__main__':
    main()

