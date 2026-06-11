import pandas as pd
import streamlit as st


def init_filter_state():
    defaults = {
        "sel_league": "All",
        "sel_club": "All",
        "sel_player_id": None,
        "sel_player_name": "",
        "sel_seasons": [],
        "sel_comp": "All",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_sidebar_filters(
    df: pd.DataFrame, 
    show_player: bool = True, 
    default_player: str = "Bruno Fernandes", 
    seasons_default: str = "latest"
) -> dict:
    """
    Page-specific defaults for player and seasons.
    """
    init_filter_state()

    st.sidebar.title("⚽ Filters")

    # League
    leagues = ["All"] + sorted(df["League"].dropna().unique().tolist())
    sel_league = st.sidebar.selectbox(
        "🏆 League", leagues,
        index=leagues.index(st.session_state.get("sel_league", "All")) 
              if st.session_state.get("sel_league") in leagues else 0,
        key="sb_league",
    )
    st.session_state["sel_league"] = sel_league

    filtered = df.copy()
    if sel_league != "All":
        filtered = filtered[filtered["League"] == sel_league]

    # Club
    clubs = ["All"] + sorted(filtered["ClubName"].dropna().unique().tolist())
    sel_club = st.sidebar.selectbox(
        "👕 Club", clubs,
        index=clubs.index(st.session_state.get("sel_club", "All")) 
              if st.session_state.get("sel_club") in clubs else 0,
        key="sb_club",
    )
    st.session_state["sel_club"] = sel_club

    if sel_club != "All":
        filtered = filtered[filtered["ClubName"] == sel_club]

    sel_player_id = None
    sel_display = ""
    sel_seasons = []
    sel_comp = "All"

    if show_player:
        # Player Selection
        player_map = (
            filtered.drop_duplicates("PlayerID")
            .set_index("PlayerID")["Player"]
            .to_dict()
        )
        player_ids = sorted(player_map.keys(), key=lambda pid: player_map[pid])
        player_display = [player_map[pid] for pid in player_ids]

        current_name = st.session_state.get("sel_player_name", "")
        if not current_name or current_name not in player_display:
            matching = [name for name in player_display if default_player.lower() in name.lower()]
            if matching:
                st.session_state["sel_player_name"] = matching[0]
                for pid, name in player_map.items():
                    if name == matching[0]:
                        st.session_state["sel_player_id"] = pid
                        break

        sel_player_id = st.session_state.get("sel_player_id")
        sel_display = st.session_state.get("sel_player_name", "")

        if player_ids:
            sel_names = st.sidebar.multiselect(
                "👤 Player",
                options=player_display,
                default=[sel_display] if sel_display and sel_display in player_display else [],
                max_selections=1,
                key="sb_player_ms",
            )
            if sel_names:
                sel_display = sel_names[0]
                sel_player_id = player_ids[player_display.index(sel_display)]
            else:
                sel_display = ""
                sel_player_id = None

            st.session_state["sel_player_id"] = sel_player_id
            st.session_state["sel_player_name"] = sel_display

        if sel_player_id:
            player_seasons = sorted(
                df[df["PlayerID"] == sel_player_id]["Season"].dropna().unique().tolist(),
                reverse=True
            )

            current_seasons = st.session_state.get("sel_seasons", [])

            if seasons_default == "latest":
                target_seasons = [player_seasons[0]] if player_seasons else []
            else:  # "all"
                target_seasons = player_seasons[:]

            if current_seasons != target_seasons:
                st.session_state["sel_seasons"] = target_seasons

            sel_seasons = st.sidebar.multiselect(
                "📅 Season(s)",
                player_seasons,
                default=st.session_state["sel_seasons"],
                key="sb_seasons",
            )
            st.session_state["sel_seasons"] = sel_seasons
        else:
            st.session_state["sel_seasons"] = []
            sel_seasons = []

        # Competition
        if sel_player_id:
            player_comp_df = df[df["PlayerID"] == sel_player_id]
            if sel_seasons:
                player_comp_df = player_comp_df[player_comp_df["Season"].isin(sel_seasons)]
            comps = ["All"] + sorted(player_comp_df["Comp"].dropna().unique().tolist())
            prev_comp = st.session_state.get("sel_comp", "All")
            sel_comp = st.sidebar.selectbox(
                "🥅 Competition", comps,
                index=comps.index(prev_comp) if prev_comp in comps else 0,
                key="sb_comp",
            )
            st.session_state["sel_comp"] = sel_comp
        else:
            sel_comp = "All"

    return {
        "filtered_df": filtered,
        "sel_league": sel_league,
        "sel_club": sel_club,
        "sel_player_id": sel_player_id,
        "sel_player_name": sel_display,
        "sel_seasons": sel_seasons,
        "sel_comp": sel_comp,
    }


def get_player_filtered_data(df: pd.DataFrame, player_id: str, seasons: list, comp: str) -> pd.DataFrame:
    pdf = df[df["PlayerID"] == player_id].copy()
    if seasons:
        pdf = pdf[pdf["Season"].isin(seasons)]
    if comp != "All":
        pdf = pdf[pdf["Comp"] == comp]
    return pdf