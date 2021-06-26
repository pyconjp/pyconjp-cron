import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = [
    # Google Sheets API
    # https://developers.google.com/sheets/api/guides/authorizing
    "https://www.googleapis.com/auth/spreadsheets",
    # Google Calendar
    # https://developers.google.com/google-apps/calendar/auth
    "https://www.googleapis.com/auth/calendar",
]

APPLICATION_NAME = "pyconjp-cron"
CREDENTIAL_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_sheets_service() -> Resource:
    """
    Google Sheets API のサービスを取得する
    """
    return get_service("sheets", "v4")


def get_calendar_service() -> Resource:
    """
    Google Calendar API のサービスを取得する
    """
    return get_service("calendar", "v3")


def get_service(name: str, version: str) -> Resource:
    """指定された Google API に接続する
    name: APIの名前
    version: APIのバージョン
    scope: OAuth のスコープを指定する
    serviceオブジェクトを返す
    """
    credentials = get_credentials()
    service = build(name, version, credentials=credentials)
    return service


def get_credentials():
    """
    credentials情報を作成して返す
    """

    creds = None

    dirname = os.path.dirname(__file__)
    credential_file = os.path.join(dirname, CREDENTIAL_FILE)
    token_file = os.path.join(dirname, TOKEN_FILE)

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return creds


def main():
    service = get_sheets_service()
    spreadsheetId = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    rangeName = "Class Data!A2:E"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheetId, range=rangeName)
        .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")
    else:
        print("Name, Major:")
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print("%s, %s" % (row[0], row[4]))


if __name__ == "__main__":
    main()
