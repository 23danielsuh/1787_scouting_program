from __future__ import print_function
import numpy as np
import pandas as pd
from auth import spreadsheet_service
# from auth import drive_service
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sheet_id = '1uW-pBBW5-XOjCJ_b4iHtdY2PyA9WwCE0RvG1XCywtb4'



def update_values(spreadsheet_id, range_name, value_input_option,
                  _values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    # creds, _ = google.auth.default()
    # pylint: disable=maybe-no-member
    try:

        # service = build('sheets', 'v4', credentials=creds)
        values = [
            [
                # Cell values ...
                3, 5, 5
            ],
            # Additional rows ...
        ]
        values = pd.DataFrame(np.zeros((100, 3)))
        values = values.values.tolist()
        body = {
            'values': values
        }
        result = spreadsheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()

        batch_update_spreadsheet_request_body = {
            "requests": [
                {
                "addSheet": {
                    "properties": {
                    "title": "Deposits",
                    "gridProperties": {
                        "rowCount": 20,
                        "columnCount": 12
                    },
                    "tabColor": {
                        "red": 1.0,
                        "green": 0.3,
                        "blue": 0.4
                    }
                    }
                }
                }
            ]
            }

        request = spreadsheet_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_spreadsheet_request_body)
        # response = request.execute()
        # print(response)
        
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == '__main__':
    # Pass: spreadsheet_id,  range_name, value_input_option and  _values
    update_values("1mMOpwAWR2woBgi6s2YJKUehTTJBsD58680Mq_ZsXfec",
                  "A1:E200", "USER_ENTERED",
                  [
                      ['A', 'B'],
                      ['C', 'D']
                  ])