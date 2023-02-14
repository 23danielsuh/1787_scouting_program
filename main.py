import numpy as np
from collections import defaultdict
import argparse
from scipy import stats
import pandas as pd
import xlsxwriter
from colour import Color


def get_dataframe(path):
    columns = ['timestamp', 'name', 'team_number', 'match_number', 'leave_community', 'auto_cone_high', 'auto_cone_mid', 'auto_cone_low', 'auto_cube_high',
               'auto_cube_mid', 'auto_cube_low', 'auto_balance', 'tele_cone_high', 'tele_cone_mid', 'tele_cone_low', 'tele_balance', 'defense', 'num_links', 'comments']

    df = pd.read_csv(path, columns=columns)
    print(df.head())
    return df


def get_teams(df, min_points):
    return []


def main():
    # adds flags
    parser = argparse.ArgumentParser(
        description='Scouting Program for 1787 (2023 version)')
    parser.add_argument('--min_points', type=int,
                        help='only considers teams with total points higher than min_points (inclusive)', default=0)
    parser.add_argument(
        '--path', type=str, help='path to csv (probably somewhere in ~/Downloads).', default='')
    args = parser.parse_args()

    df = get_dataframe(args.path)

    team_list = get_teams(df, args.min_points)

    colors = list(Color('orange').range_to(Color('grey'), len(team_list)))

    rankings_worksheet = workbook.add_worksheet('rankings')


if __name__ == '__main__':
    main()
