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
        df.loc[df[self.target[0]] > 2, self.target[0]] = 2

        # One-hot encoding of categorical variables
        self.football_frame = pd.get_dummies(df,columns = self.categorical)#, prefix=self.categorical)

        # Save target and predictors
        X = self.football_frame.drop(self.target, axis=1)
        y = self.football_frame[self.target]
        
        self.X = torch.tensor(X.values).float()
        self.y = torch.tensor(y.values).long().flatten()

    def __len__(self):
        return len(self.football_frame)

    def __getitem__(self, idx):
        # Convert idx from tensor to list due to pandas bug (that arises when using pytorch's random_split)
        #if isinstance(idx, torch.Tensor):
        #    idx = idx.tolist()
        return [self.X[idx],
                self.y[idx]]
        #return [torch.tensor(self.X.iloc[idx].values).float(), 
        #        torch.tensor(self.y.iloc[idx].values).int().flatten().flatten()]