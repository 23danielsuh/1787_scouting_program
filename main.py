import argparse
from scipy import stats
import pandas as pd
import xlsxwriter
from colour import Color
import numpy as np

def get_total_points(grid_info):
    ret_df = pd.Series(np.zeros((len(grid_info))))

    for name in grid_info.columns:
        column = grid_info[name]
        score = 0

        if 'high' in name:
            score = 5
        if 'mid' in name:
            score = 3
        if 'low' in name:
            score = 2
        if 'auto' in name:
            score += 1

        ret_df += score * column

    return ret_df



def create_categories(df):
    df["timestamp"] = df["timestamp"].apply(lambda x: x.split(" ")[0])

    # very, very inefficient code...
    dates = df["timestamp"]
    dates = dates.sort_values()
    if dates.iloc[0] != dates.iloc[-1]:
        dates = dates.replace(dates.iloc[0], 1)
        dates = dates.replace(dates.iloc[-1], 2)
    else:
        dates = dates.replace(dates.iloc[0], 1)

    df["timestamp"] = dates

    df[['team_number', 'match_number']] = df[['team_number', 'match_number']].astype(int)

    grid_columns = [
        "auto_cone_high",
        "auto_cone_mid",
        "auto_cone_low",
        "auto_cube_high",
        "auto_cube_mid",
        "auto_cube_low",
        "tele_cone_high",
        "tele_cone_mid",
        "tele_cone_low",
        "tele_cube_high",
        "tele_cube_mid",
        "tele_cube_low",
    ]

    df[grid_columns] = df[grid_columns].astype(str)
    df[grid_columns] = df[grid_columns].applymap(
        lambda x: max(map(int, x.split(", ")))
    )
    df[grid_columns] = df[grid_columns].astype(int)

    balancing_columns = [
        'auto_balance',
        'tele_balance',
    ]
    df[balancing_columns] = df[balancing_columns].replace({'Yes, balanced': 'balanced', 'Yes, unbalanced': 'unbalanced', 'No': 'none'})

    df['total_points'] = get_total_points(df[grid_columns])
    print(df['total_points'])
    df['num_cycles'] = df[grid_columns].sum()

    return df


def get_dataframe(path, min_points):
    columns = [
        "timestamp",
        "name",
        "team_number",
        "match_number",
        "leave_community",
        "auto_cone_high",
        "auto_cone_mid",
        "auto_cone_low",
        "auto_cube_high",
        "auto_cube_mid",
        "auto_cube_low",
        "auto_balance",
        "tele_cone_high",
        "tele_cone_mid",
        "tele_cone_low",
        "tele_cube_high",
        "tele_cube_mid",
        "tele_cube_low",
        "tele_balance",
        "defense",
        "num_links",
        "comments",
    ]

    df = pd.read_csv(path)
    df.columns = columns

    df = create_categories(df)
    # df = filter_dataframe(df, min_points)

    return df

def process_args():
    parser = argparse.ArgumentParser(
        description="Scouting Program for 1787 (2023 version)"
    )

    parser.add_argument(
        "--min_points",
        type=int,
        help="only considers teams with total points higher than min_points (inclusive)",
        default=0,
    )
    parser.add_argument(
        "--path",
        type=str,
        help="path to csv (probably somewhere in ~/Downloads).",
        default="",
    )

    args = parser.parse_args()

    return args
    

def main():
    # adds flags
    args = process_args()

    df = get_dataframe(args.path, args.min_points)
    df.to_csv('wtf.csv')

    colors = list(Color("orange").range_to(Color("grey"), len(df)))


if __name__ == "__main__":
    main()
