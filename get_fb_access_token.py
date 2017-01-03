import requests
from requests import Request

import settings


def step1_oauth():
    """
    ステップ1: OAuth 認証を行う
    """
    url = 'https://www.facebook.com/dialog/oauth'
    params = {
        'redirect_uri': 'http://localhost/',
        'client_id': settings.APP_ID,
        'scope': ('manage_pages', 'publish_actions', 'publish_pages'),
    }
    prepped = Request('GET', url, params=params).prepare()
    print("ステップ1: OAuth 認証を行う")
    print("次のURLをWebブラウザに入力し、Facebook上で認証してください")
    print(prepped.url)
    print()


def step2_get_access_token():
    """
    ステップ2: アクセストークンを取得する

    :return: アクセストークン
    """
    print("ステップ2: アクセストークンを取得する")
    print("ステップ1で返ってきたURLの code= 以降を入力してください")
    code = input(">")

    url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        'client_id': settings.APP_ID,
        'client_secret': settings.APP_SECRET,
        'redirect_uri': 'http://localhost/',
        'code': code
        }
    r = requests.get(url, params=params)
    access_token = ''
    for param in r.text.split('&'):
        key, value = param.split('=', 2)
        print(key, value)
        if key == 'access_token':
            access_token = value
            print("アクセストークンを取得しました")
            print()

    return access_token


def step3_get_page_access_token(access_token):
    """
    ステップ3: ページアクセストークンを取得する

    :return: ページアクセストークン
    """
    print("ステップ3: ページアクセストークンを取得する")
    url = 'https://graph.facebook.com/me/accounts'
    params = {
        'access_token': access_token,
    }
    r = requests.get(url, params=params)
    rjson = r.json()
    for page in rjson.get('data', []):
        if page['id'] == settings.PAGE_ID:
            page_access_token = page['access_token']
            print("ページアクセストークンを取得しました")
            print()
    return page_access_token


def main():
    """
    Facebook のアクセストークンを取得する手順を実行する
    """
    # ステップ1: OAuth 認証を行う
    step1_oauth()
    # ステップ2: アクセストークンを取得する
    access_token = step2_get_access_token()
    # ステップ3: アクセストークンを交換する
    page_access_token = step3_get_page_access_token(access_token)

    print('以下の記述を settings.py に追加してください')
    print("FB_ACCESS_TOKEN = '{}'".format(access_token))
    print("FB_PAGE_ACCESS_TOKEN = '{}'".format(page_access_token))


if __name__ == '__main__':
    main()
