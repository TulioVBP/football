"""This submodule presents two classes for scraping results from the web. To scrape, set the update flag of process.py to True."""

import codecs
import json
import logging
import os
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import json_normalize

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

fileHandler = logging.FileHandler(f"logs/{str(date.today() )} - scrape.log")
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)


class ScraperResults:
    def __init__(
        self,
        parent_folder="data/raw/",
        leagues=["EPL", "La liga", "Bundesliga", "Serie A", "Ligue 1", "RFPL"],
        seasons=[2014 + ii for ii in range(8)],
    ) -> None:
        self.leagues = leagues  # Initialize the leagues
        self.seasons = seasons  # Initialize the seasons
        self.parent_folder = parent_folder

    def loop_scrape(self):
        # Step 0 - Create folder
        parentPath = Path(self.parent_folder)
        if parentPath.is_dir() is not True:
            parentPath.mkdir()
        for league in self.leagues:
            # Step 1 - Create league and players folder
            logger.info(f"Scrapping {league} ...")
            directoryPath = parentPath.joinpath(league)
            if directoryPath.is_dir() is not True:
                directoryPath.mkdir()

            players_directoryPath = directoryPath.joinpath("PLAYERS")
            if players_directoryPath.is_dir() is not True:
                players_directoryPath.mkdir()

            for season in self.seasons:
                logger.info(f"Scrapping season {str(season)} ...")
                # Step 2 - Obtain website soup for the given league and season
                url = (
                    "https://understat.com/league/"
                    + league
                    + "/"
                    + str(season)
                )
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                file = open("text.txt", "w+")
                file.write(str(soup))
                file.close()

                # Step 3 - Parse all the script files
                scripts = soup.find_all("script")

                # Step 4 - Find the team's data script and trim the JSON
                for script in scripts:
                    if "var teamsData" in str(script):
                        # I store that text, then trim off the string on the ends so that
                        # it's in a valid json format
                        encoded_string = str(script)
                        encoded_string = encoded_string.split(
                            "JSON.parse('", 1
                        )[-1]
                        # encoded_string = encoded_string.rsplit("=",1)[0]
                        encoded_string = encoded_string.rsplit("');", 1)[0]
                        # Have it ignore the escape characters so it can decode the ascii
                        # and be able to use json.loads
                        jsonStr = codecs.getdecoder("unicode-escape")(
                            encoded_string
                        )[0]
                        jsonObj = json.loads(jsonStr)
                        df = json_normalize(jsonObj)

                        # Step 5: Extract team's data
                        for col_name in df.columns:
                            col = df[col_name]
                            id = int(col_name.split(".")[0])
                            feat = col_name.split(".")[1]

                            if feat == "title":
                                teams_name = col[0]  # + str(season)
                            elif feat == "id":
                                id = col[0]
                            elif feat == "history":
                                db = json_normalize(col[0])
                                # filePath = Path(f'{parent_folder}{league}/{str(id)}-{teams_name}.csv')
                                filePath = directoryPath.joinpath(
                                    f"{str(id)}-{teams_name}.csv"
                                )
                                if filePath.exists():
                                    df_old = pd.read_csv(filePath, index_col=0)
                                    # Verify if entry was obtained already, otherwise input
                                    if not (
                                        df_old["date"] == db.loc[0, "date"]
                                    ).any():
                                        df_new = df_old.append(
                                            db, ignore_index=True
                                        )
                                        df_new.to_csv(filePath)
                                else:
                                    db.to_csv(filePath)
                        logger.info("\t ... Scrapping done!")

                    if "var playersData" in str(script):
                        # I store that text, then trim off the string on the ends so that
                        # it's in a valid json format
                        encoded_string = str(script)
                        encoded_string = encoded_string.split(
                            "JSON.parse('", 1
                        )[-1]
                        # encoded_string = encoded_string.rsplit("=",1)[0]
                        encoded_string = encoded_string.rsplit("');", 1)[0]
                        # Have it ignore the escape characters so it can decode the ascii
                        # and be able to use json.loads
                        jsonStr = codecs.getdecoder("unicode-escape")(
                            encoded_string
                        )[0]
                        jsonObj = json.loads(jsonStr)
                        db = json_normalize(jsonObj)
                        # Step 5: Extract players's data
                        # filePath = Path(f'{parent_folder}{league}/PLAYERS/{str(season)}.csv')
                        filePath = players_directoryPath.joinpath(
                            f"{str(season)}.csv"
                        )
                        if filePath.exists():
                            if season == 2020:
                                db.to_csv(filePath)
                        else:
                            db.to_csv(filePath)


# %%
class ScraperRosters:
    def __init__(self, parent_folder="data/raw/Rosters"):
        self.parent_folder = parent_folder
        pass

    def loop_scrape(self):
        # Load directory
        directoryPath = Path(self.parent_folder).joinpath("Rosters")
        logger.info(f"Looping over {directoryPath}")
        filePath = directoryPath.joinpath("rosters.csv")
        if filePath.exists():
            df = pd.read_csv(filePath, index_col=0)
            matchId_prev = df["matchId"].max()
            logger.info(f"Most recent matchId for rosters: {matchId_prev}")
        else:
            df = pd.DataFrame()
            matchId_prev = 0
        # Iterate over matches
        upper_lim = 25000
        delta = 1000
        while (upper_lim - matchId_prev) > delta + 1:
            for matchId in range(
                matchId_prev + 1, matchId_prev + delta
            ):  # Guessing a maximum of 20.000 matches
                url = "https://understat.com/match/" + str(matchId)
                try:
                    response = requests.get(url)
                except ConnectionError:
                    logger.error(f"Connection error for game {matchId}")
                else:
                    if response.status_code == 200:
                        logger.info(f"OK for {matchId}")
                        soup = BeautifulSoup(response.text, "html.parser")
                        header = soup.find(
                            "div", class_="header-wrapper"
                        )  # Extracting the header of the page
                        score = [
                            header.find("span").text.split(" - ")[0][-1],
                            header.find("span").text.split(" - ")[1][0],
                        ]
                        breadcrumb = soup.find("ul", class_="breadcrumb")
                        # Extracting date
                        date = breadcrumb.find_all("li")[-1].text
                        scripts = soup.find_all("script")
                        # Scripts with data
                        for script in scripts:
                            if "var rostersData" in str(script):
                                # I store that text, then trim off the string on the ends so that
                                # it's in a valid json format
                                encoded_string = str(script)
                                encoded_string = encoded_string.split(
                                    "JSON.parse('", 1
                                )[-1]
                                # encoded_string = encoded_string.rsplit("=",1)[0]
                                encoded_string = encoded_string.rsplit(
                                    "');", 1
                                )[0]
                                # Have it ignore the escape characters so it can decode the ascii
                                # and be able to use json.loads
                                jsonStr = codecs.getdecoder("unicode-escape")(
                                    encoded_string
                                )[0]
                                jsonObj = json.loads(jsonStr)
                                # Due to the many levels, we create a list of dicts to be processed by json_normalize
                                jsonObjH = [
                                    jsonObj["h"][ii]
                                    for ii in list(jsonObj["h"])
                                ]
                                jsonObjA = [
                                    jsonObj["a"][ii]
                                    for ii in list(jsonObj["a"])
                                ]
                                db_h = pd.json_normalize(jsonObjH).set_index(
                                    "id"
                                )
                                db_a = pd.json_normalize(jsonObjA).set_index(
                                    "id"
                                )
                                db = pd.concat([db_h, db_a])
                                db["date"] = date
                                db["homeScore"] = score[0]
                                db["awayScore"] = score[1]
                                db["matchId"] = matchId
                                break
                        df = pd.concat([df, db])
                    else:
                        logger.info(f"Not OK for {matchId}")
            # Save file
            df.to_csv(filePath)
            matchId_prev = matchId
        logger.info("\t ... Scrapping done!")
