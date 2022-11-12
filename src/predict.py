""" Function to predict the match results based on a trained model. WIP."""

from unicodedata import name

import hydra
import numpy as np
import pandas as pd
import torch
from hydra.utils import to_absolute_path as abspath
from omegaconf import DictConfig
from torch import nn
from yaml import load

from utils.load_data_football import load_data_football


@hydra.main(config_path="../config", config_name="main")
# TODO - Predict future matches
# TODO - Create function to pull the next matches and create the "to_predict" file. The approach below assumes the to predict data is ready.
def predict(config: DictConfig):
    # Open next matches
    to_predict_path = abspath(config.to_predict.path)
    final_path = abspath(config.final.path)
    df_predict = pd.read_csv(to_predict_path)
    # Load the data loaders
    num_params = config.model.num_params
    cat_params = config.model.cat_params
    model_path = abspath(config.model.path)
    # target = ["pts"]
    # predict_iter = load_data_football(num_par=num_params, cat_par=cat_params,target=target,input_path=to_predict_path,to_predict=True)
    X = tensor_pipeline(
        num_params, cat_params, df_predict
    )  # return the tensor
    input_size = X.shape[1]

    # Load the default model
    model = nn.Sequential(
        nn.Flatten(), nn.Linear(input_size, 3), nn.ReLU(), nn.Linear(3, 3)
    )
    model.load_state_dict(torch.load(model_path))

    # Predict result
    predicted_results = model(X).argmax(axis=1)
    df_predict = pd.concat(
        df_predict,
        pd.DataFrame(predicted_results, columns=["Expected result"]),
    )

    # Save to output
    df_predict.to_csv(final_path)


def tensor_pipeline(num_par, cat_par, df):
    # Grouping variable names
    numerical = num_par
    categorical = cat_par

    # Dropping non-needed columns
    schema = numerical + categorical
    df = df[schema]

    # One-hot encoding of categorical variables
    football_frame = pd.get_dummies(df, prefix=categorical)

    # Dropping matches not available (mismatch between rosters and matches"
    football_frame.dropna(subset=numerical, inplace=True)

    # Save target and predictors
    return torch.tensor(football_frame.values).float()


if __name__ == "__main__":
    predict()
