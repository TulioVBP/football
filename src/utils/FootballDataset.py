import os

import pandas as pd
import torch
from torch.utils.data import Dataset


class FootballDataset(Dataset):
    """Football dataset. Used for PyTorch data loader."""

    def __init__(
        self,
        cat_par,
        num_par,
        target,
        league=None,
        season=None,
        csv_file="Data/Preprocessed/dataset.csv",
    ):
        """Initializes instance of class FootballDataset.

        Args:
            cat_par: categorical parameters used for the training
            num_par: numerical parameters used for the training
            target: the target feature. Currently supports only "pts" for softmax training.
            league: leagues used for the training. Default is all leagues.
            season: season used for the training. Default is all seasons.
            csv_file (str): Path to the csv file with the students data.

        """
        df = pd.read_csv(csv_file)

        # Filtering per league/season
        if league is not None:
            df = df[df["league"].isin(league)]
        if season is not None:
            df = df[df["season"].isin(season)]

        # Grouping variable names
        self.numerical = num_par
        self.categorical = cat_par
        self.target = target

        # Dropping non-needed columns
        schema = self.numerical + self.categorical + self.target
        df = df[schema]

        # One-hot encoding of categorical variables
        self.football_frame = pd.get_dummies(df, prefix=self.categorical)

        # Dropping matches not available (mismatch between rosters and matches"
        self.football_frame.dropna(subset=self.numerical, inplace=True)

        # Save target and predictors
        self.X = self.football_frame.drop(self.target, axis=1)

        # Capping the maximum return
        def capping(row):
            if row > 2:
                return 2
            else:
                return row

        self.football_frame.loc[self.football_frame["pts"] > 2, "pts"] = 2

        self.y = self.football_frame[self.target]

    def __len__(self):
        return len(self.football_frame)

    def __getitem__(self, idx):
        # Convert idx from tensor to list due to pandas bug (that arises when using pytorch's random_split)
        if isinstance(idx, torch.Tensor):
            idx = idx.tolist()
        return [
            torch.tensor(self.X.iloc[idx].values).float(),
            torch.tensor(self.y.iloc[idx].values).squeeze(),
        ]

    # Tests
