"""
This function process the raw data scrapped from web, process it and save an expanded database.
"""

import imp
from pathlib import Path

import hydra
from hydra.utils import to_absolute_path as abspath
from omegaconf import DictConfig

from utils.DataPreprocessing import DataPreprocessing


@hydra.main(config_path="../config", config_name="main")
def process_data(config: DictConfig, update=False):
    """Function to process the data
    Args:
        update: if set to True, will update the database after scraping newer match results."""
    DataPreprocessing(
        abspath(config.processed.path), abspath(config.raw.dir), update
    )


if __name__ == "__main__":
    process_data()
