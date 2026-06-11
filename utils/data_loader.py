# import pandas as pd
# import streamlit as st
# import os
# from db import engine

# DATA_FILE = "PlayerStatistics.xlsx"
# NUMERIC_COLS = [
#     "Age", "MP", "Starts", "MinutesPlayed", "PlayingTime_90s",
#     "Goals", "Assists", "GoalContributions", "NonPenaltyGoals",
#     "PenaltiesScored", "PenaltiesAttempted", "YellowCards", "RedCards",

#     "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
#     "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90",

#     "Shots", "ShotsOnTarget", "ShotsOnTargetPct",
#     "ShotsPer90", "ShotsOnTargetPer90",
#     "GoalsPerShot", "GoalsPerShotOnTarget",

#     "FoulsCommitted", "FoulsDrawn", "Offsides", "Crosses",
#     "Interceptions", "TacklesWon",
#     "PenaltiesWon", "PenaltiesConceded", "OwnGoals",

#     "SecondYellowRedCards", "MiscYellowCards", "MiscRedCards"
# ]



# @st.cache_data
# def load_data(filepath: str = DATA_FILE) -> pd.DataFrame:
#     if not os.path.exists(filepath):
#         return pd.DataFrame()

#     df = pd.read_excel(filepath)

#     for col in NUMERIC_COLS:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce")

#     if "Nation" in df.columns:
#         df["Nation"] = df["Nation"].astype(str).str.strip()
#     if "PlayerID" in df.columns:
#         df["PlayerID"] = df["PlayerID"].astype(str).str.strip()

#     return df

# # @st.cache_data
# # def load_data() -> pd.DataFrame:

# #     query = """
# #     SELECT *
# #     FROM player_stats
# #     """

# #     df = pd.read_sql(query, engine)
# #     df.columns = [
# #         "Player", "Nation", "ClubName", "League", "PlayerID", "PlayerURL",
# #         "Season", "Age", "Squad", "Country", "Comp", "MP", "Starts",
# #         "MinutesPlayed", "PlayingTime_90s", "Goals", "Assists",
# #         "GoalContributions", "NonPenaltyGoals", "PenaltiesScored",
# #         "PenaltiesAttempted", "YellowCards", "RedCards", "GoalsPer90",
# #         "AssistsPer90", "GoalContributionsPer90", "NonPenaltyGoalsPer90",
# #         "NonPenaltyGoalContributionsPer90", "Matches",
# #         "MiscYellowCards", "MiscRedCards", "SecondYellowRedCards",
# #         "FoulsCommitted", "FoulsDrawn", "Offsides", "Crosses",
# #         "Interceptions", "TacklesWon", "PenaltiesWon",
# #         "PenaltiesConceded", "OwnGoals", "ShootingGoals",
# #         "Shots", "ShotsOnTarget", "ShotsOnTargetPct",
# #         "ShotsPer90", "ShotsOnTargetPer90", "GoalsPerShot",
# #         "GoalsPerShotOnTarget", "ShootingPenaltiesScored",
# #         "ShootingPenaltiesAttempted", "last_updated"
# #     ]

# #     for col in NUMERIC_COLS:
# #         if col in df.columns:
# #             df[col] = pd.to_numeric(df[col], errors="coerce")

# #     if "Nation" in df.columns:
# #         df["Nation"] = df["Nation"].astype(str).str.strip()

# #     if "PlayerID" in df.columns:
# #         df["PlayerID"] = df["PlayerID"].astype(str).str.strip()

# #     return df


# def get_player_latest_season(df: pd.DataFrame, player_id: str):
#     player_df = df[df["PlayerID"] == player_id].copy()

#     if player_df.empty:
#         return None

#     return player_df.sort_values("Season", ascending=False).iloc[0]


# def aggregate_season_stats(df: pd.DataFrame, player_id: str) -> pd.DataFrame:
#     player_df = df[df["PlayerID"] == player_id].copy()

#     if player_df.empty:
#         return player_df

#     sum_cols = [
#         "MP", "Starts", "MinutesPlayed", "Goals", "Assists",
#         "GoalContributions", "NonPenaltyGoals",
#         "PenaltiesScored", "PenaltiesAttempted",
#         "YellowCards", "RedCards",
#         "PlayingTime_90s",
#         "Shots", "ShotsOnTarget",
#         "FoulsCommitted", "FoulsDrawn", "Offsides",
#         "Crosses", "Interceptions", "TacklesWon",
#         "PenaltiesWon", "PenaltiesConceded", "OwnGoals"
#     ]

#     mean_cols = [
#         "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
#         "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90",
#         "ShotsPer90", "ShotsOnTargetPer90",
#         "GoalsPerShot", "GoalsPerShotOnTarget"
#     ]

#     meta_cols = [
#         "Player", "Nation", "ClubName",
#         "League", "PlayerID", "Age"
#     ]

#     agg_dict = {c: "sum" for c in sum_cols if c in player_df.columns}
#     agg_dict.update({c: "mean" for c in mean_cols if c in player_df.columns})

#     for c in meta_cols:
#         if c in player_df.columns:
#             agg_dict[c] = "last"

#     grouped = (
#         player_df
#         .groupby("Season", as_index=False)
#         .agg(agg_dict)
#         .sort_values("Season")
#         .reset_index(drop=True)
#     )

#     return grouped

import pandas as pd
import streamlit as st
import os


DATA_FILE = "PlayerStatistics.xlsx"


NUMERIC_COLS = [
    "Age", "MP", "Starts", "MinutesPlayed", "Playing Time_90s",
    "Goals", "Assists", "GoalContributions", "NonPenaltyGoals",
    "PenaltiesScored", "PenaltiesAttempted", "YellowCards", "RedCards",
    "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
    "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90",

     
    "Shots", "ShotsOnTarget", "ShotsOnTargetPct", "ShotsPer90", "ShotsOnTargetPer90",
    "GoalsPerShot", "GoalsPerShotOnTarget",
    "FoulsCommitted", "FoulsDrawn", "Offsides", "Crosses", "Interceptions",
    "TacklesWon", "PenaltiesWon", "PenaltiesConceded", "OwnGoals",
    "SecondYellowRedCards", "MiscYellowCards", "MiscRedCards"
]

@st.cache_data
def load_data(filepath: str = DATA_FILE) -> pd.DataFrame:
    if not os.path.exists(filepath):
        return pd.DataFrame()

    df = pd.read_excel(filepath)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Nation" in df.columns:
        df["Nation"] = df["Nation"].astype(str).str.strip()
    if "PlayerID" in df.columns:
        df["PlayerID"] = df["PlayerID"].astype(str).str.strip()

    return df
 
def get_player_latest_season(df: pd.DataFrame, player_id: str):
    player_df = df[df["PlayerID"] == player_id].copy()
    if player_df.empty:
        return None
    return player_df.sort_values("Season", ascending=False).iloc[0]


def aggregate_season_stats(df: pd.DataFrame, player_id: str) -> pd.DataFrame:
    player_df = df[df["PlayerID"] == player_id].copy()
    if player_df.empty:
        return player_df

    sum_cols = [
        "MP", "Starts", "MinutesPlayed", "Goals", "Assists", "GoalContributions",
        "NonPenaltyGoals", "PenaltiesScored", "PenaltiesAttempted", "YellowCards",
        "RedCards", "Playing Time_90s", "Shots", "ShotsOnTarget", "FoulsCommitted",
        "FoulsDrawn", "Offsides", "Crosses", "Interceptions", "TacklesWon",
        "PenaltiesWon", "PenaltiesConceded", "OwnGoals"
    ]
    mean_cols = [
        "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
        "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90",
        "ShotsPer90", "ShotsOnTargetPer90", "GoalsPerShot", "GoalsPerShotOnTarget"
    ]
    meta_cols = ["Player", "Nation", "ClubName", "League", "PlayerID", "Age"]

    agg_dict = {c: "sum" for c in sum_cols if c in player_df.columns}
    agg_dict.update({c: "mean" for c in mean_cols if c in player_df.columns})
    for c in meta_cols:
        if c in player_df.columns:
            agg_dict[c] = "last"

    grouped = player_df.groupby("Season", as_index=False).agg(agg_dict)
    return grouped.sort_values("Season", ascending=True).reset_index(drop=True)