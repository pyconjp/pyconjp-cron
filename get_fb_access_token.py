import facebook
import requests

import settings

URL = 'https://graph.facebook.com/oauth/access_token'


def get_user_long_token(user_short_token):
    import pdb
    pdb.set_trace()
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': settings.APP_ID,
        'client_secret': settings.APP_SECRET,
        'fb_exchange_token': user_short_token,
    }
    r = requests.get(URL, params=params)
    user_long_token = r.json()['access_token']
    return user_long_token


def get_permanent_page_token(user_long_token):
    graph = facebook.GraphAPI(access_token=user_long_token, version="2.9")
    pages_data = graph.get_object("/me/accounts")

    for item in pages_data['data']:
        if item['id'] == settings.PAGE_ID:
            page_token = item['access_token']

    return page_token


def main():
    """
    Facebook のアクセストークンを取得する手順を実行する
    """
    print('下記ページからユーザーアクセストークンを取得')
    print('https://developers.facebook.com/tools/explorer/')
    user_short_token = input('> ')

    user_long_token = get_user_long_token(user_short_token)
    page_token = get_permanent_page_token(user_long_token)
    
    print('以下の記述を settings.py に追加してください')
    print("FB_ACCESS_TOKEN = '{}'".format(user_long_token))
    print("FB_PAGE_ACCESS_TOKEN = '{}'".format(page_token))


if __name__ == '__main__':
    main()
