"""Plotly figures for quiz reports — interactive charts, legends anchored below plots."""

from __future__ import annotations

import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import build_quiz_visualizations as bqv

LABEL_A = bqv.LABEL_A
LABEL_B = bqv.LABEL_B

# One-line keyed rubrics (aligned with LMS key / build_quiz_visualizations.correct)
KEYED_RUBRIC: list[str] = [
    "Organic definition item — keyed answer is the LMS option marked correct for definition of organic chemistry (carbon-based frameworks).",
    "Wedges / hashes — keyed answer asserts stereochemistry interpretation (matches LMS answer key).",
    "Carbon valence — keyed answer selects the option coded “4” in the export for bond-line shorthand.",
    "Implicit atoms — keyed answer selects the choice where implicit H placements match the keyed bond-line depiction.",
    'Atom/count — keyed answer selects the option matching correct counts (typically “5 carbons, 10 hydrogens”) per LMS key.',
    "Coffee/context — keyed answer is “All of the above” for the keyed application stem.",
]


def stem_topic_short(stem_ix: int) -> str:
    nm = bqv.FULL_NAMES[stem_ix].split("(")[0].strip()
    return nm[:44] + ("…" if len(nm) > 44 else "")


def stem_facts_box_html(df: pd.DataFrame, stem_ix: int, *, cohort_note: str) -> str:
    """HTML summary: keyed rule + KPI chips + list of wrong-option shares (LMS text)."""
    fracs, _n = bqv.stack_fractions(df, stem_ix)
    keyed = next((p for lab, p in fracs if lab == "Keyed correct"), 0.0)
    blank = next((p for lab, p in fracs if lab == "No answer"), 0.0)
    wrongs = sorted(
        [(lab, p) for lab, p in fracs if lab not in ("Keyed correct", "No answer")],
        key=lambda z: -z[1],
    )
    any_wrong = max(0.0, 100.0 - keyed - blank)
    rubric = html.escape(KEYED_RUBRIC[stem_ix])
    letter = bqv.LETTER[stem_ix]
    topic = html.escape(stem_topic_short(stem_ix))
    wrong_items = "".join(
        f'<li><span class="wrong-pct">{p:.1f}%</span> <span class="wrong-txt">{html.escape(lab)}</span></li>'
        for lab, p in wrongs[:22]
    )
    if len(wrongs) > 22:
        wrong_items += f'<li class="wrong-more"><em>…and {len(wrongs) - 22} additional low-share option(s) hidden for space</em></li>'
    note = html.escape(cohort_note)
    return f"""<div class="stem-facts">
  <p class="stem-facts-lead"><strong>3{letter} — {topic}</strong> · <span class="cohort-badge">{note}</span></p>
  <p class="stem-rubric"><strong>Keyed (correct):</strong> {rubric}</p>
  <div class="stem-kpis">
    <div class="kpi"><span class="kpi-val">{keyed:.1f}%</span><span class="kpi-lbl">Keyed</span></div>
    <div class="kpi"><span class="kpi-val">{any_wrong:.1f}%</span><span class="kpi-lbl">Combined wrong</span></div>
    <div class="kpi"><span class="kpi-val">{blank:.1f}%</span><span class="kpi-lbl">Blank stem</span></div>
  </div>
  <div class="wrong-wrap">
    <p class="wrong-h"><strong>Wrong / other LMS options picked</strong> (each line is verbatim export wording; % of this cohort answering the stem)</p>
    <ul class="wrong-ul">{wrong_items if wrong_items else "<li>(no sizable wrong shares recorded)</li>"}</ul>
  </div>
</div>
"""


def _legend_label(lab: str) -> str:
    return lab if len(lab) <= 52 else lab[:49] + "…"


def figure_answer_mix_single_stem(
    df: pd.DataFrame,
    stem_ix: int,
    chart_title: str,
    *,
    pooled: bool,
) -> go.Figure:
    """One full-width stacked bar for a single stem (larger type than 3×2 grid)."""
    fracs, _tot = bqv.stack_fractions(df, stem_ix)
    fig = go.Figure()
    if not fracs:
        fig.update_layout(title=chart_title)
        return _base_layout(fig, height=200, margin_bottom=60)
    left = 0.0
    for lab, pct in fracs:
        clr = bqv.color_for_segment(lab)
        fig.add_trace(
            go.Bar(
                orientation="h",
                y=["Responses"],
                x=[pct],
                base=left,
                name=_legend_label(lab),
                legendgroup=lab,
                showlegend=True,
                marker=dict(color=clr, line=dict(color=bqv.UCLA_NAVY, width=0.45)),
                customdata=[lab],
                hovertemplate="%{customdata}<br>%{x:.1f}% of respondents<br><extra></extra>",
                text=[f"{pct:.0f}%" if pct >= 7 else ""],
                textposition="inside",
                insidetextfont=dict(size=12, color="#fff" if (lab == "Keyed correct" or pct >= 18) else bqv.TEXT_DIM),
            )
        )
        left += pct
    scope = "pooled roster" if pooled else "this section’s roster"
    fig.update_xaxes(
        range=[0, 100],
        title=dict(
            text=f"Percent of {scope} (bar = 100% of students who answered this stem)",
            font=dict(size=13),
            standoff=24,
        ),
        tickfont=dict(size=12),
    )
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=15, color=bqv.UCLA_NAVY)),
        barmode="overlay",
        bargap=0.25,
        height=300,
    )
    return _base_layout(
        fig,
        height=400,
        margin_bottom=200,
        margin_right=56,
        show_legend=True,
    )


def _legend_bottom(*, legend_y: float = -0.1) -> dict:
    """Horizontal legend below the plot. Use margin_bottom ≈ 160–260 depending on title height."""
    return dict(
        orientation="h",
        yanchor="top",
        y=legend_y,
        xanchor="center",
        x=0.5,
        xref="paper",
        yref="paper",
        bgcolor="rgba(255,255,255,0.96)",
        bordercolor="#c5dcea",
        borderwidth=1,
        font=dict(size=11),
    )


def _base_layout(
    fig: go.Figure,
    *,
    height: float | None,
    margin_bottom: int,
    margin_right: int = 48,
    margin_left: int = 68,
    margin_top: int = 88,
    show_legend: bool = True,
    legend_y: float = -0.1,
    legend: dict | None = None,
) -> go.Figure:
    if legend is not None:
        leg = legend if show_legend else None
    elif show_legend:
        leg = _legend_bottom(legend_y=legend_y)
    else:
        leg = None
    fig.update_layout(
        legend=leg,
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", color=bqv.TEXT_DIM, size=13),
        title=dict(font=dict(size=15, color=bqv.UCLA_NAVY)),
        hovermode="closest",
        showlegend=show_legend,
    )
    if height:
        fig.update_layout(height=height)
    return fig


def stem_ticktexts() -> list[str]:
    out = []
    for i in range(6):
        short = bqv.FULL_NAMES[i].split("(")[0].strip()
        if len(short) > 26:
            short = short[:24] + "…"
        out.append(f"3{bqv.LETTER[i]}<br>{short}")
    return out


def figure_compare_stems() -> tuple[go.Figure, dict]:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    merged = pd.concat([mq, dd], ignore_index=True)
    s_mq = bqv.item_stats(mq)
    s_dd = bqv.item_stats(dd)
    s_all = bqv.item_stats(merged)

    pmq = [s_mq[i]["pct"] for i in range(6)]
    pdd = [s_dd[i]["pct"] for i in range(6)]
    pall = [s_all[i]["pct"] for i in range(6)]
    x = list(range(6))
    ticks = stem_ticktexts()

    fig = go.Figure()
    fig.add_hrect(y0=90, y1=100, fillcolor="rgba(139,184,232,0.28)", layer="below", line_width=0)
    fig.add_hline(y=90, line_dash="dash", line_color=bqv.UCLA_NAVY, line_width=1)
    fig.add_annotation(
        x=5.4,
        y=91.5,
        text="90% benchmark",
        showarrow=False,
        font=dict(size=10, color=bqv.UCLA_NAVY),
        xref="x",
        yref="y",
    )

    fig.add_trace(
        go.Bar(
            x=x,
            y=pmq,
            name=LABEL_A,
            marker=dict(color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=0.8)),
            hovertemplate="%{y:.1f}% keyed correct<br><extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=x,
            y=pdd,
            name=LABEL_B,
            marker=dict(color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=0.9)),
            hovertemplate="%{y:.1f}% keyed correct<br><extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=pall,
            name="Pooled (MQ+DD)",
            mode="markers",
            marker=dict(size=13, symbol="diamond", color=bqv.UCLA_NAVY, line=dict(color="#fff", width=1)),
            hovertemplate="Pooled %{y:.1f}%<extra></extra>",
        )
    )
    fig.update_xaxes(tickvals=x, ticktext=ticks, tickangle=0)
    fig.update_yaxes(range=[69.5, 101], title="% keyed correct (stem only; blanks excluded)")
    fig.update_layout(
        title="Section 3: per-stem keyed performance · hover bars for exact %",
        barmode="group",
    )
    worst = int(np.argmin([s_all[j]["pct"] for j in range(6)]))
    median_others = float(np.median([s_all[j]["pct"] for j in range(6) if j != worst]))

    insights = dict(
        worst_idx=worst,
        worst_pct=float(s_all[worst]["pct"]),
        median_rest=median_others,
        n_mq=len(mq),
        n_dd=len(dd),
        s_mq=s_mq,
        s_dd=s_dd,
        s_all=s_all,
    )

    fig = _base_layout(fig, height=560, margin_bottom=268, legend_y=-0.1)
    return fig, insights


def figure_tally_histogram() -> tuple[go.Figure, dict]:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    n_m, n_d = len(mq), len(dd)
    d_mq = bqv.total_distribution(mq)
    d_dd = bqv.total_distribution(dd)
    d_all = bqv.total_distribution(pd.concat([mq, dd], ignore_index=True))

    ks = list(range(7))
    x_num = list(range(7))
    pct_mq = np.array([100 * d_mq.get(k, 0) / n_m for k in ks])
    pct_dd = np.array([100 * d_dd.get(k, 0) / n_d for k in ks])
    pct_all = np.array([100 * d_all.get(k, 0) / (n_m + n_d) for k in ks])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x_num,
            y=pct_mq,
            name=f"{LABEL_A}, n={n_m}",
            marker=dict(color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=0.9)),
            text=[f"{v:.0f}%" if v >= 7 else "" for v in pct_mq],
            textposition="outside",
            textfont=dict(size=13),
            hovertemplate="Tally %{customdata}: %{y:.1f}% of MQ<br><extra></extra>",
            customdata=[f"{k}/6" for k in ks],
        )
    )
    fig.add_trace(
        go.Bar(
            x=x_num,
            y=pct_dd,
            name=f"{LABEL_B}, n={n_d}",
            marker=dict(color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=0.9)),
            text=[f"{v:.0f}%" if v >= 7 else "" for v in pct_dd],
            textposition="outside",
            textfont=dict(size=13),
            hovertemplate="Tally %{customdata}: %{y:.1f}% of DD<br><extra></extra>",
            customdata=[f"{k}/6" for k in ks],
        )
    )
    ymax = float(max(np.nanmax(pct_mq), np.nanmax(pct_dd))) * 1.25
    ymax_vis = min(ymax, 102)
    fig.update_yaxes(range=[0, ymax_vis], title=dict(text="% of section at this tally", font=dict(size=13)))
    fig.update_xaxes(
        tickvals=x_num,
        ticktext=[f"{k}/6" for k in ks],
        title=dict(text="Total stems keyed correctly (Section 3 only)", font=dict(size=13), standoff=28),
        tickfont=dict(size=12),
    )
    fig.update_layout(
        title=dict(
            text="Tally histogram (grouped MQ vs DD) — gray band highlights tallies 5/6 and 6/6",
            font=dict(size=16, color=bqv.UCLA_NAVY),
        ),
        barmode="group",
        shapes=[
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=4.62,
                x1=6.38,
                y0=0,
                y1=ymax_vis,
                fillcolor="rgba(0,0,0,0.08)",
                line_width=0,
                layer="below",
            ),
        ],
    )
    pooled_line = (
        f"Pooled headline: {pct_all[6]:.1f}% tally 6/6 • {pct_all[5]:.1f}% 5/6 • "
        f"{100 * sum(d_all.get(k, 0) for k in range(5)) / (n_m + n_d):.1f}% tally ≤4."
    )

    loose = pct_all[np.arange(7) <= 4].sum()
    insights = dict(pooled_pct_le4_or_worse=loose, full_credit=pct_all[6])

    fig.add_annotation(
        text=pooled_line,
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.01,
        yanchor="bottom",
        showarrow=False,
        font=dict(size=12),
    )

    fig.add_annotation(
        text="Gray band covers tally <b>5/6</b> and <b>6/6</b> (keyed ≥5 stems on Section&nbsp;3).",
        xref="paper",
        yref="paper",
        x=0.99,
        y=0.72,
        showarrow=False,
        font=dict(size=11, color="#222"),
        xanchor="right",
        yanchor="top",
        bgcolor="#f4f9ff",
        bordercolor="#c5dcea",
        borderwidth=1,
        borderpad=5,
    )

    fig = _base_layout(fig, height=595, margin_top=74, margin_bottom=248, legend_y=-0.12)
    return fig, insights


def figure_gap_ranking() -> tuple[go.Figure, dict]:
    merged = pd.concat(
        [
            pd.read_csv(bqv.FILES["MQ"], dtype=str),
            pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str),
        ],
        ignore_index=True,
    )
    s_all = bqv.item_stats(merged)
    best = max(s["pct"] for s in s_all)
    deficits = [best - s["pct"] for s in s_all]
    order = np.argsort(deficits)[::-1]
    d_sorted = [deficits[i] for i in order]
    max_d = float(max(d_sorted))
    labs = []
    colors = []
    for idx in order:
        nm = bqv.FULL_NAMES[idx]
        nm = nm[:50] + "…" if len(nm) > 52 else nm
        labs.append(f"3{bqv.LETTER[idx]}  {nm}")
        colors.append(bqv.UCLA_GOLD if abs(deficits[idx] - max_d) < 1e-9 else bqv.UCLA_BLUE)

    fig = go.Figure(
        data=[
            go.Bar(
                x=d_sorted,
                y=list(range(len(labs))),
                orientation="h",
                marker=dict(color=colors, line=dict(color=bqv.UCLA_NAVY, width=0.9)),
                text=[f"−{d:.1f} pp" for d in d_sorted],
                textposition="outside",
                hovertemplate="%{customdata}<br>Gap vs easiest stem (pooled): %{x:.1f} pp<extra></extra>",
                customdata=labs,
                name="gap",
                showlegend=False,
            ),
        ]
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(labs))),
        ticktext=labs,
        autorange="reversed",
    )
    fig.update_xaxes(
        title=f"Percentage points below easiest stem (easiest @ {best:.1f}% pooled)",
        range=[0, max_d * 1.28],
    )
    fig.update_layout(
        title=(
            "Relative difficulty (high → low gap) · easiest stem = highest keyed % pooled; "
            "gold = largest deficit vs that benchmark."
        ),
    )

    hardest_vs_best_idx = int(order[0])
    smallest_gap_idx = int(order[-1])

    insights = {
        "best_pct": float(best),
        "easiest_pool_pct": float(best),
        "largest_gap_pp": float(max_d),
        "largest_gap_idx": hardest_vs_best_idx,
        "nearest_to_easiest_idx": smallest_gap_idx,
    }

    fig = _base_layout(fig, height=560, margin_bottom=120, show_legend=False)
    return fig, insights


def figure_answer_mix_grid(
    df: pd.DataFrame, title: str, suptitle_suffix: str, *, pooled: bool = False
) -> go.Figure:
    """3×2 subplot grid of stacked 100% horizontal bars."""
    subplot_titles = [f"3{bqv.LETTER[i]} — short label" for i in range(6)]  # replaced below
    for i in range(6):
        short = bqv.FULL_NAMES[i].split("(")[0][:22]
        subplot_titles[i] = f"3{bqv.LETTER[i]} · {short}"

    fig = make_subplots(rows=3, cols=2, subplot_titles=subplot_titles, vertical_spacing=0.11, horizontal_spacing=0.12)

    # First subplot defines legend traces
    first_labels: list[str] = []
    seen_order: list[str] = []

    def ensure_order(fracs: list[tuple[str, float]]) -> None:
        for lab, _ in fracs:
            if lab not in seen_order:
                seen_order.append(lab)

    for i in range(6):
        fracs, _ = bqv.stack_fractions(df, i)
        ensure_order(fracs)

    for gi in range(6):
        r, c = gi // 2 + 1, gi % 2 + 1
        fracs, _tot = bqv.stack_fractions(df, gi)
        if not fracs:
            continue
        left = 0.0
        for lab, pct in fracs:
            clr = bqv.color_for_segment(lab)
            showlegend = gi == 0
            trace_name = lab
            fig.add_trace(
                go.Bar(
                    orientation="h",
                    y=[" "],
                    x=[pct],
                    base=left,
                    name=trace_name,
                    legendgroup=lab,
                    showlegend=showlegend,
                    marker=dict(color=clr, line=dict(color=bqv.UCLA_NAVY, width=0.5)),
                    hovertemplate=f"<b>{lab}</b><br>%{{x:.1f}}% of respondents on this stem<br><extra></extra>",
                ),
                row=r,
                col=c,
            )
            left += pct
        ttl = "% of pooled" if pooled else "% of cohort"
        fig.update_xaxes(
            range=[0, 100],
            title_text="" if gi < 4 else ttl,
            row=r,
            col=c,
        )
        fig.update_yaxes(showticklabels=False, row=r, col=c)

    fig.update_layout(
        title=dict(text=f"{title} · {suptitle_suffix}", font=dict(color=bqv.UCLA_NAVY, size=14)),
        bargap=0.45,
        barmode="overlay",
        paper_bgcolor="#fff",
        plot_bgcolor="#fafafa",
    )
    fig.add_annotation(
        text=bqv.ANSWER_MIX_SET_EXPLAIN,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.08,
        showarrow=False,
        font=dict(size=9.5),
        align="center",
        yanchor="bottom",
    )
    fig.update_layout(
        legend=_legend_bottom(legend_y=-0.075),
        legend_traceorder="reversed",
        margin=dict(l=56, r=52, t=118, b=240),
        font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", color=bqv.TEXT_DIM, size=11),
        hovermode="closest",
    )
    fig.update_layout(height=1050)
    return fig


def _likert_series_mean_sd(series: pd.Series) -> tuple[float, float]:
    """Sample mean & SD (−2…+2 likert coded); ddof=1. SD omitted when n≤1."""
    v = pd.to_numeric(series.apply(bqv.likert_num), errors="coerce").dropna()
    arr = np.asarray(v, dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    mu = float(np.mean(arr))
    if arr.size == 1:
        return mu, 0.0
    return mu, float(np.std(arr, ddof=1))


def _likert_means_for_col(mq: pd.DataFrame, dd: pd.DataFrame, coli: int) -> tuple[float, float]:
    va = pd.to_numeric(mq.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
    vb = pd.to_numeric(dd.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
    return float(np.nanmean(va)), float(np.nanmean(vb))


def figure_likert_paired_pre_post() -> go.Figure:
    """Paired prompts: MQ vs DD mean trajectories Pre→Post, ±sample SD bars at each time point (survey, not MC)."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    rows = bqv.survey_likert_rows()
    pre_rows = rows[:3]
    post_rows = rows[3:6]

    dodge = 0.055

    def _brief(s: str, cap: int = 26) -> str:
        t = s.strip().replace("Pre: ", "").replace("Post: ", "")
        frag = t if len(t) <= cap else t[: cap - 1] + "…"
        return html.escape(frag)

    subplot_titles = [
        f"<b>Set {k + 1}</b><br><span style='font-size:10px'>{_brief(pre_rows[k][1])} → {_brief(post_rows[k][1])}</span>"
        for k in range(3)
    ]

    fig = make_subplots(
        rows=1,
        cols=3,
        shared_yaxes=True,
        horizontal_spacing=0.07,
        subplot_titles=subplot_titles,
    )

    y_low = np.inf
    y_high = -np.inf

    def _stretch(mu: float, sd: float) -> None:
        nonlocal y_low, y_high
        if mu != mu:
            return
        s = sd if sd == sd else 0.0
        y_low = min(y_low, mu - s)
        y_high = max(y_high, mu + s)

    for ci in range(3):
        pc, _pshort, _ = pre_rows[ci]
        sc, _sshort, _ = post_rows[ci]

        mq_pre_mu, mq_pre_sd = _likert_series_mean_sd(mq.iloc[:, pc])
        mq_post_mu, mq_post_sd = _likert_series_mean_sd(mq.iloc[:, sc])
        dd_pre_mu, dd_pre_sd = _likert_series_mean_sd(dd.iloc[:, pc])
        dd_post_mu, dd_post_sd = _likert_series_mean_sd(dd.iloc[:, sc])

        for tup in (
            (mq_pre_mu, mq_pre_sd),
            (mq_post_mu, mq_post_sd),
            (dd_pre_mu, dd_pre_sd),
            (dd_post_mu, dd_post_sd),
        ):
            _stretch(tup[0], tup[1])

        mq_pre_sd_vis = mq_pre_sd if mq_pre_sd == mq_pre_sd else 0.0
        mq_post_sd_vis = mq_post_sd if mq_post_sd == mq_post_sd else 0.0
        dd_pre_sd_vis = dd_pre_sd if dd_pre_sd == dd_pre_sd else 0.0
        dd_post_sd_vis = dd_post_sd if dd_post_sd == dd_post_sd else 0.0

        x_mq = [-dodge, 1.0 - dodge]
        x_dd = [dodge, 1.0 + dodge]
        sl = ci == 0

        err_blue = dict(
            type="data",
            symmetric=True,
            array=[mq_pre_sd_vis, mq_post_sd_vis],
            thickness=4,
            color=bqv.UCLA_BLUE,
            width=10,
            visible=True,
        )
        err_gold = dict(
            type="data",
            symmetric=True,
            array=[dd_pre_sd_vis, dd_post_sd_vis],
            thickness=4,
            color=bqv.UCLA_GOLD,
            width=10,
            visible=True,
        )

        mq_txt = [
            f"Pre: {mq_pre_mu:.2f} (SD {mq_pre_sd_vis:.2f})",
            f"Post: {mq_post_mu:.2f} (SD {mq_post_sd_vis:.2f})",
        ]
        dd_txt = [
            f"Pre: {dd_pre_mu:.2f} (SD {dd_pre_sd_vis:.2f})",
            f"Post: {dd_post_mu:.2f} (SD {dd_post_sd_vis:.2f})",
        ]

        fig.add_trace(
            go.Scatter(
                x=x_mq,
                y=[mq_pre_mu, mq_post_mu],
                mode="lines+markers",
                line=dict(width=3.5, color=bqv.UCLA_BLUE),
                marker=dict(size=13, symbol="circle", color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=1)),
                error_y=err_blue,
                name=f"{LABEL_A} — mean ± SD",
                legendgroup="mq",
                showlegend=sl,
                text=mq_txt,
                hovertemplate=f"<b>{LABEL_A}</b><br>%{{text}}<extra></extra>",
            ),
            row=1,
            col=ci + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_dd,
                y=[dd_pre_mu, dd_post_mu],
                mode="lines+markers",
                line=dict(width=3.5, color=bqv.UCLA_GOLD),
                marker=dict(size=13, symbol="square", color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=1)),
                error_y=err_gold,
                name=f"{LABEL_B} — mean ± SD",
                legendgroup="dd",
                showlegend=sl,
                text=dd_txt,
                hovertemplate=f"<b>{LABEL_B}</b><br>%{{text}}<extra></extra>",
            ),
            row=1,
            col=ci + 1,
        )

    if y_low == np.inf:
        yr = [-2.35, 2.35]
    else:
        pad = 0.35
        yr = [
            float(max(y_low - pad, -2.6)),
            float(min(y_high + pad, 2.6)),
        ]

    for jc in range(1, 4):
        fig.update_xaxes(
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["Pre-video", "Post-video"],
            range=[-0.18, 1.18],
            showgrid=False,
            zeroline=False,
            row=1,
            col=jc,
        )
        fig.update_yaxes(
            range=yr,
            dtick=1,
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="#aaa",
            title=dict(text="Likert (−2 … +2)" if jc == 1 else "", standoff=10),
            row=1,
            col=jc,
        )

    fig.update_layout(
        title=dict(
            text="Pre/post paired Likerts — cohort means ± sample SD",
            font=dict(size=14, color=bqv.UCLA_NAVY),
            subtitle=dict(
                text="Blue = MQ, gold = DD — small horizontal offset separates sections. Bars = ±1 SD at each timepoint. Survey items only.",
                font=dict(size=11, color=bqv.TEXT_DIM),
            ),
        ),
        hovermode="closest",
    )
    fig.for_each_annotation(
        lambda a: a.update(
            font=dict(size=11.5, color=bqv.TEXT_DIM, family="Helvetica Neue, Helvetica, Arial, sans-serif"),
        )
    )

    fig = _base_layout(
        fig,
        height=560,
        margin_bottom=220,
        margin_left=76,
        margin_right=52,
        margin_top=190,
        legend=_legend_bottom(legend_y=-0.145),
    )
    return fig


def figure_likert_post_video_feedback() -> go.Figure:
    """Four post‑video Likert items: one subplot each, two horizontal bars (MQ vs DD)."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    rows = bqv.survey_likert_rows()[3:]

    panel_titles = [
        "Post: unfamiliar ideas introduced?",
        "Post: immersive format helped?",
        "Post: needed rewatches?",
        "Post: changed thinking about ochem?",
    ]

    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=panel_titles,
        vertical_spacing=0.07,
    )
    xr = [-2.12, 2.12]

    for i, (coli, _short, _full) in enumerate(rows, start=1):
        xa, xb = _likert_means_for_col(mq, dd, coli)
        show_leg = i == 1
        fig.add_trace(
            go.Bar(
                orientation="h",
                y=[LABEL_A],
                x=[xa],
                name=LABEL_A,
                legendgroup="mq",
                showlegend=show_leg,
                marker=dict(color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=0.55)),
                hovertemplate=f"{LABEL_A}: %{{x:.2f}}<extra></extra>",
            ),
            row=i,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                orientation="h",
                y=[LABEL_B],
                x=[xb],
                name=LABEL_B,
                legendgroup="dd",
                showlegend=show_leg,
                marker=dict(color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=0.55)),
                hovertemplate=f"{LABEL_B}: %{{x:.2f}}<extra></extra>",
            ),
            row=i,
            col=1,
        )
        fig.update_xaxes(range=xr, row=i, col=1)
        fig.add_vline(x=0, line_dash="dot", line_color="#888", row=i, col=1)

    fig.update_xaxes(title=dict(text="Mean (−2 … +2)", standoff=12), row=4, col=1)
    fig.update_layout(
        title=dict(
            text="Post‑video attitudes (four items — same scale as Fig. 3; not exam performance)",
            font=dict(size=14, color=bqv.UCLA_NAVY),
        ),
        barmode="group",
        bargap=0.3,
        bargroupgap=0.08,
    )
    fig.update_yaxes(tickfont=dict(size=11))
    fig = _base_layout(
        fig,
        height=720,
        margin_bottom=200,
        margin_left=108,
        margin_right=52,
        margin_top=108,
        legend=_legend_bottom(legend_y=-0.16),
    )
    return fig


def figure_likert_compare() -> go.Figure:
    """Legacy single-panel Likert chart (all 7 rows). Prefer figure_likert_paired_pre_post + figure_likert_post_video_feedback."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    rows = bqv.survey_likert_rows()

    ylbl = []
    xa, xb = [], []
    for coli, short, full_lbl in rows:
        va = pd.to_numeric(mq.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        vb = pd.to_numeric(dd.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        xa.append(float(np.nanmean(va)))
        xb.append(float(np.nanmean(vb)))
        ylbl.append(short)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(y=ylbl, x=xa, name=LABEL_A, orientation="h", marker=dict(color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=0.6)))
    )
    fig.add_trace(
        go.Bar(y=ylbl, x=xb, name=LABEL_B, orientation="h", marker=dict(color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=0.6)))
    )
    fig.update_xaxes(title=dict(text="Mean score (−2 … +2) · hover a bar", standoff=32))
    fig.update_layout(
        title=dict(text="Pre/post attitudes (survey — not keyed exam MC)", font=dict(size=16, color=bqv.UCLA_NAVY)),
        barmode="group",
        height=640,
        yaxis=dict(tickfont=dict(size=12)),
    )
    fig.add_vline(x=0, line_dash="dot", line_color="#888")
    fig = _base_layout(fig, height=None, margin_bottom=260, legend_y=-0.12)
    return fig


def figure_watch_compare() -> go.Figure:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)

    ctr_m = bqv.watch_answer_counter(mq)
    ctr_d = bqv.watch_answer_counter(dd)
    n_mq, n_dd = sum(ctr_m.values()), sum(ctr_d.values())
    categories = bqv.resolve_watch_categories(ctr_m, ctr_d)

    pct_mq = [100.0 * ctr_m.get(c, 0) / n_mq if n_mq else 0 for c in categories]
    pct_dd = [100.0 * ctr_d.get(c, 0) / n_dd if n_dd else 0 for c in categories]
    lbls = [bqv.WATCH_SHORT_LABEL_FOR_DISPLAY.get(c, c[:40]) for c in categories]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=lbls,
            x=pct_mq,
            name=f"{LABEL_A} · n={n_mq}",
            orientation="h",
            marker=dict(color=bqv.UCLA_BLUE, line=dict(color=bqv.UCLA_NAVY, width=0.7)),
            text=[f"{p:.1f}%" if p >= 6 else "" for p in pct_mq],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate="%{x:.1f}% of MQ cohort · %{fullData.name}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=lbls,
            x=pct_dd,
            name=f"{LABEL_B} · n={n_dd}",
            orientation="h",
            marker=dict(color=bqv.UCLA_GOLD, line=dict(color=bqv.UCLA_NAVY, width=0.7)),
            text=[f"{p:.1f}%" if p >= 6 else "" for p in pct_dd],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate="%{x:.1f}% of DD cohort · %{fullData.name}<extra></extra>",
        )
    )
    fig.update_xaxes(
        title=dict(
            text="% within cohort answering this watch-time option · hover reads exact %",
            standoff=34,
        )
    )
    fig.update_layout(
        title=f"Declared watch time vs assigned section (MQ submissions {n_mq}, DD {n_dd})",
        barmode="group",
        height=520,
        yaxis=dict(autorange="reversed"),
    )
    fig = _base_layout(fig, height=None, margin_bottom=255, legend_y=-0.12)
    return fig


def figure_single_cohort_stems(df: pd.DataFrame, title: str, bar_color: str) -> go.Figure:
    stats_l = bqv.item_stats(df)
    pcts = [stats_l[j]["pct"] for j in range(6)]
    xs = [f"3{bqv.LETTER[j]}" for j in range(6)]
    fig = go.Figure(
        [
            go.Bar(
                x=xs,
                y=pcts,
                marker=dict(color=bar_color, line=dict(color=bqv.UCLA_NAVY, width=0.7)),
                text=[f"{p:.1f}%" for p in pcts],
                textposition="outside",
                hovertemplate="%{x}: %{y:.1f}% keyed<extra></extra>",
                showlegend=False,
            )
        ]
    )
    fig.update_yaxes(range=[0, 105], title="% keyed correct (this section only)")
    fig.update_xaxes(title="Stem (quiz order)")
    fig.update_layout(title=title)
    return _base_layout(fig, height=440, margin_bottom=72, show_legend=False)


def figure_single_section_tally(df: pd.DataFrame, cohort_label: str, bar_color: str) -> go.Figure:
    n = len(df)
    d = bqv.total_distribution(df)
    ks = list(range(7))
    pcts = np.array([100 * d.get(k, 0) / n if n else 0 for k in ks])
    fig = go.Figure(
        [
            go.Bar(
                x=[f"{k}/6" for k in ks],
                y=pcts,
                marker=dict(color=bar_color, line=dict(color=bqv.UCLA_NAVY, width=0.8)),
                text=[f"{v:.0f}%" if v >= 6 else "" for v in pcts],
                textposition="outside",
                showlegend=False,
                hovertemplate=f"{cohort_label}: %{{y:.1f}}% at this tally<br><extra></extra>",
            )
        ]
    )
    fig.update_yaxes(title=f"% of section (n={n})", range=[0, min(100.0, float(np.max(pcts)) * 1.25 + 5)])
    fig.update_xaxes(title="Keyed tally (out of six items)")
    fig.update_layout(title=f"Tally distribution · {cohort_label}")
    return _base_layout(fig, height=460, margin_bottom=72, show_legend=False)


def stem_blanks_counts(df: pd.DataFrame) -> list[int]:
    m = bqv.score_matrix(df)
    return [int(np.sum(np.isnan(m[:, j]))) for j in range(6)]


def html_section3_table_rows() -> str:
    """Generate <tbody> rows with current CSV data."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    merged = pd.concat([mq, dd], ignore_index=True)

    s_a = bqv.item_stats(mq)
    s_b = bqv.item_stats(dd)
    s_p = bqv.item_stats(merged)

    bl_a = stem_blanks_counts(mq)
    bl_b = stem_blanks_counts(dd)

    topics = ["Definition", "Wedges/hashes", "Bonds on C", "Carbons shorthand", "Structure count", "Coffee example"]
    rows_html = []
    for i in range(6):
        rows_html.append(
            "<tr>"
            f"<td>3{bqv.LETTER[i]}</td><td>{topics[i]}</td>"
            f"<td>{s_a[i]['pct']:.1f}% ({s_a[i]['n_answered']})</td>"
            f"<td>{s_b[i]['pct']:.1f}% ({s_b[i]['n_answered']})</td>"
            f"<td>{s_p[i]['pct']:.1f}% ({s_p[i]['n_answered']})</td>"
            f"<td>{bl_a[i]} / {bl_b[i]}</td>"
            "</tr>"
        )
    return "\n".join(rows_html)


