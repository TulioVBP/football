Module src.utils.FootballDataset
================================

Classes
-------

`FootballDataset(cat_par, num_par, target, league=None, season=None, csv_file='Data/Preprocessed/dataset.csv')`
:   Football dataset. Used for PyTorch data loader.
    
    Initializes instance of class FootballDataset.
    
    Args:
        cat_par: categorical parameters used for the training
        num_par: numerical parameters used for the training
        target: the target feature. Currently supports only "pts" for softmax training.
        league: leagues used for the training. Default is all leagues.
        season: season used for the training. Default is all seasons.
        csv_file (str): Path to the csv file with the students data.

    ### Ancestors (in MRO)

    * torch.utils.data.dataset.Dataset
    * typing.Generic