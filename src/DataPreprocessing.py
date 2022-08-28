from pathlib import Path

import hydra
import pandas as pd
from hydra.utils import to_absolute_path as abspath
from omegaconf import DictConfig

from scraper import ScraperResults, ScraperRosters


class DataPreprocessing:
    def __init__(self, output_path, input_dir, update=False):
        self.ScraperResults = ScraperResults()
        self.ScraperRoster = ScraperRosters()
        self.output_path = output_path
        self.input_dir = input_dir
        if update:
            # Step 1 - Update the database
            self.__updateDatabase()
        # Step 2 - Read the database
        self.__readData()
        # Step 3 - Expand the data values
        self.__expandData()
        # Step 4 - Save the data
        self.__saveData()

    def __updateDatabase(self):
        self.ScraperResults.loop_scrape()
        self.ScraperRoster.loop_scrape()

    def __readData(self):
        leagues = [
            "EPL",
            "La liga",
            "Bundesliga",
            "Serie A",
            "Ligue 1",
            "RFPL",
        ]
        schema = [
            "h_a",
            "xG",
            "xGA",
            "npxG",
            "npxGA",
            "deep",
            "deep_allowed",
            "scored",
            "missed",
            "xpts",
            "result",
            "date",
            "wins",
            "draws",
            "loses",
            "pts",
            "npxGD",
            "ppda.att",
            "ppda.def",
            "ppda_allowed.att",
            "ppda_allowed.def",
        ]
        df = pd.DataFrame(columns=schema)

        def define_season(date_):
            if date_.month > 7:
                return int(date_.year)
            else:
                return int(date_.year) - 1

        for league in leagues:
            directoryPath = self.input_dir + "/" + league
            for file in Path(directoryPath).iterdir():
                if file.suffix == ".csv":
                    print(file)
                    df_temp = pd.read_csv(file, index_col=0)
                    df_temp["H team"] = (
                        str(file).split(".")[0].split("/")[-1].split("-")[1]
                    )
                    df_temp["team_id"] = int(
                        str(file).split(".")[0].split("/")[-1].split("-")[0]
                    )
                    df_temp["h_a_boolean"] = (
                        df_temp["h_a"]
                        .apply(lambda row: row == "h")
                        .astype(int)
                    )
                    df_temp["league"] = league
                    df_temp["datetime"] = pd.to_datetime(df_temp["date"])
                    df_temp["date"] = df_temp["datetime"].dt.date
                    df_temp["season"] = df_temp["date"].apply(
                        lambda row: define_season(row)
                    )
                    df = df.append(df_temp)
            df["team_id"] = df["team_id"].astype(int)
            df["season"] = df["season"].astype(int)
            df = df.reset_index()  # Reset the index otherwise it is a mess
            df.drop("index", axis=1, inplace=True)

            df_rosters = pd.read_csv(
                self.input_dir + "/" + "Rosters/rosters.csv"
            )

            self.df = df
            self.df_rosters = df_rosters

    def __expandData(self):
        schema_shift = [
            "season_points",
            "scored_goals_season",
            "missed_goals_season",
            "avg_ppda.att",
            "avg_ppda.def",
            "avg_ppda_allowed.att",
            "avg_ppda_allowed.def",
            "avg_deep",
            "avg_deep_allowed",
        ]
        # Global matchId
        self.df_rosters["date"] = pd.to_datetime(
            self.df_rosters["date"]
        ).dt.date  # Pre-processing to have date in the same format as
        for matchId in self.df_rosters["matchId"].unique():
            teams_ = self.df_rosters.loc[
                self.df_rosters["matchId"] == matchId, "team_id"
            ].unique()
            date_ = self.df_rosters.loc[
                self.df_rosters["matchId"] == matchId, "date"
            ].unique()[0]
            self.df.loc[
                (self.df["date"] == date_) & (self.df["team_id"].isin(teams_)),
                "matchId",
            ] = matchId
        # Adding more fields
        seasons = [2014 + ii for ii in range(8)]
        self.df.sort_values(by="date", inplace=True)
        for team_id in self.df["team_id"].unique():
            for season in seasons:
                idx = self.df.loc[
                    (self.df["team_id"] == team_id)
                    & (self.df["season"] == season),
                    :,
                ].index
                if len(idx) == 0:
                    continue
                grp = self.df.loc[idx, :].groupby("team_id")
                # sh_grp = grp.apply(lambda p: p.shift(fill_value=0).cumsum())
                # print(sh_grp)
                self.df.loc[idx, "season_points"] = self.df.loc[
                    idx, "pts"
                ].cumsum()
                self.df.loc[idx, "scored_goals_season"] = self.df.loc[
                    idx, "scored"
                ].cumsum()
                self.df.loc[idx, "missed_goals_season"] = self.df.loc[
                    idx, "missed"
                ].cumsum()
                self.df.loc[idx, "avg_ppda.att"] = self.df.loc[
                    idx, "ppda.att"
                ].cumsum() / (grp.cumcount() + 1)
                self.df.loc[idx, "avg_ppda.def"] = self.df.loc[
                    idx, "ppda.def"
                ].cumsum() / (grp.cumcount() + 1)
                self.df.loc[idx, "avg_ppda_allowed.att"] = self.df.loc[
                    idx, "ppda_allowed.att"
                ].cumsum() / (grp.cumcount() + 1)
                self.df.loc[idx, "avg_ppda_allowed.def"] = self.df.loc[
                    idx, "ppda_allowed.def"
                ].cumsum() / (grp.cumcount() + 1)
                self.df.loc[idx, "avg_deep"] = self.df.loc[
                    idx, "deep"
                ].cumsum() / (grp.cumcount() + 1)
                self.df.loc[idx, "avg_deep_allowed"] = self.df.loc[
                    idx, "deep_allowed"
                ].cumsum() / (grp.cumcount() + 1)
                # Shift the results
                idx_shift = idx[1:]
                self.df.loc[idx_shift, schema_shift] = self.df.loc[
                    idx[0:-2], schema_shift
                ]
                self.df.loc[idx[0], schema_shift] = 0  # Zeroing all the schema
        # Mirroring to get adversary teams
        for matchId in self.df["matchId"].unique():
            idx = self.df[self.df["matchId"] == matchId].index
            idxT = [idx[-1 + ii] for ii in range(len(idx))]
            self.df.loc[idx, "season_points_adv"] = self.df.loc[
                idxT, "season_points"
            ]
            self.df.loc[idx, "scored_goals_season_adv"] = self.df.loc[
                idxT, "scored_goals_season"
            ]
            self.df.loc[idx, "missed_goals_season_adv"] = self.df.loc[
                idxT, "missed_goals_season"
            ]
            self.df.loc[idx, "avg_ppda.att_adv"] = self.df.loc[
                idxT, "avg_ppda.att"
            ]
            self.df.loc[idx, "avg_ppda.def_adv"] = self.df.loc[
                idxT, "avg_ppda.def"
            ]
            self.df.loc[idx, "avg_ppda_allowed.att_adv"] = self.df.loc[
                idxT, "avg_ppda_allowed.att"
            ]
            self.df.loc[idx, "avg_ppda_allowed.def_adv"] = self.df.loc[
                idxT, "avg_ppda_allowed.def"
            ]
            self.df.loc[idx, "avg_deep_adv"] = self.df.loc[idxT, "avg_deep"]
            self.df.loc[idx, "avg_deep_allowed_adv"] = self.df.loc[
                idxT, "avg_deep_allowed"
            ]
            """
            for ii in idx:
                if self.df.loc[ii,'h_a'] == 'a':
                    self.df.loc[idx,'season_points_a'] = self.df.loc[ii,'season_points']
                    self.df.loc[idx,'scored_goals_season_a'] = self.df.loc[ii,'scored_goals_season']
                    self.df.loc[idx, 'missed_goals_season_a'] = self.df.loc[ii,'missed_goals_season']
                    self.df.loc[idx, 'avg_ppda.att_a'] = self.df.loc[ii,'avg_ppda.att']
                    self.df.loc[idx, 'avg_ppda.def_a'] = self.df.loc[ii,'avg_ppda.def']
                    self.df.loc[idx, 'avg_ppda_allowed.att_a'] = self.df.loc[ii,'avg_ppda_allowed.att']
                    self.df.loc[idx, 'avg_ppda_allowed.def_a'] = self.df.loc[ii,'avg_ppda_allowed.def']
                    self.df.loc[idx, 'avg_deep_a'] = self.df.loc[ii,'avg_deep']
                    self.df.loc[idx, 'avg_deep_allowed_a'] = self.df.loc[ii,'avg_deep_allowed']
                else:
                    self.df.loc[idx, 'season_points_h'] = self.df.loc[ii,'season_points']
                    self.df.loc[idx, 'scored_goals_season_h'] = self.df.loc[ii,'scored_goals_season']
                    self.df.loc[idx, 'missed_goals_season_h'] = self.df.loc[ii,'missed_goals_season']
                    self.df.loc[idx, 'avg_ppda.att_h'] = self.df.loc[ii,'avg_ppda.att']
                    self.df.loc[idx, 'avg_ppda.def_h'] = self.df.loc[ii,'avg_ppda.def']
                    self.df.loc[idx, 'avg_ppda_allowed.att_h'] = self.df.loc[ii,'avg_ppda_allowed.att']
                    self.df.loc[idx, 'avg_ppda_allowed.def_h'] = self.df.loc[ii,'avg_ppda_allowed.def']
                    self.df.loc[idx, 'avg_deep_h'] = self.df.loc[ii,'avg_deep']
                    self.df.loc[idx, 'avg_deep_allowed_h'] = self.df.loc[ii,'avg_deep_allowed']
            """

    def __saveData(self):
        self.df.to_csv(self.output_path)
