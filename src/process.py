"""
This is the demo code that uses hydra to access the parameters in under the directory config.
"""

import imp
from pathlib import Path

import hydra
from hydra.utils import to_absolute_path as abspath
from omegaconf import DictConfig

from DataPreprocessing import DataPreprocessing


@hydra.main(config_path="../config", config_name="main")
def process_data(config: DictConfig):
    """Function to process the data"""
    DataPreprocessing(abspath(config.processed.path), abspath(config.raw.dir))
    # processed_path = abspath(config.processed.path)
    # print(f"Process data using {raw_path}")
    # print(f"Columns used: {config.process.use_columns}")
    return 0


if __name__ == "__main__":
    process_data()
