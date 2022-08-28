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
def process_data(config: DictConfig, update=False):
    """Function to process the data"""
    DataPreprocessing(
        abspath(config.processed.path), abspath(config.raw.dir), update
    )


if __name__ == "__main__":
    process_data()
