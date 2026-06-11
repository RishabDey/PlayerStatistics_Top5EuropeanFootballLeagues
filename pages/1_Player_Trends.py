import streamlit as st
import sys, os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_data, aggregate_season_stats
from utils.filters import render_sidebar_filters, init_filter_state, get_player_filtered_data
from utils.plots import (
    line_chart_season_stat, bar_chart_season_stat,bar_chart_season_stat1,
    scatter_player_season, radar_chart,
    scatter_player_by_competition,
    squad_career_bar, squad_metric_cards_data,
)

st.set_page_config(page_title="Player Trends", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.section-header {
    font-size: 17px; font-weight: 600; color: #FAFAFA;
    border-bottom: 2px solid #1DB954; padding-bottom: 6px;
    margin: 28px 0 14px 0; letter-spacing: 0.3px;
}
.chart-note { font-size: 12px; color: #8899AA; margin-bottom: 8px; }
.squad-pill {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 600; margin: 3px 4px;
    border: 1px solid #2A3240; background: rgba(29,185,84,0.12); color: #1DB954;
}
div[data-testid="stSidebar"] { background: #141B24; }
</style>
""", unsafe_allow_html=True)

df = load_data()
if df.empty:
    st.error("Data not found.")
    st.stop()

init_filter_state()
# Sidebar filters - Bruno Fernandes + All seasons
ctx = render_sidebar_filters(df, default_player="Bruno Fernandes", seasons_default="all")
player_id   = ctx["sel_player_id"]
player_name = ctx["sel_player_name"]
sel_seasons = ctx["sel_seasons"]
sel_comp    = ctx["sel_comp"]

st.markdown(f"## 📈 Player Trends — {player_name or '—'}")

if not player_id:
    st.info("Select a player from the sidebar.")
    st.stop()

raw_df = get_player_filtered_data(df, player_id, sel_seasons, sel_comp)

if raw_df.empty:
    st.warning("No data for the selected filters.")
    st.stop()
SUM_COLS = [
    "MP", "Starts", "MinutesPlayed", "Goals", "Assists", "GoalContributions",
    "NonPenaltyGoals", "PenaltiesScored", "PenaltiesAttempted",
    "YellowCards", "RedCards", "PlayingTime_90s",
    "Shots", "ShotsOnTarget", "FoulsCommitted", "FoulsDrawn",
    "Interceptions", "TacklesWon",
]
MEAN_COLS = [
    "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
    "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90",
    "ShotsPer90", "ShotsOnTargetPer90", "GoalsPerShot", "GoalsPerShotOnTarget",
]
META_COLS = ["Player", "Nation", "ClubName", "PlayerID"]

agg_dict = {c: "sum"  for c in SUM_COLS  if c in raw_df.columns}
agg_dict.update({c: "mean" for c in MEAN_COLS if c in raw_df.columns})
for c in META_COLS:
    if c in raw_df.columns:
        agg_dict[c] = "last"

agg_df = (
    raw_df
    .groupby("Season", as_index=False)
    .agg(agg_dict)
    .sort_values("Season")
    .reset_index(drop=True)
)

# Chart type toggle 
chart_type = st.radio("Chart style", ["Line", "Bar"], horizontal=True)

def make_chart(decimals=0):
    if chart_type == "Line":
        return lambda d, cols, title: line_chart_season_stat(d, cols, title, decimals)
    else:
        return lambda d, cols, title: bar_chart_season_stat(d, cols, title, decimals)

#Goals & Assists
st.markdown('<div class="section-header">🎯 Goals & Assists</div>', unsafe_allow_html=True)

g_opts = st.multiselect(
    "Stats to show",
    [c for c in ["Goals", "Assists", "GoalContributions", "NonPenaltyGoals", "PenaltiesScored"]
     if c in agg_df.columns],
    default=[c for c in ["Goals", "Assists"] if c in agg_df.columns],
    key="g_multi",
)
if g_opts:
    st.plotly_chart(make_chart()(agg_df, g_opts, "Goals & Assists by Season"),
                    use_container_width=True)

# Playing Time
st.markdown('<div class="section-header">⏱️ Playing Time</div>', unsafe_allow_html=True)
pt_opts = st.multiselect(
    "Stats to show",
    [c for c in ["MP", "Starts", "MinutesPlayed", "PlayingTime_90s"] if c in agg_df.columns],
    default=[c for c in ["MP", "Starts"] if c in agg_df.columns],
    key="pt_multi",
)
if pt_opts:
    st.plotly_chart(make_chart()(agg_df, pt_opts, "Playing Time by Season"),
                    use_container_width=True)

# Per-90 Rates
st.markdown('<div class="section-header">📊 Per-90 Rates</div>', unsafe_allow_html=True)

rate_opts = st.multiselect(
    "Stats to show",
    [c for c in ["GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
                  "NonPenaltyGoalsPer90", "NonPenaltyGoalContributionsPer90"]
     if c in agg_df.columns],
    default=[c for c in ["GoalsPer90", "AssistsPer90"] if c in agg_df.columns],
    key="rate_multi",
)
if rate_opts:
    st.plotly_chart(make_chart(2)(agg_df, rate_opts, "Per-90 Rates by Season"),
                    use_container_width=True)

#Shooting
shoot_cols = [c for c in ["Shots", "ShotsOnTarget", "GoalsPerShot"] if c in agg_df.columns]
if shoot_cols:
    st.markdown('<div class="section-header">🎯 Shooting</div>', unsafe_allow_html=True)
    shoot_opts = st.multiselect("Stats to show", shoot_cols, default=shoot_cols[:2],
                                 key="shoot_multi")
    if shoot_opts:
        st.plotly_chart(make_chart()(agg_df, shoot_opts, "Shooting by Season"),
                        use_container_width=True)

#Defensive
def_cols = [c for c in ["TacklesWon", "Interceptions", "FoulsCommitted", "FoulsDrawn"]
            if c in agg_df.columns]
if def_cols:
    st.markdown('<div class="section-header">🛡️ Defensive</div>', unsafe_allow_html=True)
    def_opts = st.multiselect("Stats to show", def_cols, default=def_cols[:2],
                               key="def_multi")
    if def_opts:
        st.plotly_chart(make_chart()(agg_df, def_opts, "Defensive Stats by Season"),
                        use_container_width=True)

#Discipline
st.markdown('<div class="section-header">🟨 Discipline</div>', unsafe_allow_html=True)
disc_cols = [c for c in ["YellowCards", "RedCards"] if c in agg_df.columns]
if disc_cols:
    st.plotly_chart(
        bar_chart_season_stat1(agg_df, disc_cols, "Cards by Season"),
        use_container_width=True,
    )

#Season Scatter (aggregated)
st.markdown('<div class="section-header">🔵 Season Scatter (Aggregated)</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="chart-note">'
    'Each dot = one season (all selected competitions summed). '
    'Dot size = minutes played.'
    '</div>',
    unsafe_allow_html=True,
)

_numeric_candidates = [c for c in [
    "Goals", "Assists", "GoalContributions", "NonPenaltyGoals",
    "MP", "Starts", "MinutesPlayed", "PlayingTime_90s",
    "YellowCards", "RedCards", "Shots", "TacklesWon", "Interceptions",
    "GoalsPer90", "AssistsPer90", "GoalContributionsPer90",
] if c in agg_df.columns]

PRESETS = {k: v for k, v in {
    "Goals vs Assists":          ("Goals",         "Assists"),
    "Goals vs Minutes Played":   ("MinutesPlayed", "Goals"),
    "Goals vs Matches Played":   ("MP",            "Goals"),
    "G+A vs Minutes Played":     ("MinutesPlayed", "GoalContributions"),
    "Assists vs Minutes Played": ("MinutesPlayed", "Assists"),
    "Goals/90 vs Assists/90":    ("GoalsPer90",    "AssistsPer90"),
}.items() if v[0] in agg_df.columns and v[1] in agg_df.columns}

c1, c2, c3 = st.columns([2, 1.2, 1.2])
with c1:
    sc_mode = st.radio("Axis selection", ["Preset", "Custom"], horizontal=True, key="sc_mode")
with c2:
    if sc_mode == "Preset":
        preset = st.selectbox("Preset", list(PRESETS.keys()), key="sc_preset")
        x_col, y_col = PRESETS[preset]
    else:
        x_col = st.selectbox("X axis", _numeric_candidates,
                             index=_numeric_candidates.index("MinutesPlayed")
                             if "MinutesPlayed" in _numeric_candidates else 0,
                             key="sc_x")
with c3:
    if sc_mode == "Custom":
        y_col = st.selectbox("Y axis", _numeric_candidates,
                             index=_numeric_candidates.index("Goals")
                             if "Goals" in _numeric_candidates else 0,
                             key="sc_y")
    else:
        st.markdown(f"**X:** {x_col}  \n**Y:** {y_col}")

if x_col in agg_df.columns and y_col in agg_df.columns:
    st.plotly_chart(scatter_player_season(agg_df, x_col, y_col),
                    use_container_width=True)
else:
    st.info("Not enough data for the selected axes.")

#Season Scatter Per Competition
st.markdown('<div class="section-header">🔵 Season Scatter : by Competition</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="chart-note">'
    'Each dot = one individual season , '
    'Color = competition.'
    '</div>',
    unsafe_allow_html=True,
)

_raw_numeric = [c for c in _numeric_candidates if c in raw_df.columns]
PRESETS_RAW  = {k: v for k, v in PRESETS.items()
                if v[0] in raw_df.columns and v[1] in raw_df.columns}

rc1, rc2, rc3 = st.columns([2, 1.2, 1.2])
with rc1:
    raw_mode = st.radio("Axis selection", ["Preset", "Custom"],
                        horizontal=True, key="rsc_mode")
with rc2:
    if raw_mode == "Preset":
        raw_preset = st.selectbox("Preset", list(PRESETS_RAW.keys()), key="rsc_preset")
        rx_col, ry_col = PRESETS_RAW[raw_preset]
    else:
        rx_col = st.selectbox("X axis", _raw_numeric,
                              index=_raw_numeric.index("MinutesPlayed")
                              if "MinutesPlayed" in _raw_numeric else 0,
                              key="rsc_x")
with rc3:
    if raw_mode == "Custom":
        ry_col = st.selectbox("Y axis", _raw_numeric,
                              index=_raw_numeric.index("Goals")
                              if "Goals" in _raw_numeric else 0,
                              key="rsc_y")
    else:
        st.markdown(f"**X:** {rx_col}  \n**Y:** {ry_col}")

if rx_col in raw_df.columns and ry_col in raw_df.columns:
    st.plotly_chart(
        scatter_player_by_competition(raw_df, rx_col, ry_col, player_name),
        use_container_width=True,
    )
else:
    st.info("Not enough data for the selected axes.")

#Club / Squad Breakdown  
squad_col    = "Squad" if "Squad" in raw_df.columns else "ClubName"
clubs_played = raw_df[squad_col].dropna().unique().tolist()

if clubs_played:
    st.markdown('<div class="section-header">👕 Club Breakdown</div>',
                unsafe_allow_html=True)

    if len(clubs_played) > 1:
        pills = "".join(f'<span class="squad-pill">{c}</span>' for c in sorted(clubs_played))
        st.markdown(f'<div class="chart-note">Clubs represented: {pills}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chart-note">Club: <b>{clubs_played[0]}</b></div>',
                    unsafe_allow_html=True)

    squad_metric = st.selectbox(
        "Metric for club breakdown",
        [c for c in ["Goals", "Assists", "GoalContributions", "MinutesPlayed",
                      "MP", "YellowCards", "RedCards", "Shots",
                      "TacklesWon", "Interceptions"] if c in raw_df.columns],
        key="squad_metric",
    )
    st.plotly_chart(
        squad_career_bar(raw_df, squad_metric, player_name),
        use_container_width=True,
    )

    summary_metrics = [c for c in ["Goals", "Assists", "GoalContributions",
                                    "MinutesPlayed", "MP", "YellowCards",
                                    "RedCards", "Shots"] if c in raw_df.columns]
    summary = squad_metric_cards_data(raw_df, summary_metrics)
    if not summary.empty:
        st.markdown('<div class="chart-note">Per-club career totals (within selected filters):</div>',
                    unsafe_allow_html=True)
        sort_by = "Goals" if "Goals" in summary.columns else summary.columns[1]
        st.dataframe(
            summary.sort_values(sort_by, ascending=False),
            use_container_width=True,
            hide_index=True,
        )