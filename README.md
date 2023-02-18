# 1787 Scouting Program

Scouting program for Team 1787. Program will generate rankings based on several factors and create a new worksheet for every team. Code is not well documented currently, and is not very extensible for new seasons. 

### Usage in Terminal

1. Download the csv file from the Spreadsheet (File > Download > csv)
2. Open up your Terminal app
3. Download this repo's zip file and unzip it, or clone it with: `git clone https://github.com/23danielsuh/1787_scouting_program`
4. Enter the repository with `cd 1787_scouting_program`
5. Run `pip3 install -r requirements.txt` (make sure python is installed)
6. To run the program, run `python3 scouting_program.py --field_path="~/Downloads/path_to_field_scouting_csv.csv --pit_path ~/Downloads/path_to_pit_scouting_csv.csv"`
   1. For flag usage, run `python3 scouting_program.py --help`
7. Open `output.xlsx` in either Google Drive or Excel
