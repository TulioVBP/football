import logging
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import src.scraper as scraper


# Initialize logger - root
# 1. Using root logger to allow multiple modules to write in it
# logging.basicConfig(filename= f'logs/{str(date.today() )} - dashboard.log', format= '%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
# logging.info('Run start.')
## -- Load data --
@st.cache()
def load_data(
    leagues=["EPL", "La liga", "Bundesliga", "Serie A", "Ligue 1", "RFPL"],
    seasons=[2014 + ii for ii in range(8)],
):
    schema = [
        "team_id",
        "team",
        "league",
        "h_a",
        "xG",
        "xGA",
        "npxG",
        "npxGA",
        "deep",
        "deep_allowed",
        "scored",
        "missed",
        "xpts",
        "result",
        "date",
        "wins",
        "draws",
        "loses",
        "pts",
        "npxGD",
        "ppda.att",
        "ppda.def",
        "ppda_allowed.att",
        "ppda_allowed.def",
    ]
    df_teams = pd.DataFrame(columns=schema)
    for league in leagues:
        directoryPath = Path(f"Data/{league}")
        for file in directoryPath.iterdir():
            if file.suffix == ".csv":
                df_teams_temp = pd.read_csv(file, index_col=0)
                df_teams_temp["team_id"] = int(
                    str(file).split(".")[0].split("/")[2].split("-")[0]
                )
                df_teams_temp["team"] = (
                    str(file).split(".")[0].split("/")[2].split("-")[1]
                )
                df_teams_temp["league"] = league
                df_teams_temp["datetime"] = pd.to_datetime(
                    df_teams_temp["date"]
                )
                df_teams_temp["date"] = df_teams_temp["datetime"].dt.date
                df_teams = df_teams.append(df_teams_temp)
        # Sort by date
        df_teams.sort_values(by="date", inplace=True, ascending=False)
    df_rosters = pd.read_csv(Path("Data/Rosters/rosters.csv"), index_col=0)
    # Pre-processing
    df_rosters["date"] = pd.to_datetime(df_rosters["date"]).dt.date
    df_rosters.insert(loc=0, column="player_name", value=df_rosters["player"])
    df_rosters.drop("player", axis="columns", inplace=True)
    df_rosters = df_rosters.merge(right=df_teams, on=("team_id", "date"))
    return df_teams, df_rosters


def create_ha(df_teams):
    schema_ren = {
        "team": "team_h",
        "xG": "xG_h",
        "xGA": "xG_a",
        "npxG": "npxG_h",
        "npxGA": "npxG_a",
        "deep": "deep_h",
        "deep_allowed": "deep_a",
        "scored": "scored_h",
        "missed": "scored_a",
        "xpts": "xpts_h",
        "result": "result_h",
        "pts": "pts_h",
        "ppda.att": "ppda.att_h",
        "ppda.def": "ppda.def_h",
        "ppda_allowed.att": "ppda.att_a",
        "ppda_allowed.def": "ppda.def_a",
    }
    df_single = df_teams[df_teams["h_a"] == "h"].rename(schema_ren)
    df_single.merge()


## -- MAIN --
scrapeMatch = scraper.ScraperResults()  # Instatiate scrapper result
scrapeRoster = scraper.ScraperRosters()  # Instatiate scrapper rosters
df, df_rosters = load_data()
## -- Side bar --
st.sidebar.title("Data visualization")
league_s = st.sidebar.multiselect(options=df.league.unique(), label="League")
team_s = st.sidebar.multiselect(
    options=df[df["league"].isin(league_s)].team.unique(), label="Teams"
)
date_s = st.sidebar.date_input(
    label="Date range",
    value=(datetime.now().date() - timedelta(days=2), datetime.now().date()),
)

# Conditions for data visualization
b_teamCond_S = (
    (df["team"].isin(team_s))
    & (df["date"] >= date_s[0])
    & (df["date"] < date_s[1])
)
b_rostersCond_S = (
    (df_rosters["date"] >= date_s[0])
    & (df_rosters["date"] < date_s[1])
    & (df_rosters["team"].isin(team_s))
)

st.sidebar.markdown("# Scrapping data")
if st.sidebar.button("Scrappe matches"):
    scrapeMatch.loop_scrape()
if st.sidebar.button("Scrappe roosters"):
    scrapeRoster.loop_scrape()

## ---- MAIN PAGE ----
st.title("⚽ Footbal analysis")

## -- Match predicter --
st.markdown("## Match predicter")
league_p = st.selectbox(options=df.league.unique(), label="League P")
col1, col2 = st.columns(2)
team_pH = col1.selectbox(
    options=df[df["league"] == league_p].team.unique(), label="Home team"
)
team_pA = col2.selectbox(
    options=df[
        (df["league"] == league_p) & (df["team"] != team_pH)
    ].team.unique(),
    label="Away team",
)
b_teamCond_P = (
    ((df.team == team_pH) | (df.team == team_pA))
    & (df.date >= date_s[0])
    & (df.date < date_s[1])
)

# Metrics
deepR = 3  # number of games that are relevant
col1.metric(
    f"Average of xG last {deepR} games",
    value=np.round(df.loc[df.team == team_pH, "xG"].head(deepR).mean(), 2),
    delta=np.round(
        df.loc[df.team == team_pH, "xG"].head(deepR).mean()
        - df.loc[df.team == team_pH, "xG"].head(2 * deepR).tail(deepR).mean(),
        2,
    ),
)
col2.metric(
    f"Average of xG last {deepR} games",
    value=np.round(df.loc[df.team == team_pA, "xG"].head(deepR).mean(), 2),
    delta=np.round(
        df.loc[df.team == team_pA, "xG"].head(deepR).mean()
        - df.loc[df.team == team_pA, "xG"].head(2 * deepR).tail(deepR).mean(),
        2,
    ),
)
col1.metric(
    f"Average of xpts last {deepR} games",
    value=np.round(df.loc[df.team == team_pH, "xpts"].head(deepR).mean(), 2),
    delta=np.round(
        df.loc[df.team == team_pH, "xpts"].head(deepR).mean()
        - df.loc[df.team == team_pH, "xpts"]
        .head(2 * deepR)
        .tail(deepR)
        .mean(),
        2,
    ),
)
col2.metric(
    f"Average of xpts last {deepR} games",
    value=np.round(df.loc[df.team == team_pA, "xpts"].head(deepR).mean(), 2),
    delta=np.round(
        df.loc[df.team == team_pA, "xpts"].head(deepR).mean()
        - df.loc[df.team == team_pA, "xpts"]
        .head(2 * deepR)
        .tail(deepR)
        .mean(),
        2,
    ),
)
col1.metric(
    f"Average of deep passes last {deepR} games",
    value=np.round((df.loc[df.team == team_pH, "deep"]).head(deepR).mean(), 2),
    delta=np.round(
        (df.loc[df.team == team_pH, "deep"]).head(deepR).mean()
        - (df.loc[df.team == team_pH, "deep"])
        .head(2 * deepR)
        .tail(deepR)
        .mean(),
        2,
    ),
)
col2.metric(
    f"Average of deep passes last {deepR} games",
    value=np.round(df.loc[df.team == team_pA, "deep"].head(deepR).mean(), 2),
    delta=np.round(
        (df.loc[df.team == team_pA, "deep"]).head(deepR).mean()
        - (df.loc[df.team == team_pA, "deep"])
        .head(2 * deepR)
        .tail(deepR)
        .mean(),
        2,
    ),
)

with st.expander("Expected goals", False):
    fig = px.line(df[b_teamCond_P], x="date", y="xG", color="team")
    st.plotly_chart(fig)
with st.expander("Campaign", False):
    df_camp = df.loc[b_teamCond_P, ("date", "team", "pts")].sort_values(
        by="date"
    )
    df_camp["cum_pts"] = 0
    for team in df_camp["team"].unique():
        df_camp.loc[df_camp["team"] == team, "cum_pts"] = df_camp.loc[
            df_camp["team"] == team, "pts"
        ].cumsum()
    fig = px.line(df_camp, x="date", y="cum_pts", color="team")
    st.plotly_chart(fig)

st.markdown("## Raw data")

with st.expander("Matches", False):
    try:  # | (df['league'].isin(league_s))
        st.write(df.loc[b_teamCond_S, :])
    except ValueError:
        st.write(df)

with st.expander("Rosters", False):
    st.write(df_rosters[b_rostersCond_S].sort_values(by="date"))
