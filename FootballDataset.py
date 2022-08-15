import os
import pandas as pd
from torch.utils.data import Dataset
import torch

class FootballDataset(Dataset):
    """Football dataset."""

    def __init__(self,cat_par, num_par, target, csv_file = "Data/Preprocessed/dataset.csv"):
        """Initializes instance of class FootballDataset.

        Args:
            csv_file (str): Path to the csv file with the students data.

        """
        df = pd.read_csv(csv_file)

        # Grouping variable names
        self.numerical = num_par
        self.categorical = cat_par
        self.target = target

        # Dropping non-needed columns
        schema = self.numerical + self.categorical + self.target
        df = df[schema]

        # One-hot encoding of categorical variables
        self.football_frame = pd.get_dummies(df, prefix=self.categorical)

        # Save target and predictors
        self.X = self.football_frame.drop(self.target, axis=1)
        self.y = self.football_frame[self.target]

    def __len__(self):
        return len(self.football_frame)

    def __getitem__(self, idx):
        # Convert idx from tensor to list due to pandas bug (that arises when using pytorch's random_split)
        if isinstance(idx, torch.Tensor):
            idx = idx.tolist()
        return [self.X.iloc[idx].values, self.y[idx]]