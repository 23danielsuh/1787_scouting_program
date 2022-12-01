from __future__ import print_function
from auth import spreadsheet_service
from auth import drive_service
def create():
    spreadsheet_details = {
    'properties': {
        'title': 'Python-google-sheets-demo'
        }
    }
    sheet = spreadsheet_service.spreadsheets().create(body=spreadsheet_details,
                                    fields='spreadsheetId').execute()
    sheetId = sheet.get('spreadsheetId')
    print('Spreadsheet ID: {0}'.format(sheetId))
    permission1 = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': '23denial@gmail.com'
    }
    drive_service.permissions().create(fileId=sheetId, body=permission1).execute()
    return sheetId
def read_range():
    range_name = 'Sheet1!A1:H1'
    spreadsheet_id = '1JCEHwIa4ZzwAiKGmAnWGfbjeVCH_tWZF6MkIU0zICwM'
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id, range=range_name).execute()
    rows = result.get('values', [])
    print('{0} rows retrieved.'.format(len(rows)))
    print('{0} rows retrieved.'.format(rows))
    return rows
def write_range():
    spreadsheet_id = create()
    range_name = 'Sheet1!A1:H1'
    values = read_range()
    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    result = spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
write_range()