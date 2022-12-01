from __future__ import print_function
import collections
import numpy as np
import pandas as pd
from auth import spreadsheet_service


def create_dict_dataframe(df, team_number):
    """
    Takes a team number and generates a DataFrame of the scouting data from that team number
    :param df: The DataFrame with all the data
    :param team_number: The team number to get data for
    :return: A pd.DataFrame of the data
    """
    return df[df['team_number'] == team_number]


def string_to_max(s):
    """
    Takes in a string of a list and returns the maximum of the list
    :param s: string of a list
    :return: maximum of the list
    """
    lst = s.split(', ')
    new_lst = []
    # TODO: don't make this bad code (maybe use numpy to optimize?)
    for num in lst:
        new_lst.append(int(num))

    return max(new_lst)


def assign_climb_points(x):
    """
    Assigns climb points for the spreadsheet text
    :param x: text
    :return: points
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
    :param lower_hub: df.Column
    :param upper_hub: df.Column
    :param in_auto: bool
    :return: int
    """
    multiplier = (1, 2)
    if in_auto:
        multiplier = (2, 4)

    return lower_hub * multiplier[0] + upper_hub * multiplier[1]


def process_dataframe(init_df):
    """
    Processes the DataFrame to be in a better format for use
    :param init_df: DataFrame to format
    :return: Formatted DataFrame
    """
    df = init_df.drop(['email', 'time'], axis=1)
    df['name'] = df['name'].apply(lambda x: x.strip())
    df['team_number'] = pd.to_numeric(df['team_number'])
    df['qual_number'] = pd.to_numeric(df['qual_number'])

    df['taxi'] = df['taxi'].replace('Yes', 2)
    df['taxi'] = df['taxi'].replace('No', 0)

    # lots of boilerplate :)
    df['auto_upper_hub'] = df['auto_upper_hub'].apply(lambda x: max(map(int, x.split(', '))))
    df['auto_lower_hub'] = df['auto_lower_hub'].apply(lambda x: max(map(int, x.split(', '))))

    df['total_auto_points'] = get_shooter_points(df['auto_lower_hub'], df['auto_upper_hub'], True)

    df['teleop_upper_hub'] = df['teleop_upper_hub'].apply(lambda x: max(map(int, x.split(', '))))
    df['teleop_lower_hub'] = df['teleop_lower_hub'].apply(lambda x: max(map(int, x.split(', '))))

    df['total_teleop_points'] = get_shooter_points(df['auto_lower_hub'], df['auto_upper_hub'], False)

    df['climb'] = df['climb'].apply(lambda x: assign_climb_points(x))
    df['defense'] = df['defense'].apply(lambda x: x.lower())

    df['total_points'] = df['total_auto_points'] + df['total_teleop_points'] + df['climb']

    return df


def get_dataframe(spreadsheet_id):
    """
    Gets the spreadsheet from the API, and returns the spreadsheet converted to a pd.DataFrame
    :param spreadsheet_id: the id of the spreadsheet
    :return: a pd.DataFrame of the data
    """
    data = spreadsheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='Sheet1').execute().get(
        'values')
    columns = ['time', 'email', 'name', 'team_number', 'qual_number', 'taxi', 'auto_upper_hub', 'auto_lower_hub',
               'teleop_upper_hub', 'teleop_lower_hub', 'climb', 'defense', 'written_information']
    df = pd.DataFrame(data[1:], columns=columns)
    df = process_dataframe(df)
    return df


def get_teams(df):
    """
    Gets all the unique teams in the dataframe
    :param df: DataFrame to get the teams from
    :return: list of the teams in sorted order
    """
    l = list(pd.unique(df['team_number']))
    l.sort()
    return l


def main():
    '''
    runs the program
    :return: nothing
    '''
    df = get_dataframe('1mMOpwAWR2woBgi6s2YJKUehTTJBsD58680Mq_ZsXfec')
    print(get_teams(df))


if __name__ == '__main__':
    main()
