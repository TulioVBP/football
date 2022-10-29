Module src.utils.DataPreprocessing
==================================

Classes
-------

`DataPreprocessing(output_path, input_dir, update=False)`
:   Class to process data. Called by process.py in main src folder.
    
    Initializes instance of the class DataPreprocessing.
    
    Args:
        output_path: parent directory for the processed data. Defined in the config file.
        input_dir: parent directory of the raw data. Defined in the config file. 
        update: if set to True, will update the database by scraping the web for newer results.