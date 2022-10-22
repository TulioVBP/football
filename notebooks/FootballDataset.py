import os

import pandas as pd
import torch
from torch.utils.data import Dataset


class FootballDataset(Dataset):
    """Football dataset."""

    def __init__(
        self,
        cat_par,
        num_par,
        target,
        league=None,
        season=None,
        csv_file="../data/processed/processed.csv",
    ):
        """Initializes instance of class FootballDataset.

        Args:
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

        self.y = self.football_frame[self.target]
        self.y[self.y > 2] = 2

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
