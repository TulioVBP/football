from unicodedata import name

import hydra
import numpy as np
import pandas as pd
import torch


@hydra.main(config_path="../config", config_name="main")
# TODO - Predict future matches
def predict():
    pass


if __name__ == "__main__":
    predict()
