import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_data
from utils.filters import render_sidebar_filters, init_filter_state
from utils.plots import (
    top_n_bar, distribution_hist, club_aggregated_bar,
    cards_stacked_bar, league_scatter,
)

st.set_page_config(page_title="League & Club Stats", page_icon="🏆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.section-header {
    font-size: 17px; font-weight: 600; color: #FAFAFA;
    border-bottom: 2px solid #FF6B35; padding-bottom: 6px;
    margin: 28px 0 14px 0;
}
div[data-testid="stSidebar"] { background: #141B24; }
</style>
""", unsafe_allow_html=True)

df = load_data()
if df.empty:
    st.error("Data not found.")
    st.stop()

init_filter_state()
render_sidebar_filters(df, show_player=False)

st.markdown("## 🏆 League & Club Statistics")

#On-page filters 
fc1, fc2, fc3 = st.columns(3)
with fc1:
    leagues  = ["All"] + sorted(df["League"].dropna().unique().tolist())
    sel_lg   = st.selectbox("League", leagues, key="ls_league")
with fc2:
    seasons  = ["All"] + sorted(df["Season"].dropna().unique().tolist(), reverse=True)
    sel_sea  = st.selectbox("Season", seasons, key="ls_season")
with fc3:
    comps    = ["All"] + sorted(df["Comp"].dropna().unique().tolist())
    sel_comp = st.selectbox("Competition", comps, key="ls_comp")

fdf = df.copy()
if sel_lg   != "All": fdf = fdf[fdf["League"]==sel_lg]
if sel_sea  != "All": fdf = fdf[fdf["Season"]==sel_sea]
if sel_comp != "All": fdf = fdf[fdf["Comp"]==sel_comp]

clubs_list   = ["All"] + sorted(fdf["ClubName"].dropna().unique().tolist())
sel_club     = st.selectbox("Filter by Club", clubs_list, key="ls_club")
if sel_club != "All": fdf = fdf[fdf["ClubName"]==sel_club]

if fdf.empty:
    st.warning("No data for selected filters.")
    st.stop()

# Aggregate per player 
AGG_SUM  = ["MP","Starts","MinutesPlayed","Goals","Assists","GoalContributions",
            "NonPenaltyGoals","PenaltiesScored","YellowCards","RedCards","Playing Time_90s"]
AGG_MEAN = ["GoalsPer90","AssistsPer90"]
agg_cols = {c:"sum" for c in AGG_SUM if c in fdf.columns}
agg_cols.update({c:"mean" for c in AGG_MEAN if c in fdf.columns})
for mc in ["Player","ClubName","Nation"]:
    if mc in fdf.columns: agg_cols[mc] = "last"

agg = fdf.groupby("PlayerID", as_index=False).agg(agg_cols)

#Overview metrics 
st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Players",        f'{agg["PlayerID"].nunique():,}')
m2.metric("Clubs",          f'{fdf["ClubName"].nunique():,}')
m3.metric("Total Goals",    f'{int(agg["Goals"].sum()):,}')
m4.metric("Total Assists",  f'{int(agg["Assists"].sum()):,}')
m5.metric("Total Minutes",  f'{int(agg["MinutesPlayed"].sum()):,}')

n_top = st.slider("Top N players", 5, 30, 15, 5)

#Top scorers & assisters side by side
st.markdown('<div class="section-header">🥇 Top Performers</div>', unsafe_allow_html=True)

tc1, tc2 = st.columns(2)
with tc1:
    st.plotly_chart(top_n_bar(agg, "Goals", n=n_top, title=f"Top {n_top} Scorers"),
                    use_container_width=True)
with tc2:
    st.plotly_chart(top_n_bar(agg, "Assists", n=n_top, title=f"Top {n_top} Assisters"),
                    use_container_width=True)

tc3, tc4 = st.columns(2)
with tc3:
    st.plotly_chart(top_n_bar(agg, "GoalContributions", n=n_top,
                               title=f"Top {n_top} Goals + Assists"),
                    use_container_width=True)
with tc4:
    st.plotly_chart(top_n_bar(agg, "MinutesPlayed", n=n_top,
                               title=f"Top {n_top} Minutes Played"),
                    use_container_width=True)

#Discipline 
st.markdown('<div class="section-header">🟨 Discipline</div>', unsafe_allow_html=True)
st.plotly_chart(cards_stacked_bar(agg, n=n_top), use_container_width=True)

#Scatter
st.markdown('<div class="section-header">🔵 Scatter Explorer</div>', unsafe_allow_html=True)
st.markdown(
    '<span style="font-size:12px;color:#8899AA">'
    'Dot colour = club. Top performers are labelled automatically.'
    '</span>',
    unsafe_allow_html=True,
)

SCATTER_METRICS = [c for c in ["Goals","Assists","GoalContributions","MinutesPlayed",
                                 "MP","Starts","YellowCards","RedCards",
                                 "GoalsPer90","AssistsPer90","NonPenaltyGoals",
                                 "PenaltiesScored"] if c in agg.columns]

PRESETS = {
    "Goals vs Assists":           ("Goals","Assists"),
    "Goals vs Minutes Played":    ("MinutesPlayed","Goals"),
    "Goals vs Matches Played":    ("MP","Goals"),
    "Goals/90 vs Assists/90":     ("GoalsPer90","AssistsPer90"),
    "Assists vs Minutes Played":  ("MinutesPlayed","Assists"),
    "G+A vs Minutes Played":      ("MinutesPlayed","GoalContributions"),
}
valid_presets = {k:v for k,v in PRESETS.items()
                 if v[0] in agg.columns and v[1] in agg.columns}

sc_l, sc_r = st.columns([2, 1])
with sc_l:
    sc_mode = st.radio("Axis mode", ["Preset","Custom"], horizontal=True, key="ls_sc_mode")
with sc_r:
    label_pct = st.slider("Label top %", 5, 50, 15, 5, key="ls_sc_lbl",
                           help="Label players above this percentile in the Y axis")

if sc_mode == "Preset":
    sc_preset = st.selectbox("Preset", list(valid_presets.keys()), key="ls_sc_preset")
    sx, sy = valid_presets[sc_preset]
else:
    cc1, cc2 = st.columns(2)
    with cc1:
        sx = st.selectbox("X axis", SCATTER_METRICS,
                           index=SCATTER_METRICS.index("MinutesPlayed")
                           if "MinutesPlayed" in SCATTER_METRICS else 0, key="ls_sx")
    with cc2:
        sy = st.selectbox("Y axis", SCATTER_METRICS,
                           index=SCATTER_METRICS.index("Goals")
                           if "Goals" in SCATTER_METRICS else 0, key="ls_sy")

st.plotly_chart(
    league_scatter(agg, sx, sy, label_threshold=(100-label_pct)/100),
    use_container_width=True,
)

# Club totals
st.markdown('<div class="section-header">🏟️ Club Totals</div>', unsafe_allow_html=True)

club_agg_cols = {c:"sum" for c in ["Goals","Assists","GoalContributions",
                                    "YellowCards","RedCards","MinutesPlayed"]
                 if c in fdf.columns}
club_agg = fdf.groupby("ClubName", as_index=False).agg(club_agg_cols)

club_m = st.selectbox(
    "Metric",
    [c for c in ["Goals","Assists","GoalContributions","YellowCards","MinutesPlayed"]
     if c in club_agg.columns],
    key="club_m",
)
st.plotly_chart(club_aggregated_bar(club_agg, club_m), use_container_width=True)

# Distribution
st.markdown('<div class="section-header">📊 Distribution</div>', unsafe_allow_html=True)

dist_m = st.selectbox(
    "Metric",
    [c for c in ["Goals","Assists","MinutesPlayed","MP","GoalsPer90","AssistsPer90",
                  "YellowCards","RedCards"] if c in agg.columns],
    key="dist_m",
)
st.plotly_chart(distribution_hist(agg, dist_m), use_container_width=True)

#Full table
st.markdown('<div class="section-header">📋 Player Table</div>', unsafe_allow_html=True)

show = [c for c in ["Player","ClubName","Nation","MP","Starts","MinutesPlayed",
                      "Goals","Assists","GoalContributions","YellowCards","RedCards",
                      "GoalsPer90","AssistsPer90"] if c in agg.columns]
st.dataframe(
    agg[show].sort_values("Goals", ascending=False).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)