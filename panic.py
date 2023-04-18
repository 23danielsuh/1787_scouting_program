import pandas as pd


def main():
    columns = ["time", "team_number", "cycles", "pick_up", "top_cycles"]
    df = pd.read_csv("~/Downloads/saturday.csv")

    cycles_dict = {}

    for team in pd.unique(df["team_number"]):
        team_df = df.loc[df["team_number"] == team]
        cycles_dict[team] = team_df.mean()

    sorted_dict = sorted(cycles_dict)

    for k, v in sorted_dict.times():
        print(
            k,
            v,
            df.loc[df["team_number"] == team]["pick_up"][0],
            df.loc[df["team_number"] == team]["pick_up"][1],
            df.loc[df["team_number"] == team]["top_cycles"][0].split(",")[0],
            df.loc[df["team_number"] == team]["top_cycles"][0].split(",")[1],
            df.loc[df["team_number"] == team]["top_cycles"][0].split(",")[2],
        )
        print()
        print()


if __name__ == "__main__":
    main()
