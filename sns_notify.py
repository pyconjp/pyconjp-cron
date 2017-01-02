#!/usr/bin/env python

from datetime import datetime, date

from dateutil import parser

from google_sheets import get_service

SHEET_ID = "1lpa9p_dCyTckREf09-oA2C6ZAMACCrgD9W3HQSKeoSI"


def is_valid_period(start, end):
    """
    今日が start, end の範囲内かどうかを返す

    :params start: 通知開始日の文字列または空文字
    :params end: 通知終了日の文字列または空文字

    :return: True: 通知範囲内、False: 通知範囲外
    """

    # 文字列を date 型にする
    try:
        start = parser.parse(start).date()
    except ValueError:
        start = date(2000, 1, 1)  # 過去の日付にする
    try:
        end = parser.parse(end).date()
    except ValueError:
        end = date(3000, 1, 1)  # 未来の日付にする
    today = date.today()

    # 今日が範囲内かどうかを返す
    return start <= today <= end


def sns_notify(row, now):
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
    # メッセージ送信する
    if row[6] == '1':
        pass
    if row[7] == '1':
        pass


def main():
    """
    PyCon JP Twitter/Facebook通知シートからデータを読み込んで通知する
    """
    now = datetime.now()
    service = get_service()
    # シートから全データを読み込む
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range='messages!A4:H').execute()
    for row in result.get('values', []):
        # 1行のデータを元にSNSへの通知を実行
        sns_notify(row, now)


if __name__ == '__main__':
    main()
