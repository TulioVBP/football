#%%
from bs4 import BeautifulSoup
import requests
import json
import codecs
import pandas as pd
import os
from pathlib import Path
import logging

# Initialize log file
logging.basicConfig(filename="logs/log_roster_scrapper.log", level=logging.DEBUG)
# Create directory for rosters
directoryPath = Path('Data/Rosters/')
if directoryPath.is_dir() != True:
            directoryPath.mkdir()

roster_db = directoryPath.joinpath('rosters.csv')

# Load directory
if directoryPath.joinpath('rosters.csv').exists():
    df = pd.read_csv(roster_db,index_col=0)
    matchId_prev = df['matchId'].max()
else:
    df = pd.DataFrame()
    matchId_prev = 0

# Iterate over matches
upper_lim = 20000
delta = 1000
while (upper_lim- matchId_prev)> delta+1:
    for matchId in range(matchId_prev+1,matchId_prev+delta): # Guessing a maximum of 20.000 matches
        url = 'https://understat.com/match/'+str(matchId)
        try:
            response = requests.get(url)
        except ConnectionError:
            logging.error('Connection error for game ' + matchId)
        else:
            if response.status_code == 200:
                logging.debug(f'OK for {matchId}')
                soup = BeautifulSoup(response.text, 'html.parser')
                header = soup.find('div', class_ = 'header-wrapper') # Extracting the header of the page
                score = [header.find('span').text.split(' - ')[0][-1], header.find('span').text.split(' - ')[1][0]]
                breadcrumb = soup.find('ul',class_ = 'breadcrumb'); # Extracting date
                date = breadcrumb.find_all('li')[-1].text
                scripts = soup.find_all('script'); # Scripts with data
                for script in scripts:
                    if 'var rostersData' in str(script):
                        # I store that text, then trim off the string on the ends so that 
                        # it's in a valid json format
                        encoded_string = str(script)
                        encoded_string  = encoded_string.split("JSON.parse('",1)[-1]
                        #encoded_string = encoded_string.rsplit("=",1)[0]
                        encoded_string = encoded_string.rsplit("');",1)[0]
                        # Have it ignore the escape characters so it can decode the ascii 
                        # and be able to use json.loads
                        jsonStr = codecs.getdecoder('unicode-escape')(encoded_string)[0]
                        jsonObj = json.loads(jsonStr)
                        # Due to the many levels, we create a list of dicts to be processed by json_normalize
                        jsonObjH = [jsonObj['h'][ii] for ii in list(jsonObj['h'])]
                        jsonObjA = [jsonObj['a'][ii] for ii in list(jsonObj['a'])]
                        db_h = pd.json_normalize(jsonObjH).set_index('id')
                        db_a = pd.json_normalize(jsonObjA).set_index('id')
                        db = db_h.append(db_a)
                        db['date'] = date
                        db['homeScore'] = score[0]
                        db['awayScore'] = score[1]
                        db['matchId'] = matchId
                        break
                df = df.append(db)
            else:
                logging.debug(f'Not OK for {str(matchId)}')
    # Save file
    df.to_csv(roster_db)
    matchId_prev = matchId