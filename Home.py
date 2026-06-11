import streamlit as st
import pandas as pd
import sys, os
from utils.metric_cards import metric_card
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_data, get_player_latest_season
from utils.filters import render_sidebar_filters, get_player_filtered_data, init_filter_state
from utils.plots import radar_chart

def load_css():
    with open("styles.css") as f:
        return f"<style>{f.read()}</style>"
st.markdown(load_css(), unsafe_allow_html=True)

INT_STATS = {"MP", "Starts", "MinutesPlayed", "Goals", "Assists", "GoalContributions",
             "NonPenaltyGoals", "PenaltiesScored", "PenaltiesAttempted", "YellowCards",
             "RedCards", "Shots", "ShotsOnTarget", "FoulsCommitted", "FoulsDrawn",
             "Offsides", "Crosses", "Interceptions", "TacklesWon"}

def fmt(col, val):
    if pd.isna(val): return "0"
    if col in INT_STATS: return str(int(round(val)))
    return f"{float(val):.2f}"

st.set_page_config(
    page_title="Player Satistics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

#Load data
df = load_data()

if df.empty:
    st.markdown("""
    <div class="no-data">
        <h2>⚽ Player Statistics Dashboard</h2>
        <p>Place your <code>all_players_stats.xlsx</code> file in the same folder as this app, then refresh.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

#Sidebar filters
init_filter_state()
# Sidebar filters - Bruno Fernandes + Latest season only
ctx = render_sidebar_filters(df, default_player="Bruno Fernandes", seasons_default="latest")
player_id = ctx["sel_player_id"]

#Main content
st.markdown("## Player Statistics (Top 5 Football Leagues)")

if not player_id:
    st.info("Select a player from the sidebar.")
    st.stop()

# Latest-season row for header info
latest = get_player_latest_season(df, player_id)
if latest is None:
    st.warning("No data found for this player.")
    st.stop()

# Filtered data
seasons = ctx["sel_seasons"]
comp = ctx["sel_comp"]
player_data = get_player_filtered_data(df, player_id, seasons, comp)

# Sum numeric across competitions for the selected seasons
def _safe_sum(col): 
    return pd.to_numeric(player_data[col], errors="coerce").sum() if col in player_data.columns else 0
def _safe_mean(col):
    return round(pd.to_numeric(player_data[col], errors="coerce").mean(), 2) if col in player_data.columns else 0


#Player header
name   = latest.get("Player", "Unknown")
nation = latest.get("Nation", "—")
club   = latest.get("ClubName", "—")
league = latest.get("League", "—")
age    = int(latest.get("Age", 0)) if pd.notna(latest.get("Age")) else "—"
season_label = ", ".join(seasons) if seasons else "All seasons"

st.markdown(f"""
<div class="player-header">
    <p class="player-name">{name}</p>
    <div class="player-meta">
        <span>🌍 {nation}</span>
        <span>👕 {club}</span>
        <span>🏆 {league}</span>
        <span>🎂 Age {age}</span>
        <span>📅 {season_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)

#Playing time
st.markdown('<div class="section-header">⏱️ Playing Time</div>', unsafe_allow_html=True)

c1, c2, c3, c5 = st.columns(4)

with c1:
    metric_card("Matches Played", int(_safe_sum("MP")))

with c2:
    metric_card("Starts", int(_safe_sum("Starts")))

with c3:
    mins = int(_safe_sum("MinutesPlayed"))
    metric_card("Minutes Played", f"{mins:,}")

# with c4:
#     metric_card("90's Played", round(_safe_sum("Playing Time_90s"), 1))

with c5:
    mp = int(_safe_sum("MP"))
    starts = int(_safe_sum("Starts"))
    sub_apps = mp - starts
    sub_rate = round(sub_apps / mp * 100) if mp > 0 else 0

    metric_card(
        "As a Substitute",
        sub_apps,
        f"{sub_rate}% of apps"
    )

#Goal contributions
st.markdown('<div class="section-header">🎯 Goal Contributions</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5= st.columns(5)

with c1:
    metric_card("Goals", int(_safe_sum("Goals")))

with c2:
    metric_card("Assists", int(_safe_sum("Assists")))

with c3:
    metric_card("Goals + Assists", int(_safe_sum("GoalContributions")))

with c4:
    metric_card("Non-Penalty Goals", int(_safe_sum("NonPenaltyGoals")))

with c5:
    metric_card(
        "Penalties Scored",
        int(_safe_sum("PenaltiesScored")),
        f"of {int(_safe_sum('PenaltiesAttempted'))} attempted"
    )



#Per-90 rates 
st.markdown('<div class="section-header">📈 Per 90 Rates</div>', unsafe_allow_html=True)

c0, c1, c2, c3 = st.columns(4)
with c0:
    ninety = _safe_sum("Playing Time_90s")
    g90 = round(_safe_sum("Goals") / ninety, 2) if ninety > 0 else 0

    metric_card("Goals per 90", g90)
with c1:
    metric_card("Assists per 90", _safe_mean("AssistsPer90"))

with c2:
    metric_card("Goals + Assists / 90", _safe_mean("GoalContributionsPer90"))

with c3:
    metric_card("Non-Penalty Goals / 90", _safe_mean("NonPenaltyGoalsPer90"))

# with c4:
#     metric_card(
#         "Non-Penalty G+A / 90",
#         _safe_mean("NonPenaltyGoalContributionsPer90")
#     )

#Discipline
st.markdown('<div class="section-header">🟨 🟥 Discipline</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Yellow Cards", int(_safe_sum("YellowCards")), color="#FFE66D")

with c2:
    metric_card("Red Cards",int(_safe_sum("RedCards")),color="#E63946")

mp_val = int(_safe_sum("MP"))
cards = int(_safe_sum("YellowCards")) + int(_safe_sum("RedCards"))

with c3:
    metric_card("Total cards",f"{cards}")

with c4:
    rate = round(cards / mp_val * 100, 1) if mp_val > 0 else 0

    metric_card("Card Rate",f"{rate}%", "per match played")

#Shooting Stats
st.markdown('<div class="section-header">🎯 Shooting</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    metric_card("Total Shots", int(_safe_sum("Shots")))

with c2:
    metric_card("Shots on Target", int(_safe_sum("ShotsOnTarget")))

with c3:
    metric_card("Shots per 90", _safe_mean("ShotsPer90"))

with c4:
    metric_card("Shots on Targer %", f"{_safe_mean('ShotsOnTargetPct')}%")

with c5:
    metric_card("Goals per Shot", _safe_mean("GoalsPerShot"))

# Defense and interceptions
st.markdown('<div class="section-header">🛡️ Interceptions </div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Tackles Won", int(_safe_sum("TacklesWon")))

with c2:
    metric_card("Interceptions", int(_safe_sum("Interceptions")))

with c3:
    metric_card("Fouls Committed", int(_safe_sum("FoulsCommitted")))

with c4:
    metric_card("Fouls Drawn", int(_safe_sum("FoulsDrawn")))
#Radar chart
st.markdown('<div class="section-header">🕸️ Attribute Radar</div>', unsafe_allow_html=True)
radar_cats = ["Goals", "Assists", "Shots", "TacklesWon", "Interceptions", "FoulsCommitted"]
# all_max = {c: df[c].max() for c in radar_cats if c in df.columns}

# def normalise(col):
#     mx = all_max.get(col, 1)
#     return round(_safe_sum(col) / mx * 10, 2) if mx else 0
all_max = {c: df[c].max() for c in radar_cats if c in df.columns}

def normalise(col):
    mx = all_max.get(col, 1)
    if not mx:
        return 0

    score = (_safe_sum(col) / mx) * 10

    # Cap at 10
    return round(min(score, 10), 2)

radar_vals = [normalise(c) for c in radar_cats]
actual_vals = [_safe_sum(c) for c in radar_cats]

st.plotly_chart(
    radar_chart(
        radar_cats,
        radar_vals,
        actual_vals,
        name
    ),
    use_container_width=True
)

# Season breakdown table  
st.markdown('<div class="section-header">📋 Season Breakdown</div>', unsafe_allow_html=True)

show_cols = ["Season", "Comp", "ClubName", "MP", "Starts", "MinutesPlayed",
             "Goals", "Assists", "Shots", "TacklesWon", "Interceptions", "YellowCards"]
show_cols = [c for c in show_cols if c in player_data.columns]
st.dataframe(player_data[show_cols].sort_values(["Season", "Comp"]), use_container_width=True, hide_index=True)
