""" Function to predict the match results based on a trained model. WIP."""

import datetime
from pathlib import Path
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
# TODO - Add logger
def predict(config: DictConfig):
    data_prep(config)
    # Open next matches
    to_predict_path = abspath(config.to_predict.path)
    final_path = abspath(
        config.final.dir
        + "/"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M")
        + "_"
        + config.final.name
    )
    df_predict = pd.read_csv(to_predict_path)
    # Load the data loaders
    num_params = config.model.num_params
    cat_params = config.model.cat_params
    model_path = abspath(config.model.path)

    df_predict.dropna(subset=num_params, inplace=True)
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
    df_predict.reset_index(inplace=True)
    pts_to_str = {0: "l", 1: "d", 2: "w"}
    df_predict["h.predicted_result"] = pd.Series(predicted_results)
    df_predict["h.predicted_result"] = df_predict["h.predicted_result"].apply(
        lambda row: pts_to_str[row]
    )
    # Save to output
    df_predict[config.final.schema].to_csv(final_path)


def tensor_pipeline(num_par, cat_par, df):
    # Grouping variable names
    numerical = num_par
    categorical = cat_par

    # Dropping non-needed columns
    schema = numerical + categorical
    df = df[schema]

    # One-hot encoding of categorical variables
    football_frame = pd.get_dummies(df, prefix=categorical)
    football_frame["h_a_a"] = 0  # TODO make this workaround more robust

    # Dropping matches not available (mismatch between rosters and matches"

    # Save target and predictors
    return torch.tensor(football_frame.values).float()


def data_prep(config: DictConfig):
    # TODO add the date of the last match to understand how updated the prediction is
    # Read the reference latest stats
    processed_path = abspath(config.processed.path)
    df_proc = pd.read_csv(processed_path)
    df_proc.dropna(inplace=True)  # TODO limit to processed schema drop
    df_ref = df_proc.sort_values("date").groupby("team_id").tail(1)

    # Read the next matches
    files = Path(abspath(config.raw.future_matches_path)).glob("**/*.csv")
    schema = config.processed.schema_expanded
    schema_adv = config.processed.schema_expanded_adv
    schema_adv_map = {col: col + "_adv" for col in schema}
    df = pd.DataFrame()
    for file in files:
        df_temp = pd.read_csv(file)
        # Add home stats
        df_temp_h = df_temp.rename(columns={"h.id": "team_id"}).merge(
            df_ref.loc[:, schema], how="left", on="team_id"
        )
        df_temp_a = (
            df_temp.rename(columns={"a.id": "team_id"})
            .merge(df_ref.loc[:, schema], how="left", on="team_id")
            .rename(columns=schema_adv_map)
        )
        df_league = df_temp_h.merge(
            df_temp_a.loc[:, schema_adv], left_index=True, right_index=True
        )
        # Add missing fieldds
        df_league["h_a"] = "h"
        df = pd.concat([df, df_league], ignore_index=True)


if __name__ == "__main__":
    predict()
