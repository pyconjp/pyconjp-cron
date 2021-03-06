#!/usr/bin/env python
"""
スプレッドシートに記入している内容からSNS(Twitter, Facebook)に通知するスクリプト
"""

import logging
from datetime import date, datetime, timedelta

import facebook
import tweepy
from dateutil import parser

import settings
from google_api import get_sheets_service

# スプレッドシートのID
SHEET_ID = "1lpa9p_dCyTckREf09-oA2C6ZAMACCrgD9W3HQSKeoSI"
# インターバルは5分
INTERVAL = 5
# 曜日の文字列
WEEK_STR = "月火水木金土日"

# ログをファイルに出力する
fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, filename="sns_notify.log", level=logging.INFO)
logger = logging.getLogger("sns_notify")


def is_valid_period(start: str, end: str) -> bool:
    """
    今日が start, end の範囲内かどうかを返す

    :params start: 通知開始日の文字列または空文字
    :params end: 通知終了日の文字列または空文字

    :return: True: 通知範囲内、False: 通知範囲外
    """

    # 文字列を date 型にする
    try:
        start_date = parser.parse(start).date()
    except ValueError:
        start_date = date(2000, 1, 1)  # 過去の日付にする
    try:
        end_date = parser.parse(end).date()
    except ValueError:
        end_date = date(3000, 1, 1)  # 未来の日付にする
    today = date.today()

    # 今日が範囲内かどうかを返す
    return start_date <= today <= end_date


def is_target_date(now: datetime, date_str: str, time_str: str) -> bool:
    """
    date, timeが指定範囲の場合に True を返す

    :param now: 現在時刻(datetime)
    :param date: 通知日(YYYY/MM/DD または曜日指定)
    :param time: 通知時刻
    """
    target_time = parser.parse(time_str)
    now_plus_interval = now + timedelta(minutes=INTERVAL)
    # 時間が範囲外なら False を返す
    if not now <= target_time < now_plus_interval:
        return False
    try:
        # 日付指定の場合は日付が同じかどうかをチェック
        target_date = parser.parse(date_str).date()
        return target_date == now.date()
    except ValueError:
        # 曜日を取得
        week_str = WEEK_STR[now.weekday()]
        return week_str in date_str


def twitter_notify(message: str, link: str) -> None:
    """
    指定されたメッセージを Twitter に通知する

    :param message: 送信するメッセージ
    :param link: 送信するURL
    """
    logger.info("twitter notify: %s", message)
    # Twitter に OAuth 認証する
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    # リンクがある場合は後ろにつける
    if link != "":
        message += " " + link
    # ハッシュタグを付けてメッセージを送信
    api.update_status("{} #pyconjp".format(message))


def facebook_notify(message: str, link: str) -> None:
    """
    指定されたメッセージを Facebook に通知する

    :param message: 送信するメッセージ
    :param link: 送信するURL
    """
    logger.info("facebook notify: %s", message)
    access_token = settings.FB_PAGE_ACCESS_TOKEN
    graph = facebook.GraphAPI(access_token=access_token, version="3.1")
    params = {"message": message}
    if link:
        params["link"] = link
    graph.put_object(settings.PAGE_ID, "feed", **params)


def sns_notify(row: list, now: datetime) -> None:
    """
    スプレッドシートのデータ1行分をSNSに通知する。
    データは以下の形式。

    1. 通知日(YYYY/MM/DD または曜日指定)
    2. 通知時刻
    3. 送信メッセージ
    4. 送信するURL
    5. 通知開始日
    6. 通知終了日
    7. twitter通知フラグ(1なら通知)
    8. facebook通知フラグ(1なら通知)

    :param row: スプレッドシートの1行分のデータ
    :param now: 現在時刻(datetime)
    """

    # データの件数が少なかったらなにもしない
    if len(row) < 7:
        return
    # 通知期間の範囲外ならなにもしない
    if not is_valid_period(row[4], row[5]):
        return
    # 通知対象日時じゃなかったらなにもしない
    if not is_target_date(now, row[0], row[1]):
        return
    # メッセージを送信する
    if row[6] == "1":
        twitter_notify(row[2], row[3])
    if row[7] == "1":
        facebook_notify(row[2], row[3])


def main() -> None:
    """
    PyCon JP Twitter/Facebook通知シートからデータを読み込んで通知する
    """
    logger.info("Start sns_notify")
    # 現在時刻(分まで)を取得
    now = datetime.now()
    now = datetime(now.year, now.month, now.day, now.hour, now.minute)
    logger.info("now: %s", now)

    service = get_sheets_service()
    # シートから全データを読み込む
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range="messages!A4:H")
        .execute()
    )
    for row in result.get("values", []):
        # 1行のデータを元にSNSへの通知を実行
        sns_notify(row, now)
    logger.info("End sns_notify")


if __name__ == "__main__":
    main()
