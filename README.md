# pyconjp-cron

* cron scripts for PyCon JP

```sh
$ git clone git@github.com:pyconjp/pyconjp-cron.git
$ cd pyconjp-cron
$ python3.5 -m venv env
$ . env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ python google_sheets.py # Google 認証を実行
(env) $ cp settings.py.sample settings.py
(env) $ vi settings.py
```

## Google への認証を準備する

* Google スプレッドシートにアクセスできるようにする。

### 1. Google API を有効にする

1. [Google API Console](https://console.developers.google.com/apis/api) を開く
2. 「プロジェクトを作成」→ `pyconjp-cron` などを指定して「作成」
3. 「APIを有効にする」を選択し、 `Google Seets API` を検索して有効にする
4. 「認証情報」メニュー→「OAuth同意画面」タブ→以下を入力して「保存」

    メールアドレス: 自分のメールアドレス
    ユーザーに表示するサービス名: `pyconjp-cron`

5. 「認証情報を作成」→「OAuth クライアント ID」→「その他」を選択→名前に `pyconjp-cron` などを指定して「作成」
6. OAuth クライアント IDがダイアログで表示されるので「OK」をクリックして閉じる
7. 右端のダウンロードボタンをクリックして、 `client_secret_XXXX.json` をダウンロードする
8. ファイル名を `client_secret.json` に変更して clone したディレクトリに置く

### 2. credentials を生成

- 下記の手順で `google_sheets.py` を実行すると、ブラウザが開いて API の許可を求める
- 任意の Google アカウントで API を許可する
- 成功すると `credentials.json` という証明書ファイルが生成される

```
$ . env/bin/activate
(env) $ python google_sheets.py
:
credentialsをcredentials.jsonに保存しました
Name, Major:
Alexandra, English
:
Will, Math
(env) $ ls credentials.json
credentials.json
```

## Twitter との認証情報を用意する

1. [Twitter Application Management](https://apps.twitter.com/ "Twitter Application Management") にPyCon JPのTwitterアカウント(@PyConJ)でログインする
2. 以下のような情報を入力してアプリケーションを作成する

  * Name: sns_notify
  * Description :SNS Notify script for PyCon JP
  * Website: https://github.com/pyconjp/pyconjp-cron
  * Callback URL: 空

3. `Key and Access Tokens` を選択→ `Create my access token` ボタンをクリック
4. 以下の4項目の値を `settings.py` に記入する

  * Consumer Key (API Key)
  * Consumer Secret (API Secre)
  * Access Token
  * Access Token Secret

## Facebook のアクセストークンの取得

1. [開発者向けFacebook](https://developers.facebook.com/ "開発者向けFacebook") にアクセスしする
2. `マイアプリ` → `新しいアプリを追加` を選択し、アプリケーションを登録する

  * 表示名: pyconjp_sns_notify
  * 連絡先メールアドレス: takanori@pycon.jp
  * カテゴリ: コミュニケーション

3. 作成したアプリケーションのダッシュボードが開くので `プラットフォームを選択` ボタンをクリックし `ウェブサイト` を選択する。Site URLには `http://localhost/` を指定する
4. app id と app sercret を `settings.py` に記述する
5. `get_fb_access_token.py` を実行し、手順に従ってアクセストークンを取得する
7. 成功するとアクセストークンが出力されるので、その内容を `settings.py` に書き込む
