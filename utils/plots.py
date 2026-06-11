import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PRIMARY   = "#1DB954"
SECONDARY = "#FF6B35"
ACCENT1   = "#4ECDC4"
ACCENT2   = "#FFE66D"
ACCENT3   = "#A8DADC"
DANGER    = "#E63946"

BG        = "#0E1117"
SURFACE   = "#161C27"
CARD      = "#1E2530"
BORDER    = "#2A3240"
MUTED     = "#8899AA"
TEXT      = "#FAFAFA"

PALETTE   = [PRIMARY, SECONDARY, ACCENT1, ACCENT2, ACCENT3, DANGER,
             "#C77DFF", "#80B918", "#F4A261"]

_BASE_LAYOUT = dict(
    paper_bgcolor=BG,
    plot_bgcolor=SURFACE,
    font=dict(color=TEXT, family="Inter, sans-serif", size=13),
    title_font=dict(size=16, color=TEXT, family="Inter, sans-serif"),
    margin=dict(t=56, b=40, l=16, r=16),
    legend=dict(
        bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
        font=dict(size=12), orientation="h",
        yanchor="bottom", y=1.02, xanchor="right", x=1,
    ),
    hoverlabel=dict(bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT, size=12)),
    colorway=PALETTE,
)

_AXIS_STYLE = dict(
    gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER,
    tickfont=dict(color=MUTED, size=11),
    title_font=dict(color=MUTED, size=12),
)


def _base(fig: go.Figure, title: str = "", height: int = 420,
          show_legend: bool = True, xaxis_kw: dict = None,
          yaxis_kw: dict = None) -> go.Figure:
    xkw = {**_AXIS_STYLE, **(xaxis_kw or {})}
    ykw = {**_AXIS_STYLE, **(yaxis_kw or {})}
    fig.update_layout(**_BASE_LAYOUT, title=title, height=height,
                      showlegend=show_legend, xaxis=xkw, yaxis=ykw)
    return fig


#Player History

def line_chart_season_stat(agg_df: pd.DataFrame, y_cols: list, title: str, decimals=0) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        if col not in agg_df.columns:
            continue
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Scatter(
            x=agg_df["Season"], y=agg_df[col],
            mode="lines+markers+text",
            name=col,
            line=dict(color=color, width=3, shape="spline", smoothing=0.6),
            marker=dict(size=9, color=color, line=dict(width=2, color=BG)),
            text=[f"<b>{v:.{decimals}f}</b>" if v == v else "" for v in agg_df[col]],
            textposition="top center",
            textfont=dict(size=11, color=color),
            hovertemplate=f"<b>{col}</b><br>Season: %{{x}}<br>Value: %{{y:.{decimals}f}}<extra></extra>",
        ))
    _base(fig, title, height=440,
          xaxis_kw=dict(title="Season", type="category"),
          yaxis_kw=dict(title="Value"))
    fig.update_layout(plot_bgcolor=SURFACE)
    for s in agg_df["Season"].unique():
        fig.add_vline(x=s, line_width=1, line_dash="dot", line_color=BORDER, opacity=0.4)
    return fig


def bar_chart_season_stat(agg_df: pd.DataFrame, y_cols: list, title: str, decimals=0) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        if col not in agg_df.columns:
            continue
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Bar(
            x=agg_df["Season"], y=agg_df[col],
            name=col,
            marker=dict(color=color, opacity=0.88, line=dict(color=BG, width=1.2)),
            text=[f"<b>{v:.{decimals}f}</b>" if v == v else "" for v in agg_df[col]],
            textposition="outside",
            textfont=dict(size=11, color=TEXT),
            hovertemplate=f"<b>{col}</b><br>Season: %{{x}}<br>Value: %{{y:.{decimals}f}}<extra></extra>",
        ))
    _base(fig, title, height=420,
          xaxis_kw=dict(title="Season", type="category"),
          yaxis_kw=dict(title="Value"))
    fig.update_layout(barmode="group", bargap=0.18, bargroupgap=0.06)
    return fig
BAR_COLORS = ["#FFD700", "#E63946"] 
def bar_chart_season_stat1(agg_df: pd.DataFrame, y_cols: list, title: str, decimals=0) -> go.Figure:
    fig = go.Figure()

    for i, col in enumerate(y_cols):
        if col not in agg_df.columns:
            continue

        color = BAR_COLORS[i % len(BAR_COLORS)]

        fig.add_trace(
            go.Bar(
                x=agg_df["Season"],
                y=agg_df[col],
                name=col,
                marker=dict(
                    color=color,
                    opacity=0.88,
                    line=dict(color=BG, width=1.2)
                ),
                text=[f"<b>{v:.{decimals}f}</b>" if v == v else "" for v in agg_df[col]],
                textposition="outside",
                textfont=dict(size=11, color=TEXT),
                hovertemplate=f"<b>{col}</b><br>Season: %{{x}}<br>Value: %{{y:.{decimals}f}}<extra></extra>",
            )
        )

    _base(
        fig,
        title,
        height=420,
        xaxis_kw=dict(title="Season", type="category"),
        yaxis_kw=dict(title="Value"),
    )

    fig.update_layout(
        barmode="group",
        bargap=0.18,
        bargroupgap=0.06,
    )

    return fig



def scatter_player_season(agg_df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    df = agg_df.copy()
    df = df.dropna(subset=[x_col, y_col])
    if df.empty:
        return go.Figure()

    n = len(df)
    colors = [
        f"rgba({int(29 + (255-29)*i/(max(n-1,1)))},{int(185 - (185-107)*i/(max(n-1,1)))},{int(84 + (53-84)*i/(max(n-1,1)))}, 0.9)"
        for i in range(n)
    ]

    sizes = df["MinutesPlayed"].fillna(500) if "MinutesPlayed" in df.columns else pd.Series([12]*n)
    sizes = 8 + (sizes - sizes.min()) / (sizes.max() - sizes.min() + 1) * 18

    fig = go.Figure()
    for idx, (_, row) in enumerate(df.iterrows()):
        xv = row[x_col]
        yv = row[y_col]
        fig.add_trace(go.Scatter(
            x=[xv], y=[yv],
            mode="markers+text",
            name=str(row["Season"]),
            text=[f"<b>{row['Season']}</b>"],
            textposition="top center",
            textfont=dict(size=10, color=TEXT),
            marker=dict(
                size=sizes.iloc[idx],
                color=colors[idx],
                line=dict(width=1.5, color=BG),
                symbol="circle",
            ),
            hovertemplate=(
                f"<b>{row['Season']}</b><br>"
                f"{x_col}: {xv:.1f}<br>"
                f"{y_col}: {yv:.1f}<br>"
                + (f"Minutes: {int(row['MinutesPlayed'])}" if "MinutesPlayed" in row else "")
                + "<extra></extra>"
            ),
            showlegend=True,
        ))

    if n > 2:
        x_num = pd.to_numeric(df[x_col], errors="coerce")
        y_num = pd.to_numeric(df[y_col], errors="coerce")
        valid = x_num.notna() & y_num.notna()
        if valid.sum() > 2:
            z = np.polyfit(x_num[valid], y_num[valid], 1)
            x_range = np.linspace(x_num[valid].min(), x_num[valid].max(), 60)
            # fig.add_trace(go.Scatter(
            #     x=x_range, y=np.polyval(z, x_range),
            #     mode="lines",
            #     name="Trend",
            #     line=dict(color=SECONDARY, width=1.5, dash="dot"),
            #     hoverinfo="skip",
            #     showlegend=True,
            # ))

    _base(fig, f"{x_col} vs {y_col} (by Season)", height=460,
          xaxis_kw=dict(title=x_col),
          yaxis_kw=dict(title=y_col))
    fig.update_layout(legend=dict(
        orientation="v", x=1.01, y=1, xanchor="left", yanchor="top",
        bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
    ))
    return fig


def scatter_player_by_competition(raw_df: pd.DataFrame, x_col: str, y_col: str,
                                   player_name: str) -> go.Figure:
    """
    Scatter where each dot = one season+competition row (no aggregation).
    Colour encodes competition. Squad/Club shown in hover.
    """
    df = raw_df.copy()
    df = df.dropna(subset=[x_col, y_col])
    if df.empty:
        return go.Figure()

    comps = df["Comp"].dropna().unique().tolist()
    cmap = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(sorted(comps))}

    fig = go.Figure()
    for comp, grp in df.groupby("Comp"):
        color = cmap.get(comp, PRIMARY)
        squad_col = "Squad" if "Squad" in grp.columns else "ClubName"
        hover_squad = grp[squad_col] if squad_col in grp.columns else ["—"] * len(grp)

        fig.add_trace(go.Scatter(
            x=grp[x_col],
            y=grp[y_col],
            mode="markers+text",
            name=comp,
            text=grp["Season"].astype(str),
            textposition="top center",
            textfont=dict(size=9, color=TEXT),
            marker=dict(size=11, color=color, opacity=0.85,
                        line=dict(width=1.5, color=BG)),
            customdata=list(zip(
                grp["Season"].astype(str),
                hover_squad,
                grp[x_col].round(1),
                grp[y_col].round(1),
            )),
            hovertemplate=(
                f"<b>{player_name}</b><br>"
                "Season: %{customdata[0]}<br>"
                "Club: %{customdata[1]}<br>"
                f"{x_col}: %{{customdata[2]}}<br>"
                f"{y_col}: %{{customdata[3]}}<extra></extra>"
            ),
        ))

    _base(fig, f"{x_col} vs {y_col} (by Competition)", height=460,
          xaxis_kw=dict(title=x_col),
          yaxis_kw=dict(title=y_col))
    fig.update_layout(legend=dict(
        orientation="v", x=1.01, y=1, xanchor="left", yanchor="top",
        bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
    ))
    return fig


def line_chart_by_competition(raw_df: pd.DataFrame, y_cols: list, title: str,
                               decimals=0) -> go.Figure:
    """
    Multi-line chart: one line per competition per stat.
    Each row = individual season+competition entry (no summing).
    """
    fig = go.Figure()
    comps = sorted(raw_df["Comp"].dropna().unique().tolist())
    color_idx = 0

    for comp in comps:
        sub = raw_df[raw_df["Comp"] == comp].sort_values("Season")
        for col in y_cols:
            if col not in sub.columns:
                continue
            color = PALETTE[color_idx % len(PALETTE)]
            color_idx += 1
            squad_col = "Squad" if "Squad" in sub.columns else "ClubName"
            hover_squad = sub[squad_col] if squad_col in sub.columns else ["—"] * len(sub)

            fig.add_trace(go.Scatter(
                x=sub["Season"], y=sub[col],
                mode="lines+markers",
                name=f"{col} · {comp}",
                line=dict(color=color, width=2.5, shape="spline", smoothing=0.5),
                marker=dict(size=8, color=color, line=dict(width=1.5, color=BG)),
                customdata=list(zip(hover_squad, sub[col].round(decimals))),
                hovertemplate=(
                    f"<b>{col}</b> ({comp})<br>"
                    "Season: %{x}<br>"
                    "Club: %{customdata[0]}<br>"
                    f"Value: %{{customdata[1]:.{decimals}f}}<extra></extra>"
                ),
            ))

    _base(fig, title, height=460,
          xaxis_kw=dict(title="Season", type="category"),
          yaxis_kw=dict(title="Value"))
    fig.update_layout(plot_bgcolor=SURFACE)
    return fig


def bar_chart_by_competition(raw_df: pd.DataFrame, y_cols: list, title: str,
                              decimals=0) -> go.Figure:
    """Grouped bar: x = Season, colour = Competition, one group per stat."""
    fig = go.Figure()
    comps = sorted(raw_df["Comp"].dropna().unique().tolist())
    color_idx = 0

    for comp in comps:
        sub = raw_df[raw_df["Comp"] == comp].sort_values("Season")
        for col in y_cols:
            if col not in sub.columns:
                continue
            color = PALETTE[color_idx % len(PALETTE)]
            color_idx += 1
            fig.add_trace(go.Bar(
                x=sub["Season"], y=sub[col],
                name=f"{col} · {comp}",
                marker=dict(color=color, opacity=0.88, line=dict(color=BG, width=1)),
                text=[f"{v:.{decimals}f}" for v in sub[col]],
                textposition="outside",
                textfont=dict(size=10, color=TEXT),
                hovertemplate=(
                    f"<b>{col}</b> ({comp})<br>"
                    "Season: %{x}<br>"
                    f"Value: %{{y:.{decimals}f}}<extra></extra>"
                ),
            ))

    _base(fig, title, height=420,
          xaxis_kw=dict(title="Season", type="category"),
          yaxis_kw=dict(title="Value"))
    fig.update_layout(barmode="group", bargap=0.15, bargroupgap=0.04)
    return fig


def squad_career_bar(raw_df: pd.DataFrame, metric: str, player_name: str) -> go.Figure:
    """
    Horizontal stacked bar showing a metric per season broken out by Squad/Club.
    Useful to see how a player's output was split across clubs they played for.
    """
    squad_col = "Squad" if "Squad" in raw_df.columns else "ClubName"
    df = raw_df.dropna(subset=[metric, "Season"]).copy()
    df[squad_col] = df[squad_col].fillna("Unknown")

    squads = sorted(df[squad_col].unique())
    seasons = sorted(df["Season"].unique())

    fig = go.Figure()
    for i, squad in enumerate(squads):
        color = PALETTE[i % len(PALETTE)]
        sub = df[df[squad_col] == squad]
        # Aggregate per season for this squad
        season_vals = sub.groupby("Season")[metric].sum().reindex(seasons, fill_value=0)

        fig.add_trace(go.Bar(
            x=season_vals.index.astype(str),
            y=season_vals.values,
            name=squad,
            marker=dict(color=color, opacity=0.88, line=dict(color=BG, width=0.8)),
            hovertemplate=(
                f"<b>{squad}</b><br>"
                "Season: %{x}<br>"
                f"{metric}: %{{y}}<extra></extra>"
            ),
        ))

    _base(fig, f"{player_name} : {metric} by Club per Season", height=420,
          xaxis_kw=dict(title="Season", type="category"),
          yaxis_kw=dict(title=metric))
    fig.update_layout(barmode="stack", bargap=0.2)
    return fig


def squad_metric_cards_data(raw_df: pd.DataFrame, metric_cols: list) -> pd.DataFrame:
    """
    Return per-squad aggregated totals for the given metric columns.
    Used to render small metric breakdowns per club in the UI.
    """
    squad_col = "Squad" if "Squad" in raw_df.columns else "ClubName"
    agg_dict = {}
    for col in metric_cols:
        if col in raw_df.columns:
            agg_dict[col] = "sum"
    if not agg_dict:
        return pd.DataFrame()
    return raw_df.groupby(squad_col, as_index=False).agg(agg_dict)


def radar_chart(categories: list, values: list, actual_values: list,
                player_name: str) -> go.Figure:
    r_closed = values + [values[0]]
    t_closed = categories + [categories[0]]
    a_closed = actual_values + [actual_values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=r_closed, theta=t_closed, customdata=a_closed,
        fill="toself",
        fillcolor="rgba(29,185,84,0.18)",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=6, color=PRIMARY, line=dict(width=1, color=BG)),
        name=player_name,
        hovertemplate=(
            "<b>%{theta}</b><br>"
            "Actual: %{customdata}<br>"
            "Score: %{r:.1f}/10<extra></extra>"
        ),
    ))
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(text=f"{player_name} — Attribute Radar",
                   font=dict(size=16, color=TEXT)),
        height=460,
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(
                visible=True, range=[0, 10],
                gridcolor=BORDER, tickcolor=MUTED, tickfont=dict(color=MUTED, size=9),
                linecolor=BORDER,
            ),
            angularaxis=dict(
                gridcolor=BORDER, linecolor=BORDER,
                tickfont=dict(color=TEXT, size=12),
            ),
        ),
        showlegend=False,
    )
    return fig


#Comparison Charts

def comparison_bar(players: list, metric: str, fmt_fn) -> go.Figure:
    player_colors = [PRIMARY, SECONDARY, ACCENT1]
    fig = go.Figure()
    for i, p in enumerate(players):
        val = p.get(metric, 0) or 0
        fig.add_trace(go.Bar(
            name=p["Player"],
            x=[p["Player"]], y=[val],
            marker=dict(color=player_colors[i % len(player_colors)],
                        line=dict(color=BG, width=1.5), opacity=0.9),
            text=[fmt_fn(metric, val)],
            textposition="outside",
            textfont=dict(size=14, color=TEXT, family="Inter"),
            width=0.45,
            hovertemplate=f"<b>{p['Player']}</b><br>{metric}: {fmt_fn(metric, val)}<extra></extra>",
        ))
    _base(fig, f"{metric} — Comparison", height=420, show_legend=False,
          xaxis_kw=dict(tickfont=dict(size=13, color=TEXT)),
          yaxis_kw=dict(title=metric))
    fig.add_hline(y=0, line_color=BORDER, line_width=1)
    return fig


def comparison_scatter(players: list, x_metric: str, y_metric: str, fmt_fn) -> go.Figure:
    player_colors = [PRIMARY, SECONDARY, ACCENT1]
    fig = go.Figure()
    for i, p in enumerate(players):
        xv = p.get(x_metric, 0) or 0
        yv = p.get(y_metric, 0) or 0
        fig.add_trace(go.Scatter(
            x=[xv], y=[yv],
            mode="markers+text",
            name=p["Player"],
            text=[f"  {p['Player']}"],
            textposition="top center",
            textfont=dict(size=12, color=TEXT),
            marker=dict(size=22, color=player_colors[i % len(player_colors)],
                        line=dict(width=2, color=BG), symbol="circle"),
            hovertemplate=(
                f"<b>{p['Player']}</b><br>"
                f"{x_metric}: {fmt_fn(x_metric, xv)}<br>"
                f"{y_metric}: {fmt_fn(y_metric, yv)}<extra></extra>"
            ),
        ))
    _base(fig, f"{x_metric} vs {y_metric}", height=420,
          xaxis_kw=dict(title=x_metric),
          yaxis_kw=dict(title=y_metric))
    return fig


def comparison_radar(players: list, categories: list) -> go.Figure:
    player_colors = [PRIMARY, SECONDARY, ACCENT1]
    fig = go.Figure()

    for i, p in enumerate(players):
        vals = [p.get(c, 0) or 0 for c in categories]
        r_c = vals + [vals[0]]
        t_c = categories + [categories[0]]
        c = player_colors[i % len(player_colors)]
        r_int = int(c[1:3], 16)
        g_int = int(c[3:5], 16)
        b_int = int(c[5:7], 16)

        fig.add_trace(go.Scatterpolar(
            r=r_c, theta=t_c,
            fill="toself",
            fillcolor=f"rgba({r_int},{g_int},{b_int},0.28)",
            line=dict(color=c, width=2.8),
            marker=dict(size=6, color=c),
            name=p["Player"],
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}/10<extra></extra>",
        ))

    base_no_legend = {k: v for k, v in _BASE_LAYOUT.items() if k != "legend"}
    fig.update_layout(
        **base_no_legend,
        title="Attribute Radar Comparison",
        height=520,
        legend=dict(
            bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
            font=dict(size=12), orientation="h",
            yanchor="bottom", y=-0.18, xanchor="center", x=0.5,
        ),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[0, 10],
                            gridcolor=BORDER, tickcolor=MUTED,
                            tickfont=dict(color=MUTED, size=9), linecolor=BORDER),
            angularaxis=dict(gridcolor=BORDER, linecolor=BORDER,
                             tickfont=dict(color=TEXT, size=12)),
        ),
    )
    return fig


#League Stats

def top_n_bar(df: pd.DataFrame, metric: str, n: int = 15, title: str = "") -> go.Figure:
    top = df.nlargest(n, metric)[["Player", "ClubName", metric]].copy()
    top = top.sort_values(metric, ascending=True).reset_index(drop=True)

    n_rows = len(top)
    bar_colors = [
        f"rgba(29,{int(80 + (185-80)*i/(max(n_rows-1,1)))},{int(20 + (84-20)*i/(max(n_rows-1,1)))},0.85)"
        for i in range(n_rows)
    ]

    fig = go.Figure(go.Bar(
        x=top[metric],
        y=top["Player"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color=BG, width=0.8)),
        customdata=top["ClubName"],
        text=[f" {v:.0f}" for v in top[metric]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT),
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>%{x:.1f}<extra></extra>",
    ))
    _base(fig, title or f"Top {n} — {metric}", height=max(360, n_rows * 28),
          show_legend=False,
          xaxis_kw=dict(title=metric, showgrid=True),
          yaxis_kw=dict(showgrid=False, tickfont=dict(size=11)))
    fig.update_layout(margin=dict(l=160, r=60, t=56, b=32))
    return fig


def cards_stacked_bar(df: pd.DataFrame, n: int = 20) -> go.Figure:
    total = df["YellowCards"].fillna(0) + df["RedCards"].fillna(0)
    top = df.assign(_total=total).nlargest(n, "_total")[
        ["Player", "ClubName", "YellowCards", "RedCards"]
    ].sort_values("YellowCards", ascending=True).reset_index(drop=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top["YellowCards"], y=top["Player"], orientation="h",
        name="Yellow Cards",
        marker=dict(color=ACCENT2, opacity=0.9, line=dict(color=BG, width=0.8)),
        hovertemplate="<b>%{y}</b><br>Yellow: %{x}<extra></extra>",
        text=[str(int(v)) for v in top["YellowCards"]],
        textposition="inside", textangle=0, textfont=dict(color="#1a1a1a", size=14),
    ))
    fig.add_trace(go.Bar(
        x=top["RedCards"], y=top["Player"], orientation="h",
        name="Red Cards",
        marker=dict(color=DANGER, opacity=0.9, line=dict(color=BG, width=0.8)),
        hovertemplate="<b>%{y}</b><br>Red: %{x}<extra></extra>",
        text=[str(int(v)) for v in top["RedCards"]],
        textposition="inside", textangle=0, textfont=dict(color=TEXT, size=14),
    ))
    _base(fig, "Discipline : Cards", height=max(360, len(top) * 28),
          xaxis_kw=dict(title="Cards", showgrid=True),
          yaxis_kw=dict(showgrid=False, tickfont=dict(size=11)))
    fig.update_layout(
        barmode="stack",
        margin=dict(l=160, r=48, t=56, b=32),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def league_scatter(df: pd.DataFrame, x_col: str, y_col: str,
                   label_threshold: float = 0.85) -> go.Figure:
    plot_df = df.dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return go.Figure()

    clubs = plot_df["ClubName"].unique()
    cmap = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(sorted(clubs))}
    thresh = plot_df[y_col].quantile(label_threshold)

    fig = go.Figure()
    for club, grp in plot_df.groupby("ClubName"):
        color = cmap[club]
        top_mask = grp[y_col] >= thresh

        # Build hover columns
        nation_col = grp["Nation"] if "Nation" in grp.columns else pd.Series(["—"] * len(grp), index=grp.index)
        goals_col = grp["Goals"] if "Goals" in grp.columns else pd.Series([0] * len(grp), index=grp.index)
        assists_col = grp["Assists"] if "Assists" in grp.columns else pd.Series([0] * len(grp), index=grp.index)

        custom = list(zip(
            grp["Player"],
            nation_col,
            goals_col.fillna(0).astype(int),
            assists_col.fillna(0).astype(int),
            grp[x_col].round(1),
            grp[y_col].round(1),
        ))

        hover_tmpl = (
            "<b>%{customdata[0]}</b><br>"
            "🌍 %{customdata[1]}<br>"
            "🏟️ " + club + "<br>"
            "⚽ Goals: %{customdata[2]} | 🅰️ Assists: %{customdata[3]}<br>"
            f"{x_col}: %{{customdata[4]}}<br>"
            f"{y_col}: %{{customdata[5]}}<extra></extra>"
        )

        for mask, mode, tpos in [
            (~top_mask, "markers", None),
            (top_mask, "markers+text", "top center"),
        ]:
            sub = grp[mask]
            if sub.empty:
                continue
            sub_custom = [custom[i] for i in range(len(grp)) if mask.iloc[i]]
            fig.add_trace(go.Scatter(
                x=sub[x_col], y=sub[y_col],
                mode=mode,
                name=club,
                legendgroup=club,
                showlegend=(mode == "markers"),
                text=sub["Player"] if tpos else None,
                textposition=tpos,
                textfont=dict(size=9, color=TEXT),
                marker=dict(size=8, color=color, opacity=0.75,
                            line=dict(width=0.8, color=BG)),
                customdata=sub_custom,
                hovertemplate=hover_tmpl,
            ))

    _base(fig, f"{x_col} vs {y_col}", height=500,
          xaxis_kw=dict(title=x_col),
          yaxis_kw=dict(title=y_col))
    fig.update_layout(legend=dict(
        orientation="v", x=1.01, y=1, xanchor="left",
        bgcolor=CARD, bordercolor=BORDER, borderwidth=1,
        font=dict(size=10),
    ))
    return fig


def distribution_hist(df: pd.DataFrame, metric: str, title: str = "") -> go.Figure:
    vals = pd.to_numeric(df[metric], errors="coerce").dropna()
    mean_v = vals.mean()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=vals, nbinsx=30,
        marker=dict(color=PRIMARY, opacity=0.82, line=dict(color=BG, width=0.6)),
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
        name=metric,
    ))
    fig.add_vline(
        x=mean_v, line_width=2, line_dash="dash", line_color=SECONDARY,
        annotation_text=f"Avg {mean_v:.1f}",
        annotation_position="top right",
        annotation_font=dict(color=SECONDARY, size=12),
    )
    _base(fig, title or f"Distribution — {metric}", height=380,
          show_legend=False,
          xaxis_kw=dict(title=metric),
          yaxis_kw=dict(title="Players"))
    return fig


def club_aggregated_bar(club_df: pd.DataFrame, metric: str, title: str = "") -> go.Figure:
    df_s = club_df.sort_values(metric, ascending=False).head(25)
    n = len(df_s)
    colors = [
        f"rgba({int(255 - (255-29)*i/(max(n-1,1)))},{int(107 + (185-107)*i/(max(n-1,1)))},{int(53 + (84-53)*i/(max(n-1,1)))},0.88)"
        for i in range(n)
    ]
    fig = go.Figure(go.Bar(
        x=df_s["ClubName"], y=df_s[metric],
        marker=dict(color=colors, line=dict(color=BG, width=0.8)),
        text=[f"{v:.0f}" for v in df_s[metric]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}<extra></extra>",
    ))
    _base(fig, title or f"{metric} by Club", height=420, show_legend=False,
          xaxis_kw=dict(tickangle=-38, tickfont=dict(size=10)),
          yaxis_kw=dict(title=metric))
    return fig


def club_competition_stacked_bar(raw_df: pd.DataFrame, metric: str,
                                  title: str = "") -> go.Figure:
    """
    Stacked bar: x = Club, stacked by Competition.
    Shows how a club's total metric is split across competitions.
    """
    if "Comp" not in raw_df.columns or "ClubName" not in raw_df.columns:
        return go.Figure()

    grp = (
        raw_df.groupby(["ClubName", "Comp"], as_index=False)[metric]
        .sum()
    )
    # Total per club for ordering
    totals = grp.groupby("ClubName")[metric].sum().sort_values(ascending=False)
    top_clubs = totals.head(25).index.tolist()
    grp = grp[grp["ClubName"].isin(top_clubs)]
    grp["ClubName"] = pd.Categorical(grp["ClubName"], categories=top_clubs, ordered=True)
    grp = grp.sort_values("ClubName")

    comps = sorted(grp["Comp"].unique())
    fig = go.Figure()
    for i, comp in enumerate(comps):
        sub = grp[grp["Comp"] == comp]
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Bar(
            x=sub["ClubName"].astype(str),
            y=sub[metric],
            name=comp,
            marker=dict(color=color, opacity=0.88, line=dict(color=BG, width=0.6)),
            hovertemplate=f"<b>%{{x}}</b><br>{comp}<br>{metric}: %{{y:.0f}}<extra></extra>",
        ))

    _base(fig, title or f"{metric} by Club × Competition", height=460,
          xaxis_kw=dict(tickangle=-38, tickfont=dict(size=10)),
          yaxis_kw=dict(title=metric))
    fig.update_layout(barmode="stack", bargap=0.15)
    return fig


def club_players_bar(df: pd.DataFrame, club_name: str, metric: str,
                     n: int = 20) -> go.Figure:
    """
    Horizontal bar showing top N players of a specific club for a metric.
    Each bar is coloured by competition.
    """
    club_df = df[df["ClubName"] == club_name].copy()
    if club_df.empty:
        return go.Figure()

    agg = club_df.groupby(["Player", "ClubName"], as_index=False)[metric].sum()
    agg = agg.nlargest(n, metric).sort_values(metric, ascending=True).reset_index(drop=True)

    n_rows = len(agg)
    bar_colors = [
        f"rgba(78,{int(150 + (205-150)*i/(max(n_rows-1,1)))},{int(196 + (212-196)*i/(max(n_rows-1,1)))},0.85)"
        for i in range(n_rows)
    ]

    fig = go.Figure(go.Bar(
        x=agg[metric],
        y=agg["Player"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color=BG, width=0.8)),
        text=[f" {v:.0f}" for v in agg[metric]],
        textposition="outside",
        textfont=dict(size=11, color=TEXT),
        hovertemplate=f"<b>%{{y}}</b><br>{metric}: %{{x:.1f}}<extra></extra>",
    ))
    _base(fig, f"{club_name} — {metric} by Player", height=max(340, n_rows * 28),
          show_legend=False,
          xaxis_kw=dict(title=metric, showgrid=True),
          yaxis_kw=dict(showgrid=False, tickfont=dict(size=11)))
    fig.update_layout(margin=dict(l=160, r=60, t=56, b=32))
    return fig

