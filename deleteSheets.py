from __future__ import print_function
import pickle
from auth import spreadsheet_service

with open("test", "rb") as fp:  # Unpickling
    sheetIds = pickle.load(fp)

for sheetId in sheetIds:
    print(sheetId, type(sheetId))
    batch_update_spreadsheet_request_body = {
        "requests": [
            {
                "deleteSheet": {
                    "sheetId": sheetId
                }
            }
        ]
    }

    spreadsheet_id = '1wyS8yFLIZZdr23nP2SdYWx4bDEFCmUC611Rfd9_OUvM'
    try:
        request = spreadsheet_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                 body=batch_update_spreadsheet_request_body).execute()
    except:
        continue
