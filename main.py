import argparse
from scipy import stats
import pandas as pd
import xlsxwriter
from colour import Color
import numpy as np


def get_total_points(df):
    aggregate_columns = [
        "auto_points",
        "total_points",
        "num_cycles",
        "charge_station_points",
    ]
    ret_df = pd.DataFrame(
        np.zeros((len(df), len(aggregate_columns))), columns=aggregate_columns
    )

    for name in df.columns:
        if "cone" not in name and "cube" not in name:
            continue

        column = df[name]
        score = 0

        if "high" in name:
            score = 5
        if "mid" in name:
            score = 3
        if "low" in name:
            score = 2

        if "auto" in name:
            score += 1
            ret_df["auto_points"] += score * column
        else:
            ret_df["num_cycles"] += 1 * column

        ret_df["total_points"] += score * column

    ret_df["total_points"] += df["auto_balance"] + df["tele_balance"]
    ret_df["auto_points"] += df["auto_balance"]
    ret_df["charge_station_points"] += df["auto_balance"] + df["tele_balance"]

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

    df[["team_number", "match_number"]] = df[["team_number", "match_number"]].astype(
        int
    )

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
    df[grid_columns] = df[grid_columns].applymap(lambda x: max(map(int, x.split(", "))))
    df[grid_columns] = df[grid_columns].astype(int)

    df["auto_balance"] = df["auto_balance"].replace(
        {"Yes, balanced": 12, "Yes, unbalanced": 8, "No": 0}
    )
    df["tele_balance"] = df["tele_balance"].replace(
        {"Yes, balanced": 10, "Yes, unbalanced": 6, "No": 0}
    )

    df = df.join(get_total_points(df))

    return df


def get_team_dfs(path, min_points):
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
    teams = df["team_number"].unique()

    teams.sort()
    ret = []

    for team in teams:
        if df.loc[df["team_number"] == team]["total_points"].mean() >= min_points:
            ret.append(team)

    return ret, df


def get_statistics(df, teams):
    stats_columns = [
        "team_number",
        "average_total_points",
        "average_auto_points",
        "average_num_cycles",
        "average_charge_station_points",
        "lsrl_slope",
        "defense_percentage",
        "p_value",
    ]
    stats_df = pd.DataFrame(
        np.zeros((len(teams), len(stats_columns))), columns=stats_columns
    )

    for team in teams:
        stats_df["team_number"] = team
        stats_df[
            [
                "average_total_points",
                "average_auto_points",
                "average_num_cycles",
                "average_charge_station_points",
            ]
        ] = (
            df.loc[df["team_number"] == team][
                ["total_points", "auto_points", "num_cycles", "charge_station_points"]
            ]
            .mean(axis=0)
            .round(2)
        )

    return stats_df


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

    teams, df = get_team_dfs(args.path, args.min_points)
    df.to_csv("info.csv")
    stats_df = get_statistics(df, teams)
    stats_df.to_csv("stats.csv")

    colors = list(Color("orange").range_to(Color("grey"), len(df)))


if __name__ == "__main__":
    main()
