import numpy as np
from collections import defaultdict
import argparse
from scipy import stats
import pandas as pd
import xlsxwriter
from colour import Color

workbook = xlsxwriter.Workbook('output.xlsx')
writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

data_dict = defaultdict()


def create_dict_dataframe(df, team_number):
    """
    Takes a team number and generates a DataFrame of the scouting data from that team number

    Args:
        df (pd.DataFrame): DataFrame with all the data
        team_number (int): The team number to get data for

    Returns:
        pd.DataFrame: subset of df with the data
    """
    return df[df['team_number'] == team_number]


def string_to_max(s):
    """
    Takes in a string of a list and returns the maximum of the list

    Args:
        s (str): string of a list (n1, n2, n3, ...)

    Returns:
        int: maximum of the list
    """
    lst = s.split(', ')
    new_lst = []

    for num in lst:
        new_lst.append(int(num))

    return max(new_lst)


def assign_climb_points(x):
    """
    Assigns climb points for the spreadsheet text

    Args:
        x (str): string with what the spreadsheet says

    Returns:
        int: number of climb points gained from climb
    """
    ret = 0
    if x == 'Traversal Rung (4)':
        ret = 15
    elif x == 'High Rung (3)':
        ret = 10
    elif x == 'Mid Rung (2)':
        ret = 6
    elif x == 'Low Rung (1)':
        ret = 4

    return ret


def get_shooter_points(lower_hub, upper_hub, in_auto):
    """
    Gets the total number of points gathered

    Args:
        lower_hub (int): number of balls scored in lower hub
        upper_hub (int): number of balls scored in upper hub
        in_auto (bool): boolean for if mode is auto or teleop

    Returns:
        int: total number of points scored
    """
    multiplier = (1, 2)
    if in_auto:
        multiplier = (2, 4)

    return lower_hub * multiplier[0] + upper_hub * multiplier[1]


def process_dataframe(init_df):
    """
    Processes the DataFrame to be in a better format for use

    Args:
        init_df (pd.DataFrame): DataFrame to format

    Returns:
        pd.DataFrame: Formatted DataFrame
    """
    df = init_df.drop(['email'], axis=1)

    # assuming only 2 days of qualifications
    df['time'] = df['time'].apply(lambda x: x.split(' ')[0])

    # very, very inefficient code...
    dates = df['time']
    dates = dates.sort_values()
    if dates.iloc[0] != dates.iloc[-1]:
        dates = dates.replace(dates.iloc[0], 1)
        dates = dates.replace(dates.iloc[-1], 2)
    else:
        dates = dates.replace(dates.iloc[0], 1)

    df['time'] = dates

    df['name'] = df['name'].apply(lambda x: x.strip())
    df['team_number'] = pd.to_numeric(df['team_number'])
    df['qual_number'] = pd.to_numeric(df['qual_number'])

    df['taxi'] = df['taxi'].replace('Yes', 2)
    df['taxi'] = df['taxi'].replace('No', 0)

    # lots of boilerplate :)
    df['auto_upper_hub'] = df['auto_upper_hub'].apply(
        lambda x: max(map(int, x.split(', '))))
    df['auto_lower_hub'] = df['auto_lower_hub'].apply(
        lambda x: max(map(int, x.split(', '))))

    df['total_auto_points'] = get_shooter_points(
        df['auto_lower_hub'], df['auto_upper_hub'], True)

    df['teleop_upper_hub'] = df['teleop_upper_hub'].apply(
        lambda x: max(map(int, x.split(', '))))
    df['teleop_lower_hub'] = df['teleop_lower_hub'].apply(
        lambda x: max(map(int, x.split(', '))))

    df['total_teleop_points'] = get_shooter_points(
        df['teleop_lower_hub'], df['teleop_upper_hub'], False)

    df['climb'] = df['climb'].apply(lambda x: assign_climb_points(x))
    df['defense'] = df['defense'].apply(lambda x: x.lower())

    df['total_points'] = df['total_auto_points'] + \
        df['total_teleop_points'] + df['climb'] + df['taxi']

    # probably useless, but takes care of a few corner cases
    df = df.sort_values(by=['qual_number'])

    return df


def get_dataframe(spreadsheet_id, path):
    """
    Turns a spreadsheet from a csv or sheets API into a Pandas DataFrame

    Args:
        spreadsheet_id (str): ID of the spreadsheet (check README.md for how to find this)
        path (str): If path is 'USE_API', program will use API. Otherwise, it will use the provided path

    Returns:   
        pd.DataFrame: DataFrame created from the spreadsheet
    """
    columns = ['time', 'email', 'name', 'team_number', 'qual_number', 'taxi', 'auto_upper_hub', 'auto_lower_hub',
               'teleop_upper_hub', 'teleop_lower_hub', 'climb', 'defense', 'written_information']

    print(f'Using CSV with path: {path}')
    df = pd.read_csv(path)
    df.columns = columns
    df = process_dataframe(df)
    return df


def get_teams(df, min_points):
    """
    Gets all of the teams that meet a certain threshold of min_points

    Args:
        df (pd.DataFrame): DataFrame to get the teams from
        min_points (int): minimum number of points for a team to be considered

    Returns:
        list: a list of the teams to be considered
    """

    l = list(pd.unique(df['team_number']))
    l.sort()

    ret = []
    for team in l:
        if df[df['team_number'] == team]['total_points'].mean() >= min_points:
            ret.append(team)

    return ret


sheetIds = []


def write_data(team, data):
    """
    Writes data (point values) for a given team

    Args:
        team (int): team to write the data for
        data (pd.DataFrame): DataFrame with data for the team
    """

    raw_data = data[['qual_number', 'total_auto_points',
                     'total_teleop_points', 'climb', 'total_points']]

    average_auto = round(data['total_auto_points'].mean(
        axis=0) + data['taxi'].mean(axis=0), 2)
    average_tele = round(data['total_teleop_points'].mean(axis=0), 2)
    average_climb = round(data['climb'].mean(axis=0), 2)
    average_total_points = round(data['total_points'].mean(axis=0), 2)

    raw_data.columns = ['Qualification number', 'Auto Points',
                        'Teleop Points', 'Climb Points', 'Total Points']
    averages = pd.DataFrame([['N/A', average_auto, average_tele, average_climb, average_total_points]],
                            columns=raw_data.columns)
    raw_data = pd.concat([raw_data, averages])

    left_hand_column = [''] * len(raw_data)
    left_hand_column[-1] = 'Averages:'
    raw_data.insert(0, '', left_hand_column, True)

    raw_data.to_excel(writer, sheet_name=str(team), index=False)

    data_dict[team].append(average_auto)
    data_dict[team].append(average_tele)
    data_dict[team].append(average_climb)
    data_dict[team].append(average_total_points)


def write_qualitative_information(team, data):
    """
    Writes the qualitative information from the DataFrame (written information / who scouted it)

    Args:
        team (int): team to write the data for
        data (pd.DataFrame): DataFrame with data for the team
    """
    raw_data = data[['name', 'written_information']]

    raw_data.columns = ['Name', 'Written Information']

    raw_data.to_excel(writer, sheet_name=str(
        team), index=False, startrow=0, startcol=7)


def write_statistics(team, data):
    """
    Writes the statistics (defense percentage, an LSRL slope, and a p-value from a t-test

    Args:
        team (int): team to write the data for
        data (pd.DataFrame): DataFrame with data for the team
    """
    columns = ['Defense Percentage', 'LSRL Slope',
               'T-test']
    # calculates percent of time doing defense to 2 decimal places
    defense_percentage = round(len(
        data['total_points'][data['defense'] == 'yes']) * 100 / len(data['defense']), 2)

    # LSRL slope using scipy
    slope, _, _, _, _ = stats.linregress(
        range(0, len(data['total_points'])), data['total_points'])
    slope = round(slope, 5)

    # p-value from independent t-test
    p_value = np.NaN
    if len(pd.unique(data['time'])) != 1:
        p_value = round(stats.ttest_ind(data['total_points'][data['time'] == 1],
                                        data['total_points'][data['time'] == 2]).pvalue, 7)

    df = pd.DataFrame([[defense_percentage, slope, p_value]], columns=columns)

    # writes data
    df.to_excel(writer, sheet_name=str(team), index=False,
                startrow=len(data) + 4, startcol=1)

    data_dict[team].append(defense_percentage)
    data_dict[team].append(slope)
    data_dict[team].append(p_value)


def write_graphs(team, data):
    """
    Writes the statistics (defense percentage, an LSRL slope, and a p-value from a t-test)

    Args:
        team (int): team to write the data for
        data (pd.DataFrame): DataFrame with data for the team
    """

    # i have no idea how this code works, but if you remove some of it, it stops working so don't change it
    workbook1 = writer.book
    worksheet1 = writer.sheets[str(team)]

    (max_row, _) = data.shape

    categories = ['total_auto_points', 'total_teleop_points',
                  'climb', 'total_points', 'day1vsday2']
    y_axes = ['Total auto points', 'Total teleop points',
              'Climb points', 'Total points', 'Total points']
    colors = ['red', 'blue', '', 'green', '']
    titles = ['Total Auto Points', 'Total Teleop Points', 'Climb Distribution',
              'Total Points Scored', 'Day 1 vs. Day 2 (Total Points)']
    positions = [(max_row + 7, 0), (max_row + 7, 5), (max_row +
                                                      7 + 16, 0), (max_row + 7 + 16, 5), (max_row + 7 + 16 + 16, 2)]

    # xlsxwriter is annoying, you can't pass in values, so you're forced to create new entries off-screen
    worksheet1.write(0, 24, 'No hang (0)')
    worksheet1.write(1, 24, 'Low bar (4)')
    worksheet1.write(2, 24, 'Middle bar (6)')
    worksheet1.write(3, 24, 'High bar (10)')
    worksheet1.write(4, 24, 'Traversal bar (15)')

    worksheet1.write(0, 25, len(data[data['climb'] == 0]))
    worksheet1.write(1, 25, len(data[data['climb'] == 4]))
    worksheet1.write(2, 25, len(data[data['climb'] == 6]))
    worksheet1.write(3, 25, len(data[data['climb'] == 10]))
    worksheet1.write(4, 25, len(data[data['climb'] == 15]))

    worksheet1.write(5, 24, 'Day 1')
    worksheet1.write(6, 24, 'Day 2')
    worksheet1.write(5, 25, data[data['time'] == 1]
                     ['total_points'].mean(axis=0))
    average_day2 = 0
    if (len(data[data['time'] == 2]) != 0):
        average_day2 = data[data['time'] == 2]['total_points'].mean(axis=0)
    worksheet1.write(6, 25, average_day2)

    worksheet1.write(7, 24, 'Points')

    for i in range(len(categories)):
        if i == 2:
            # pie chart
            chart = workbook1.add_chart({'type': 'pie'})

            chart.add_series({
                'categories': [str(team), 0, 24, 4, 24],
                'values': [str(team), 0, 25, 4, 25]
            })

            chart.set_title({'name': titles[i]})

            # Insert the chart into the worksheet.
            worksheet1.insert_chart(positions[i][0], positions[i][1], chart)
        elif i == 4:
            # bar graph
            chart = workbook1.add_chart({'type': 'column'})

            chart.add_series({
                'categories': [str(team), 5, 24, 6, 24],
                'values': [str(team), 5, 25, 6, 25],
                'name': [str(team), 7, 24]
            })

            chart.set_title({'name': titles[i]})

            # Insert the chart into the worksheet.
            worksheet1.insert_chart(positions[i][0], positions[i][1], chart)
        else:
            # line graph
            chart = workbook1.add_chart({'type': 'line', 'subtype': 'stacked'})
            col = i + 2

            chart.add_series({
                'name': [str(team), 7, 24],
                'values': [str(team), 1, col, max_row, col],
                'line': {'color': colors[i]}
            })

            chart.set_x_axis({'name': 'Match'})
            chart.set_y_axis({'name': y_axes[i]})

            chart.set_title({'name': titles[i]})

            # Insert the chart into the worksheet.
            worksheet1.insert_chart(positions[i][0], positions[i][1], chart)


def main():
    '''
    runs the program
    '''

    # adds flags
    parser = argparse.ArgumentParser(description='Scouting Program for 1787')
    parser.add_argument('--min_points', type=int,
                        help='only considers teams with total points higher than min_points (inclusive)', default=0)
    parser.add_argument(
        '--path', type=str, help='path to csv (probably somewhere in ~/Downloads). Defaults to using Sheets API.', default='')
    args = parser.parse_args()

    spreadsheet_id = '1wyS8yFLIZZdr23nP2SdYWx4bDEFCmUC611Rfd9_OUvM'
    df = get_dataframe(spreadsheet_id, args.path)

    team_list = get_teams(df, args.min_points)

    colors = list(Color('orange').range_to(Color('grey'), len(team_list)))

    rankings_worksheet = workbook.add_worksheet('rankings')

    # writes data for each team
    for i, team in enumerate(team_list):
        print(f'processing team {team}')

        data_dict[team] = []

        # data = create_dict_dataframe(df, team, args.min_points)
        data = create_dict_dataframe(df, team)

        worksheet = workbook.add_worksheet(str(team))
        write_data(team, data)
        write_qualitative_information(team, data)
        write_statistics(team, data)

        writer.sheets[str(team)].set_column(0, 0, 10)
        writer.sheets[str(team)].set_column(1, 1, 19)
        writer.sheets[str(team)].set_column(2, 2, 13)
        writer.sheets[str(team)].set_column(3, 3, 13)
        writer.sheets[str(team)].set_column(4, 4, 13)
        writer.sheets[str(team)].set_column(5, 5, 13)
        writer.sheets[str(team)].set_column(6, 6, 15)
        writer.sheets[str(team)].set_column(7, 7, 18)
        writer.sheets[str(team)].set_column(8, 8, 150)

        writer.sheets[str(team)].set_tab_color(colors[i].hex)
        write_graphs(team, data)

    # very convoluted way to do it, but performance is fast enough so it's fine
    columns = ['Average Auto', 'Average Teleop', 'Average Climb',
               'Average Total Points', 'Defense Percentage', 'LSRL Slope', 'P-value']
    ranking_data = pd.DataFrame.from_dict(
        data_dict, columns=columns, orient='index')

    rankings = pd.DataFrame()
    rankings['#'] = range(1, len(team_list) + 1)
    for i, column in enumerate(columns):  # df -> df subset -> df????
        temp_df = pd.DataFrame()
        temp_df[f'Team{i}'] = team_list
        temp_df[column] = ranking_data[column].values
        temp_df[column] = pd.to_numeric(temp_df[column])
        temp_df = temp_df.sort_values(by=[column], ascending=(
            column == 'P-value'), ignore_index=True)
        rankings = pd.concat([rankings, temp_df], axis=1, sort=False)

    rankings.to_excel(writer, sheet_name='rankings',
                      index=False, startrow=0, startcol=0)
    writer.sheets['rankings'].set_column(0, 0, 3)
    workbook1 = writer.book
    cell_format = workbook1.add_format(
        {'bg_color': '#FFD580', 'border': 1, 'valign': 'center'})
    for i in range(2, 16, 2):
        writer.sheets['rankings'].set_column(
            i, i, cell_format=cell_format, width=20)

    writer.save()


if __name__ == '__main__':
    main()
