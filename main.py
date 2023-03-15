import argparse
from scipy import stats
import pandas as pd
import xlsxwriter
from colour import Color
import numpy as np

"""
this is probably the worst code i've ever written in my life but if it works it works :)
to anyone trying to read this code in future seasons, i am very sorry, honestly just make it from scratch instead, this thing is an absolute rushed mess 
i'm not commenting this either because i'm lazy and there's no point in commenting 700 lines of stupidity
"""


def get_total_points(df):
    # oops this is very bad code
    aggregate_columns = [
        "total_points",
        "tele_points",
        "auto_points",
        "num_cycles",
        "charge_station_points",
        "high_points",
        "mid_points",
        "low_points",
        "high_cycles",
        "mid_cycles",
        "low_cycles",
        "cone_points",
        "cube_points",
    ]
    ret_df = pd.DataFrame(
        np.zeros((len(df), len(aggregate_columns))), columns=aggregate_columns
    )

    for name in df.columns:
        if "cone" not in name and "cube" not in name:
            continue

        column = df[name]
        score = 0
        if "auto" in name:
            score += 1

        if "high" in name:
            score += 5
            ret_df["high_points"] += score * column
            if "tele" in name:
                ret_df["high_cycles"] += column
            if "auto" in name:
                ret_df["auto_points"] += score * column
        if "mid" in name:
            score += 3
            ret_df["mid_points"] += score * column
            if "tele" in name:
                ret_df["mid_cycles"] += column
            if "auto" in name:
                ret_df["auto_points"] += score * column
        if "low" in name:
            score += 2
            ret_df["low_points"] += score * column
            if "tele" in name:
                ret_df["low_cycles"] += column
            if "auto" in name:
                ret_df["auto_points"] += score * column

        if "cone" in name:
            ret_df["cone_points"] += score * column

        if "cube" in name:
            ret_df["cube_points"] += score * column

        ret_df["total_points"] += score * column
        if "tele" in name:
            ret_df["num_cycles"] += column

    df["leave_community"] = df["leave_community"].replace({"Yes": 3, "No": 0})
    ret_df["total_points"] += (
        df["leave_community"] + df["auto_balance"] + df["tele_balance"]
    )
    ret_df["auto_points"] += df["leave_community"] + df["auto_balance"]
    ret_df["tele_points"] = (
        ret_df["high_cycles"] * 5 + ret_df["mid_cycles"] * 3 + ret_df["low_cycles"] * 2
    )
    ret_df["charge_station_points"] += df["tele_balance"]

    return ret_df


def create_categories(df):
    # we should also have top points, mid points, low points, cube points, cone points,
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


def get_team_dfs(field_path, min_points):
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

    df = pd.read_csv(field_path)
    df.columns = columns

    df = create_categories(df)
    teams = df["team_number"].unique()

    teams.sort()
    ret = []

    for team in teams:
        if df.loc[df["team_number"] == team]["total_points"].mean() >= min_points:
            ret.append(team)

    return ret, df


def get_rankings(df, teams):
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
    stats_df = pd.DataFrame(columns=stats_columns)

    for team in teams:
        cur_df = pd.DataFrame(columns=stats_columns)

        cur_df["team_number"] = [team]
        cur_df[
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

        slope, _, _, _, _ = stats.linregress(
            range(0, len(df.loc[df["team_number"] == team]["total_points"])),
            df.loc[df["team_number"] == team]["total_points"],
        )
        slope = round(slope, 4)

        p_value = np.NaN
        if len(pd.unique(df["timestamp"])) != 1:
            p_value = round(
                stats.ttest_ind(
                    df.loc[df["team_number"] == team]["total_points"][
                        df["timestamp"] == 1
                    ],
                    df.loc[df["team_number"] == team]["total_points"][
                        df["timestamp"] == 2
                    ],
                ).pvalue,
                7,
            )

        defense_percentage = round(
            len(df.loc[(df["team_number"] == team) & (df["defense"] == "Yes")])
            * 100
            / len(df.loc[df["team_number"] == team]["defense"]),
            2,
        )

        cur_df["lsrl_slope"] = [slope]
        cur_df["p_value"] = [p_value]
        cur_df["defense_percentage"] = [defense_percentage]

        stats_df = pd.concat([stats_df, cur_df])

    formatted_columns = [
        "Total Points",
        "Auto Points",
        "# of Cycles",
        "Endgame Balance",
        "LSRL Slope",
        "Defense %",
        "P-value",
    ]

    rankings = pd.DataFrame()
    rankings["#"] = range(1, len(teams) + 1)
    for i, column in enumerate(stats_columns):
        if i == 0:
            continue
        temp_df = pd.DataFrame()
        temp_df[f"Team{i}"] = teams
        temp_df[formatted_columns[i - 1]] = stats_df[column].values
        temp_df = temp_df.sort_values(
            by=[formatted_columns[i - 1]],
            ascending=(column == "p_value"),
            ignore_index=True,
        )
        rankings = pd.concat([rankings, temp_df], axis=1, sort=False)

    return rankings, stats_df


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
        "--field_path",
        type=str,
        help="path to field scouting csv (probably somewhere in ~/Downloads).",
        default="",
    )
    parser.add_argument(
        "--pit_path",
        type=str,
        help="path to pit scouting csv (probably somewhere in ~/Downloads).",
        default="",
    )

    args = parser.parse_args()

    return args


def create_spreadsheet(teams, field_df, stats_df, rankings, pit_df):
    colors = list(Color("orange").range_to(Color("grey"), len(teams)))
    workbook = xlsxwriter.Workbook("output.xlsx")
    writer = pd.ExcelWriter("output.xlsx", engine="xlsxwriter")
    stats_worksheet = workbook.add_worksheet("Rankings")

    rankings.to_excel(
        writer, sheet_name="rankings", index=False, startrow=0, startcol=0
    )

    cell_format = writer.book.add_format(
        {"bg_color": "white", "border": 1, "valign": "center"}
    )

    format_1787 = writer.book.add_format({"bg_color": "#FFD580", "border": 1})

    data_format = writer.book.add_format({"valign": "center"})

    writer.sheets["rankings"].conditional_format(
        "A1:O100",
        {
            "type": "cell",
            "criteria": "==",
            "value": 1787,
            "format": format_1787,
        },
    )

    for i in range(2, 16, 2):
        writer.sheets["rankings"].conditional_format(
            1,
            i,
            len(teams),
            i,
            {
                "type": "cell",
                "criteria": ">",
                "value": -99999999999,
                "format": cell_format,
            },
        )
        writer.sheets["rankings"].set_column(i, i, 15, data_format)

    data_columns = [
        "match_number",
        "total_points",
        "tele_points",
        "auto_points",
        "num_cycles",
        "charge_station_points",
        "high_points",
        "mid_points",
        "low_points",
        "cone_points",
        "cube_points",
        "num_links",
    ]

    formatted_data_columns = [
        "Match #",
        "Total Points",
        "Teleop Points",
        "Auto Points",
        "# of Cycles",
        "Endgame Balance",
        "High Points",
        "Mid Points",
        "Low Points",
        "Cone Points",
        "Cube Points",
        "# of Links",
    ]

    stats_columns = ["lsrl_slope", "defense_percentage", "p_value"]

    formatted_stats_columns = ["LSRL Slope", "Defense %", "P-value"]

    written_columns = ["name", "comments"]

    formatted_written_columns = ["Name", "Comments"]

    color_idx = 0

    for team in teams:
        print(f"Processing team {team}...")
        # data side of stuff
        averages = (
            field_df.loc[field_df["team_number"] == team][data_columns]
            .mean(axis=0)
            .round(2)
        )
        averages = pd.DataFrame(averages).transpose()
        averages["match_number"] = "N/A"

        left_hand_column = [""] * (
            len(field_df.loc[field_df["team_number"] == team]) + 1
        )
        left_hand_column[-1] = "Averages:"

        team_data_df = pd.concat(
            [field_df.loc[field_df["team_number"] == team][data_columns], averages],
            axis=0,
        )
        team_data_df.columns = formatted_data_columns
        team_data_df.insert(0, "", left_hand_column, True)

        worksheet = workbook.add_worksheet(str(team))

        team_data_df.to_excel(
            writer, sheet_name=str(team), index=False, startrow=0, startcol=0
        )

        for i in range(0, len(data_columns) + 1):
            writer.sheets[str(team)].set_column(i, i, width=12)

        # qualitative info stuff
        team_written_df = field_df.loc[field_df["team_number"] == team][written_columns]
        team_written_df.columns = formatted_written_columns
        team_written_df.to_excel(
            writer,
            sheet_name=str(team),
            index=False,
            startrow=0,
            startcol=len(data_columns) + 2,
        )
        writer.sheets[str(team)].set_column(
            len(data_columns) + 3, len(data_columns) + 3, width=150
        )

        # stats stuff
        team_stats_df = stats_df.loc[stats_df["team_number"] == team][stats_columns]
        team_stats_df.columns = formatted_stats_columns
        team_stats_df.to_excel(
            writer,
            sheet_name=str(team),
            index=False,
            startrow=len(team_data_df) + 3 + 7,
            startcol=0,
        )

        workbook1 = writer.book
        worksheet1 = writer.sheets[str(team)]

        worksheet1.write(7, 49, "Points")

        num_data_points = len(field_df.loc[field_df["team_number"] == team])
        cur_team = field_df.loc[field_df["team_number"] == team]

        # rankings stuff
        ranking_columns = [
            "Total Points",
            "Auto Points",
            "# of Cycles",
            "Endgame Balance",
        ]

        cell_format = writer.book.add_format(
            {"border": 1, "bold": True, "bg_color": "#FFD580", "valign": "center"}
        )

        worksheet1.write(len(team_data_df) + 3, 0, "Category", cell_format)
        worksheet1.write(len(team_data_df) + 3, 1, "Ranking", cell_format)
        for i in range(1, 5):
            cur_column = "Team" + str(i)
            ranking = rankings.loc[rankings[cur_column] == team].index.tolist()[0] + 1
            worksheet1.write(len(team_data_df) + 3 + i, 0, rankings.columns[i * 2])
            worksheet1.write(len(team_data_df) + 3 + i, 1, ranking)

        # chart 1: line graph of the total points
        for i, points in enumerate(
            field_df.loc[field_df["team_number"] == team]["total_points"]
        ):
            worksheet1.write(i, 50, points)

        chart = workbook1.add_chart({"type": "line", "subtype": "stacked"})
        chart.add_series(
            {
                "name": [str(team), 7, 49],
                "values": [str(team), 0, 50, num_data_points - 1, 50],
                "line": {"color": "blue"},
            }
        )

        chart.set_x_axis({"name": "Match #"})
        chart.set_y_axis({"name": "Total Points"})

        chart.set_title({"name": "Total Points"})

        worksheet1.insert_chart(len(team_data_df) + 3, 5, chart)

        # chart 2: pie graph with low, mid, high
        worksheet1.write(0, 51, "High")
        worksheet1.write(1, 51, "Mid")
        worksheet1.write(2, 51, "Low")
        worksheet1.write(0, 52, cur_team["high_cycles"].sum())
        worksheet1.write(1, 52, cur_team["mid_cycles"].sum())
        worksheet1.write(2, 52, cur_team["low_cycles"].sum())

        chart = workbook1.add_chart({"type": "pie"})
        chart.add_series(
            {
                "categories": [str(team), 0, 51, 2, 51],
                "values": [str(team), 0, 52, 2, 52],
            }
        )

        chart.set_title({"name": "Placement of Game Pieces"})

        worksheet1.insert_chart(len(team_data_df) + 3, 11, chart)

        # chart 3: pie chart of auto balancing distribution
        worksheet1.write(0, 53, "Docked (Engaged)")
        worksheet1.write(1, 53, "Docked (Not Engaged)")
        worksheet1.write(2, 53, "None")
        worksheet1.write(0, 54, len(cur_team.loc[cur_team["auto_balance"] == 12]))
        worksheet1.write(1, 54, len(cur_team.loc[cur_team["auto_balance"] == 8]))
        worksheet1.write(2, 54, len(cur_team.loc[cur_team["auto_balance"] == 0]))

        chart = workbook1.add_chart({"type": "pie"})
        chart.add_series(
            {
                "categories": [str(team), 0, 53, 2, 53],
                "values": [str(team), 0, 54, 2, 54],
            }
        )

        chart.set_title({"name": "Autonomous Balancing Distribution"})

        worksheet1.insert_chart(len(team_data_df) + 3 + 16, 5, chart)

        # chart 4: pie chart of tele balancing distribution
        worksheet1.write(0, 55, "Docked (Engaged)")
        worksheet1.write(1, 55, "Docked (Not Engaged)")
        worksheet1.write(2, 55, "None")
        worksheet1.write(0, 56, len(cur_team.loc[cur_team["tele_balance"] == 10]))
        worksheet1.write(1, 56, len(cur_team.loc[cur_team["tele_balance"] == 6]))
        worksheet1.write(2, 56, len(cur_team.loc[cur_team["tele_balance"] == 0]))

        chart = workbook1.add_chart({"type": "pie"})
        chart.add_series(
            {
                "categories": [str(team), 0, 55, 2, 55],
                "values": [str(team), 0, 56, 2, 56],
            }
        )

        chart.set_title({"name": "Teleoperated Balancing Distribution"})

        worksheet1.insert_chart(len(team_data_df) + 3 + 16, 11, chart)

        # chart 5: pie chart for defense
        worksheet1.write(0, 57, "Offense")
        worksheet1.write(1, 57, "Not Sure")
        worksheet1.write(2, 57, "Defense")
        worksheet1.write(0, 58, len(cur_team.loc[cur_team["defense"] == "Yes"]))
        worksheet1.write(1, 58, len(cur_team.loc[cur_team["defense"] == "No"]))
        worksheet1.write(2, 58, len(cur_team.loc[cur_team["defense"] == "Not sure"]))

        chart = workbook1.add_chart({"type": "pie"})
        chart.add_series(
            {
                "categories": [str(team), 0, 57, 2, 57],
                "values": [str(team), 0, 58, 2, 58],
            }
        )

        chart.set_title({"name": "Defense Distribution"})

        worksheet1.insert_chart(len(team_data_df) + 3 + 16 + 16, 5, chart)

        # chart 6: day 1 vs. day 2
        worksheet1.write(0, 59, "Day 1")
        worksheet1.write(1, 59, "Day 2")
        worksheet1.write(
            0,
            60,
            field_df.loc[
                (field_df["timestamp"] == 1) & (field_df["team_number"] == team)
            ]["total_points"].mean(),
        )
        average_day2 = 0
        if (
            len(
                field_df.loc[
                    (field_df["timestamp"] == 2) & (field_df["team_number"] == team)
                ]
            )
            != 0
        ):
            average_day2 = field_df.loc[
                (field_df["timestamp"] == 2) & (field_df["team_number"] == team)
            ]["total_points"].mean()
        worksheet1.write(1, 60, average_day2)

        chart = workbook1.add_chart({"type": "column"})

        chart.add_series(
            {
                "categories": [str(team), 0, 59, 1, 59],
                "values": [str(team), 0, 60, 1, 60],
                "name": [str(team), 7, 49],
            }
        )

        chart.set_title({"name": "Day 1 vs. Day 2"})
        worksheet1.insert_chart(len(team_data_df) + 3 + 16 + 16, 5 + 6, chart)

        # pit scouting information
        if isinstance(pit_df, pd.DataFrame):
            cell_format = writer.book.add_format(
                {"border": 1, "bold": True, "bg_color": "#FFD580", "valign": "center"}
            )

            writer.sheets[str(team)].merge_range(
                len(team_data_df) + 9 + 5,
                0,
                len(team_data_df) + 9 + 5,
                2,
                "Pit Scouting Info",
                cell_format,
            )

            cell_format = writer.book.add_format({"border": 1, "bold": True})

            pit_team_df = pit_df.loc[pit_df["Team Number"] == team]
            row = len(team_data_df) + 9 + 6
            for column in pit_team_df.columns:
                if "useless" in column:
                    continue

                worksheet1.write(row, 0, column, cell_format)
                worksheet1.write(row, 1, pit_team_df[column].values[0])

                row += 1

            writer.sheets[str(team)].set_column(0, 0, width=17)

        # colors!
        writer.sheets[str(team)].set_tab_color(colors[color_idx].hex)
        color_idx += 1

        cell_format = writer.book.add_format(
            {"border": 1, "bold": True, "bg_color": "#FFD580", "valign": "center"}
        )

        for i in range(0, len(formatted_data_columns)):
            worksheet1.write(0, i + 1, formatted_data_columns[i], cell_format)

        worksheet1.write(0, 0, "Matches:", cell_format)
        worksheet1.write(0, len(formatted_data_columns) + 1, "", cell_format)
        worksheet1.write(0, len(formatted_data_columns) + 2, "Name", cell_format)
        worksheet1.write(0, len(formatted_data_columns) + 3, "Comments", cell_format)

        worksheet1.write(len(team_data_df) + 3 + 7, 0, "LSRL Slope", cell_format)
        worksheet1.write(len(team_data_df) + 3 + 7, 1, "Defense %", cell_format)
        worksheet1.write(len(team_data_df) + 3 + 7, 2, "P-value", cell_format)

    writer.save()


def get_pit_info(pit_csv, teams):
    columns = [
        "useless_timestamp",
        "Name",
        "Team Number",
        "Weight",
        "Speed",
        "Drivetrain",
        "Scoring Capabilities",
        "Leave Community?",
        "useless1",
        "useless2",
        "useless3",
        "useless4",
        "useless5",
        "useless6",
        "useless7",
        "Starting Position",
        "useless8",
        "Scoring Method",
        "Defense?",
        "Other Information",
    ]
    df = pd.read_csv(pit_csv)
    df.columns = columns
    return df


def main():
    # adds flags
    args = process_args()

    teams, df = get_team_dfs(args.field_path, args.min_points)
    teams.sort()
    rankings_df, stats_df = get_rankings(df, teams)
    if args.pit_path != "":
        pit_scouting_df = get_pit_info(args.pit_path, teams)
        create_spreadsheet(teams, df, stats_df, rankings_df, pit_scouting_df)
    else:
        create_spreadsheet(teams, df, stats_df, rankings_df, None)


if __name__ == "__main__":
    main()
