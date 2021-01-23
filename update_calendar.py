#!/usr/bin/python
"""
PyCon JP、PyCon JP スタッフのconnpassイベント情報を PyCon JP のGoogleカレンダー
に登録する

* https://pyconjp.connpass.com/ connpassグループID 137
* https://pyconjp-staff.connpass.com/ connpassグループID 1671
* connpass API: https://connpass.com/about/api/

* PyCon JP カレンダーID: bsn2855fnbngs1itml66l28ml8@group.calendar.google.com
"""

import logging
import os
from datetime import datetime

import requests
from dateutil import parser
from pytz import timezone

from google_api import get_calendar_service

# 以下のタイトルを含むイベントは登録対象から外す
NG_WORDS = ("懇親会", "spicy-food部", "Meat")

# カレンダーID
CAL_ID = "bsn2855fnbngs1itml66l28ml8@group.calendar.google.com"

# ログをファイルに出力する
BASENAME = os.path.basename(__file__).replace(".py", "")
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
filename = BASENAME + ".log"
logging.basicConfig(format=fmt, filename=filename, level=logging.INFO)
logger = logging.getLogger(BASENAME)


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


def get_calendar_event_id(calendar, event_url):
    """
    指定された URL のイベントがカレンダーに登録済か調べる

    :param calendar: カレンダーAPIに接続するためのサービス
    :param str event_url: connpassイベントのURL
    :return: GoogleカレンダーのイベントID(存在しない場合はNone)
    """
    event_id = None
    events = calendar.events().list(calendarId=CAL_ID, q=event_url).execute()
    if events["items"]:
        event = events["items"][0]
        event_id = event["id"]

    return event_id


def create_calendar_event_body(event):
    """
    connpassのevent情報をもとに、Google Calendarのイベント情報を生成する

    https://developers.google.com/google-apps/calendar/v3/reference/events/insert
    https://developers.google.com/google-apps/calendar/v3/reference/events/update

    event 情報(dict)の詳細

    * event_id: イベントID
    * title: タイトル
    * description: 概要
    * event_url: connpass.com上のURL
    * started_at: 開催日時(文字列)
    * ended_at: 終了日時(文字列)
    * address: 開催場所
    * place: 開催会場

    :param dict event: connpassのイベント情報
    :return: Google Calendarのイベント情報
    """
    # TODO: description をテキストにしたい
    # https://pypi.python.org/pypi/html2text/2016.9.19

    body = {
        "summary": event["title"],
        "description": '<a href="{0}">{0}</a>'.format(event["event_url"]),
        "start": {
            "dateTime": event["started_at"],
            "timeZone": "Asia/Tokyo",
        },
        "end": {
            "dateTime": event["ended_at"],
            "timeZone": "Asia/Tokyo",
        },
    }
    # 場所が設定されていたら登録する
    if event["address"]:
        body["location"] = "{address}({place})".format(**event)

    return body


def register_event_to_calendar(event):
    """
    イベント情報を PyCon JP カレンダーに登録する

    https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/calendar_v3.events.html

    :param dict event: connpassのイベント情報
    """
    # カレンダーAPIを使用するためにサービスを取得
    calendar = get_calendar_service()

    # 同一connpassイベントがカレンダーに登録済か調べる
    event_id = get_calendar_event_id(calendar, event["event_url"])

    # カレンダーに登録するためのイベント情報を作成する
    body = create_calendar_event_body(event)

    if event_id:
        # Googleカレンダーのイベントを更新する
        calendar.events().update(
            calendarId=CAL_ID, eventId=event_id, body=body
        ).execute()
        logger.info("Update calendar event: %s", event["title"])
    else:
        # Googleカレンダーにイベントを追加する
        calendar.events().insert(calendarId=CAL_ID, body=body).execute()
        logger.info("Insert calendar event: %s", event["title"])


def main():
    # 現在日時を取得
    jst_now = datetime.now().astimezone(timezone("Asia/Tokyo"))
    for series_id in 137, 1671:
        logger.debug("Get event info from connpass: %d", series_id)
        # connpass の API を実行する
        params = {"series_id": series_id}
        r = requests.get("https://connpass.com/api/v1/event/", params=params)
        # イベント情報を取得
        for event in r.json().get("events"):
            # 1日以内に更新されていなければ対象外
            updated_at = parser.parse(event["updated_at"])
            delta = jst_now - updated_at
            if delta.days > 0:
                continue

            # 開始日時が設定されていなければ対象外
            if not event["started_at"]:
                continue

            # 開始日時が未来のイベントでタイトルがOKのものを対象とする
            started_at = parser.parse(event["started_at"])
            if jst_now < started_at and is_ok_title(event["title"]):
                # イベントを PyCon JP カレンダーに登録する
                register_event_to_calendar(event)


if __name__ == "__main__":
    logger.info("Start script")
    main()
    logger.info("End script")
