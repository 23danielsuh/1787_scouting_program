# 1787 Scouting Program

Scouting program for Team 1787. Program will generate rankings based on several factors and create a new worksheet for every team. Code is not well documented currently, and is not very extensible for new seasons. Code efficiency is also bad, but performance is okay (<5 seconds).

Tested using OSX and Python 3.10 (**IMPORTANT: REQUIRES PYTHON >=3.10**)

### Usage in Terminal

1. Download the csv file from the Spreadsheet (File > Download > csv)
2. Open up your Terminal app
3. Download this repo's zip file and unzip it, or clone it with: `git clone https://github.com/23danielsuh/1787_scouting_program`
4. Enter the repository with `cd 1787_scouting_program`
5. Run `python3 --version`. Ensure that it says Python 3.10. If not, install the latest version of python from the website.
6. Run `pip3 install -r requirements.txt` (make sure python is installed)
7. To run the program, run `python3 scouting_program.py --path="~/Downloads/name_of_csv.csv"`
   1. For flag usage, run `python3 scouting_program.py --help`
8. Open `output.xlsx` in either Google Drive or Excel

### API Usage (Warning: Difficult to Set Up / Debug)

1. To automatically read data from Sheets API, you will need to set up a service account on Google Cloud (https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/)
2. Share spreadsheet with the email given by the service account
3. Download the JSON file, and change the path in `auth.py` to the download JSON file path
4. Get the Spreadsheet ID (docs.google.com/spreadsheets/SPREADSHEET_ID/edit...)
5. Change variable `spreadsheet_id` in `scouting_program.py` to the spreadsheet ID you found
6. Should work now
