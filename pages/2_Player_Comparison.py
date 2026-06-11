import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_data
from utils.filters import render_sidebar_filters, init_filter_state
from utils.plots import comparison_bar, comparison_scatter, comparison_radar

st.set_page_config(page_title="Player Comparison", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.section-header {
    font-size: 17px; font-weight: 600; color: #FAFAFA;
    border-bottom: 2px solid #1DB954; padding-bottom: 6px;
    margin: 28px 0 14px 0;
}
.player-header {
    border-radius: 14px; padding: 18px 22px; text-align: center;
    background: linear-gradient(145deg, #1E2530, #141B24);
    border-top: 4px solid var(--pc);
    margin-bottom: 4px;
}
.player-header h3 { margin: 0 0 4px 0; font-size: 17px; color: #FAFAFA; }
.player-header p  { margin: 0; font-size: 12px; color: #8899AA; }
.stat-block {
    background: #1E2530; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
}
.stat-block .lbl { font-size: 16px; color: #FFFFFF; }
.stat-block .val { font-size: 19px; font-weight: 700; color: #FAFAFA; }
.grp-label {
    font-size: 18px; font-weight: 700; color: #FFFFFF;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin: 18px 0 8px 0;
}
table.cmp { width:100%; border-collapse:collapse; }
table.cmp th {
    background:#1E2530; color:#8899AA; font-size:11px;
    text-transform:uppercase; letter-spacing:1px;
    padding:10px 14px; text-align:left;
}
table.cmp td { padding:9px 14px; border-bottom:1px solid #2A3240;
    font-size:14px; color:#FAFAFA; }
table.cmp tr:hover td { background:#1A2230; }
table.cmp td.best { color:#1DB954; font-weight:700; }
table.cmp .grp-row td {
    background:#141B24; color:#8899AA; font-size:11px;
    text-transform:uppercase; letter-spacing:1px; padding:8px 14px;
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

st.markdown("## ⚖️ Player Comparison")

#Player selectors
player_map = (
    df.drop_duplicates("PlayerID")
    .set_index("PlayerID")["Player"].to_dict()
)
all_ids   = sorted(player_map, key=lambda p: player_map[p])
all_names = [player_map[p] for p in all_ids]

default_pid = st.session_state.get("sel_player_id")
d_idx = all_ids.index(default_pid) if default_pid in all_ids else 0

c1, c2, c3 = st.columns(3)
with c1:
    p1_name = st.selectbox("Player 1", all_names, index=d_idx, key="cmp_p1")
    p1_id   = all_ids[all_names.index(p1_name)]
with c2:
    p2_name = st.selectbox("Player 2", all_names,
                            index=min(d_idx+1, len(all_names)-1), key="cmp_p2")
    p2_id   = all_ids[all_names.index(p2_name)]
with c3:
    add3  = st.checkbox("Add 3rd player", value=False)
    p3_id = None
    if add3:
        p3_name = st.selectbox("Player 3", all_names,
                                index=min(d_idx+2, len(all_names)-1), key="cmp_p3")
        p3_id   = all_ids[all_names.index(p3_name)]

def get_seasons(pid):
    return sorted(df[df["PlayerID"]==pid]["Season"].dropna().unique().tolist(), reverse=True)

with st.expander("📅 Season selection (defaults: all seasons)"):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        p1_s = st.multiselect(p1_name, get_seasons(p1_id), default=get_seasons(p1_id), key="cs1")
    with sc2:
        p2_s = st.multiselect(p2_name, get_seasons(p2_id), default=get_seasons(p2_id), key="cs2")
    with sc3:
        p3_s = st.multiselect(p3_name if p3_id else "—",
                              get_seasons(p3_id) if p3_id else [],
                              default=get_seasons(p3_id) if p3_id else [],
                              key="cs3") if p3_id else []


EXTRA_COLS = ["Shots", "TacklesWon", "Interceptions", "FoulsCommitted", "GoalContributions"]

SUM_COLS  = ["MP","Starts","MinutesPlayed","Goals","Assists","GoalContributions",
             "NonPenaltyGoals","PenaltiesScored","PenaltiesAttempted",
             "YellowCards","RedCards"] + EXTRA_COLS

MEAN_COLS = ["GoalsPer90","AssistsPer90","GoalContributionsPer90",
             "NonPenaltyGoalsPer90","NonPenaltyGoalContributionsPer90"]
INT_COLS  = {"MP","Starts","MinutesPlayed","Goals","Assists","GoalContributions",
             "NonPenaltyGoals","PenaltiesScored","PenaltiesAttempted",
             "YellowCards","RedCards"}
ALL_METRICS = SUM_COLS + MEAN_COLS
def build_row(pid, name, seasons):
    sub = df[df["PlayerID"]==pid]
    if seasons: 
        sub = sub[sub["Season"].isin(seasons)]
    
    row = {"Player": name, "PlayerID": pid}
    
    for c in SUM_COLS:
        if c in sub.columns:
            row[c] = pd.to_numeric(sub[c], errors="coerce").sum()
    
    for c in MEAN_COLS:
        if c in sub.columns:
            row[c] = pd.to_numeric(sub[c], errors="coerce").mean()
    
    return row

def fmt(col, val):
    if pd.isna(val): return "0"
    return str(int(round(val))) if col in INT_COLS else f"{val:.2f}"

def build_row(pid, name, seasons):
    sub = df[df["PlayerID"]==pid]
    if seasons: sub = sub[sub["Season"].isin(seasons)]
    row = {"Player": name, "PlayerID": pid}
    for c in SUM_COLS:
        if c in sub.columns:
            row[c] = pd.to_numeric(sub[c], errors="coerce").sum()
    for c in MEAN_COLS:
        if c in sub.columns:
            row[c] = pd.to_numeric(sub[c], errors="coerce").mean()
    return row

players = [build_row(p1_id, p1_name, p1_s), build_row(p2_id, p2_name, p2_s)]
if p3_id:
    players.append(build_row(p3_id, p3_name, p3_s))

COLORS = ["#1DB954", "#FF6B35", "#4ECDC4"]
n_p = len(players)

#Head-to-head cards
st.markdown('<div class="section-header">📊 Head-to-Head</div>', unsafe_allow_html=True)

GROUPS = {
    "⚽ Attack":      ["Goals","Assists","GoalContributions","NonPenaltyGoals",
                       "PenaltiesScored","PenaltiesAttempted"],
    "📈 Per 90":      ["GoalsPer90","AssistsPer90","GoalContributionsPer90",
                       "NonPenaltyGoalsPer90","NonPenaltyGoalContributionsPer90"],
    "⏱️ Playing Time":["MP","Starts"],
    "🟨 Discipline":  ["YellowCards","RedCards"],
}

# Player header cards
hdr_cols = st.columns(n_p)
for i, (col, p) in enumerate(zip(hdr_cols, players)):
    latest = df[df["PlayerID"]==p["PlayerID"]].sort_values("Season",ascending=False).iloc[0]
    col.markdown(
        f'<div class="player-header" style="--pc:{COLORS[i]}">'
        f'<h3>{p["Player"]}</h3>'
        f'<p>🌍 {latest.get("Nation","—")} &nbsp;|&nbsp; 🏟️ {latest.get("ClubName","—")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

# Stat rows per group
for grp_label, stats in GROUPS.items():
    valid = [s for s in stats if s in players[0]]
    if not valid: continue
    st.markdown(f'<div class="grp-label">{grp_label}</div>', unsafe_allow_html=True)
    for stat in valid:
        vals = [p.get(stat, 0) or 0 for p in players]
        max_v = max(vals)
        row_cols = st.columns(n_p)
        for i, (col, p) in enumerate(zip(row_cols, players)):
            v = p.get(stat, 0) or 0
            color = COLORS[i] if (v == max_v and max_v > 0) else "#FAFAFA"
            col.markdown(
                f'<div class="stat-block">'
                f'<span class="lbl">{stat}</span>'
                f'<span class="val" style="color:{color}">{fmt(stat,v)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

#Bar chart
st.markdown('<div class="section-header">📊 Bar Comparison</div>', unsafe_allow_html=True)

avail = [m for m in ALL_METRICS if m in players[0]]
bar_metric = st.selectbox("Metric", avail,
                           index=avail.index("Goals") if "Goals" in avail else 0,
                           key="bar_m")
st.plotly_chart(comparison_bar(players, bar_metric, fmt), use_container_width=True)

#Scatter
st.markdown('<div class="section-header">🔵 Scatter Comparison</div>', unsafe_allow_html=True)

sc1, sc2 = st.columns(2)
with sc1:
    x_m = st.selectbox("X axis", avail,
                        index=avail.index("Goals") if "Goals" in avail else 0, key="sc_x")
with sc2:
    y_m = st.selectbox("Y axis", avail,
                        index=avail.index("Assists") if "Assists" in avail else 1, key="sc_y")
st.plotly_chart(comparison_scatter(players, x_m, y_m, fmt), use_container_width=True)
 
#Radar Comparison
st.markdown('<div class="section-header">🕸️ Radar Comparison</div>', unsafe_allow_html=True)

radar_default = ["Goals", "Assists", "Shots", "TacklesWon", "Interceptions", "FoulsCommitted"]
radar_avail = [c for c in radar_default if c in players[0]]

if len(radar_avail) >= 3:
    # Collect raw values
    raw_data = []
    for p in players:
        d = {"Player": p["Player"]}
        for c in radar_avail:
            val = p.get(c, 0) or 0
            d[c] = pd.to_numeric(val, errors='coerce') 
        raw_data.append(d)

    #normalization
    def norm_relative(col, player_val, all_vals):
        mx = max(all_vals) if max(all_vals) > 0 else 1
        return round((player_val / mx) * 10, 2)

    radar_players = []
    for p in raw_data:
        norm_dict = {"Player": p["Player"]}
        for c in radar_avail:
            all_vals = [pd.get(c, 0) for pd in raw_data]
            norm_dict[c] = norm_relative(c, p[c], all_vals)
        radar_players.append(norm_dict)

    st.plotly_chart(comparison_radar(radar_players, radar_avail), use_container_width=True)
else:
    st.warning(f"Only {len(radar_avail)} stats available: {radar_avail}")


