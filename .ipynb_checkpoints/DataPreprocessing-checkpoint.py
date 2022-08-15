import pandas as pd
from pathlib import Path
from scraper import ScraperResults, ScraperRosters

class DataPreprocessing:
    def __init__(self, update = False):
        self.ScraperResults = ScraperResults()
        self.ScraperRoster = ScraperRosters()
        # Step 1 - Update the database
        if update: 
            self.__updateDatabase()
        # Step 2 - Read the database
        self.__readData()
        # Step 3 - Expand the data values
        self.__expandData()
        # Step 4 - Save the data
        self.__saveData()

    def __updateDatabase(self):
        self.ScraperResults.loop_scrape()
        self.ScraperRoster.loop_scrape()

    def __readData(self, league_data_path = 'Data/', rosters_data_path = 'Data/Rosters/rosters.csv'):
        leagues = ["EPL", "La liga", "Bundesliga","Serie A","Ligue 1","RFPL"]
        schema = ['h_a','xG','xGA','npxG','npxGA','deep','deep_allowed','scored','missed','xpts','result','date','wins','draws','loses','pts','npxGD','ppda.att','ppda.def','ppda_allowed.att','ppda_allowed.def']
        df = pd.DataFrame(columns=schema)
        def define_season(date_):
            if date_.month > 7:
                return int(date_.year)
            else:
                return int(date_.year)-1
            
        for league in leagues:
            directoryPath = Path(league_data_path + league)
            for file in directoryPath.iterdir():
                if file.suffix == '.csv':
                    print(file)
                    df_temp = pd.read_csv(file, index_col=0)
                    df_temp['H team'] = str(file).split('.')[0].split('/')[2].split('-')[1]
                    df_temp['team_id'] = int(str(file).split('.')[0].split('/')[2].split('-')[0])
                    df_temp['h_a_boolean'] = df_temp['h_a'].apply(lambda row: row == 'h').astype(int)
                    df_temp['league'] = league
                    df_temp['datetime'] = pd.to_datetime(df_temp['date'])
                    df_temp['date'] = df_temp['datetime'].dt.date
                    df_temp['season'] = df_temp['date'].apply(lambda row: define_season(row))
                    df = df.append(df_temp)
            df['team_id'] = df['team_id'].astype(int)
            df['season'] = df['season'].astype(int) 
            df = df.reset_index() # Reset the index otherwise it is a mess
            df.drop('index',axis = 1,inplace = True)

            df_rosters = pd.read_csv(rosters_data_path)

            self.df = df
            self.df_rosters = df_rosters
    
    def __expandData(self):
        # Global matchId
        self.df_rosters['date'] = pd.to_datetime(self.df_rosters['date']).dt.date # Pre-processing to have date in the same format as 
        for matchId in self.df_rosters['matchId'].unique():
            teams_ = self.df_rosters.loc[self.df_rosters['matchId'] == matchId,'team_id'].unique()
            date_ = self.df_rosters.loc[self.df_rosters['matchId'] == matchId,'date'].unique()[0]
            self.df.loc[(self.df['date'] == date_)&(self.df['team_id'].isin(teams_)),'matchId'] = matchId
        # Adding more fields
        seasons = [2014 + ii for ii in range(8)]
        self.df.sort_values(by = 'date',inplace = True)
        for team_id in self.df['team_id'].unique():
            for season in seasons:
                idx = (self.df['team_id'] == team_id) & (self.df['season'] == season)
                grp = self.df[idx].groupby('team_id')
                #sh_grp = grp.apply(lambda p: p.shift(fill_value=0).cumsum())
                #print(sh_grp)
                self.df.loc[idx,'home_points'] = self.df[idx].pts.cumsum()
                self.df.loc[idx,'scored_goals_season_h'] = self.df[idx].scored.cumsum()
                self.df.loc[idx,'missed_goals_season_h'] = self.df[idx].missed.cumsum()
                self.df.loc[idx,'avg_ppda.att_h'] = self.df.loc[idx,'ppda.att'].cumsum()/(grp.cumcount()+1)
                self.df.loc[idx,'avg_ppda.def_h'] = self.df.loc[idx,'ppda.def'].cumsum()/(grp.cumcount()+1)
                self.df.loc[idx,'avg_ppda_allowed.att_h'] = self.df.loc[idx,'ppda_allowed.att'].cumsum()/(grp.cumcount()+1)
                self.df.loc[idx,'avg_ppda_allowed.def_h'] = self.df.loc[idx,'ppda_allowed.def'].cumsum()/(grp.cumcount()+1)
                self.df.loc[idx,'avg_deep_h']= self.df.loc[idx,'deep'].cumsum()/(grp.cumcount()+1)
                self.df.loc[idx,'avg_deep_allowed_h']= self.df.loc[idx,'deep_allowed'].cumsum()/(grp.cumcount()+1)
        
    def __saveData(self, path_ = 'Data/Preprocessed'):
        self.df.to_csv(path_ + 'processedData.csv')

