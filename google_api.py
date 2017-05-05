import os.path

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = [
    # Google Sheets API
    # https://developers.google.com/sheets/api/guides/authorizing
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    # Google Calendar
    # https://developers.google.com/google-apps/calendar/auth
    'https://www.googleapis.com/auth/calendar',
]
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'pyconjp-cron'
CREDENTIAL_FILE = 'credentials.json'


def get_sheets_service():
    """
    Google Sheets API のサービスを取得する
    """
    return get_service('sheets', 'v4')


def get_calendar_service():
    """
    Google Calendar API のサービスを取得する
    """
    return get_service('calendar', 'v3')


def get_service(name, version):
    """
    指定された名前とバージョンのサービスを取得する
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build(name, version, http=http)
    return service


def get_credentials():
    """
    credentialsファイルを生成する
    """
    dirname = os.path.dirname(__file__)
    credential_path = os.path.join(dirname, CREDENTIAL_FILE)
    client_secret_file = os.path.join(dirname, CLIENT_SECRET_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('credentialsを{}に保存しました'.format(credential_path))
    return credentials


def main():
    service = get_sheets_service()
    spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    rangeName = 'Class Data!A2:E'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))

            
if __name__ == '__main__':
    main()
