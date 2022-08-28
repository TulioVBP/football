# How to run this package

## Setup the environment

Run the below commands to setup the virtual environment (using poetry):

    make activate
    make setup

# Reference

## Football predicter

### Problem: Predicting football results based on team performance

In this notebook, we build, train, validate, and test a Neural Network with PyTorch to predict the __target_label__ field (win, draw, lose) of the upcoming matches

1. <a href="#1">Read the dataset</a>
    * <a href='#11'> Select features to build the model </a>
2. <a href="#2">Data Processing</a>
    * <a href="#21">Data Preprocessing (cleaning)</a>
    * <a href="#22">Train - Validation - Test Datasets</a>
    * <a href="#23">Data processing with Pipeline and ColumnTransformer</a>
3. <a href="#3">Neural Network Training and Validation</a>
4. <a href="#4">Test the Neural Network</a>
5. <a href="#5">Improvement ideas</a>


__Rosters schema:__ 
- __id:__ (INT) Identifier of roster, which is unique for a player and match
- __goals:__ (INT) Number of goals scored by player in that match
- __shots:__ (INT) Number of shots to the goal for that player
- __own_goals:__ (INT) Number of own goals scored by player in that match
- __xG:__ (FLOAT) Expected goals for that player
- __time:__ (INT) Field time in minutes of player
- __player_id:__ (INT) Unique identifier for that player.
- __team_id:__(INT) Unique identifier of that team
- __position:__(INT) Position played by that player
- __player:__(STR) Name of the player
- __h_a:__(STR, ['h','a']) Home or away
- __yellow_card:__(INT,[0,1,2]) Number of yellow cards
- __red_card:__(INT,[0,1]) Number of red cards
- __roster_in:__ (INT) ID of roster that substitued this player
- __roster_out:__ (INT) ID of roster that left to give place to this player
- __key_passes:__ (INT) number of key passes
- __assists:__ (INT) number of assists to goals
- __xA:__ (FLOAT) expected assists to goals
- __xGChain:__ (FLOAT) expected goals chain
- __xGBuildup:__ (FLOAT) expected goals buildup
- __positionOrder:__ (INT) order in lineup position
- __date:__ (DATE) date of match
- __homeScore:__ (INT) Score of home team
- __awayScore:__ (INT) Score of away team
- __matchId:__ (INT) Unique identifier of the match

__Teams schema:__
- __matchId:__ (INT) Unique identifier of the match
- __teamId:__ (INT) Unique identifier of the team
- __h_a:__ (STR, ['h','a']) Home or away
- __xG:__ (FLOAT) Expected goals for the team
- __xGA:__ (FLOAT) Expected goals against
- __npxG:__ (FLOAT) Expected goals for the team (excluding penalties and own goals)
- __npxGA:__ (FLOAT) Expected goals against (excluding penalties and own goals)
- __deep:__ (FLOAT) Passes completed within an estimated 20 yards of goal (crosses excluded)
- __deep_allowed:__ (FLOAT) Allowed deep passes for the opposite team
- __scored:__ (INT) Goals scored
- __missed:__ (INT) Goals scored against
- __xpts:__ (FLOAT) Expected points
- __result:__ (STR, ['l','w','d']) Match result, win, draw, or loss
- __wins:__ (BOOLEAN) True if team wins
- __draws:__ (BOOLEAN) True if team draws
- __loses:__ (BOOLEAN) True if team loses
- __pts:__ (INT) Points gained for that team
- __npxGD:__ (FLOAT) Difference between expected goals for and against, excluding penalties and own goals.
- __ppda.att:__ (FLOAT) Passes per defensive action in the attack part of the field (PPDA metric is calculated by dividing the number of passes allowed by the defending team by the total number of defensive actions.)
- __ppda.def:__ (FLOAT) Passes per defensive action in the defensive part of the field.
- __ppda_allowed.att:__ (FLOAT) Opponent passes per defensive action in the attack part of the field.
- __ppda_allowed.def:__ (FLOAT) Opponent passes per defensive action in the defensive part of the field.

__Additional fields:__
- __home_points:__ (INT) Points in season before match for home team
- __away_points:__ (INT) Points in season before match for away team
- __scored_goals_season_h:__ (INT) Goals scored in season for home team
- __missed_goals_season_h:__ (INT) Goals missed in season for home team
- __scored_goals_season_a:__ (INT) Goals scored in season for away team
- __missed_goals_season_a:__ (INT) Goals missed in season for away team
- __league:__ (STR) League of the match
- __season:__ (INT) Season of the match
- __(TO BE INSERTED)n_points_h:__ (INT) Points earned in the last N encounters for home team
- __(TO BE INSERTED)n_points_a:__ (INT) Points earned in the last N encounters for away team
- __(TO BE INSERTED)top_assists_h:__ (FLOAT) Highest individual season assists.
- __(TO BE INSERTED)top_score_a:__ (FLOAT) Highest individual season score in squad
- __avg_ppda.att_h:__(FLOAT) Season average of ppda.att for host team
- __avg_ppda.def_h:__(FLOAT) Season average of ppda.def for host team
- __avg_ppda.att_a:__(FLOAT) Season average of ppda.att for visiting team
- __avg_ppda.def_a:__(FLOAT) Season average of ppda.def for visiting team
- __avg_ppda_allowed.att_h:__(FLOAT) Season average of ppda_allowed.att for host team
- __avg_ppda_allowed.def_h:__(FLOAT) Season average of ppda_allowed.def for host team
- __avg_ppda_allowed.att_a:__(FLOAT) Season average of ppda_allowed.att for visiting team
- __avg_ppda_allowed.def_a:__(FLOAT) Season average of ppda_allowed.def for visiting team 
- __avg_deep_h:__(FLOAT) Season average of deep passes for host team
- __avg_deep_a:__(FLOAT) Season average of deep passes for visitor team
- __avg_deep_allowed_h:__ (FLOAT) Season average of allowed deep passes for host team
- __avg_deep_allowed_a:__ (FLOAT) Season average of allowed deep passes for visitor team
... to be continued
