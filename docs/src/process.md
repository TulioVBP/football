Module src.process
==================
This function process the raw data scrapped from web, process it and save an expanded database.

Functions
---------

    
`process_data(config: omegaconf.dictconfig.DictConfig, update=False)`
:   Function to process the data
    Args:
        update: if set to True, will update the database after scraping newer match results.