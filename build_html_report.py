#!/usr/bin/env python3
"""
Build Organic_Chemistry_Video_Quiz_Report.html with interactive Plotly figures (hover, pan, legend
anchored below plots). Includes data-driven interpretation blurbs and CSV-backed tables.

Needs: Python packages plotly, pandas, numpy (same project as build_quiz_visualizations.py).

Run:
  python3 build_html_report.py
"""

from __future__ import annotations

import html as html_mod
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.io as pio

import build_quiz_visualizations as bqv
from plotly_quiz_figures import (
    figure_answer_mix_single_stem,
    figure_compare_stems,
    figure_gap_ranking,
    figure_likert_paired_pre_post,
    figure_likert_post_video_feedback,
    figure_watch_compare,
    html_section3_table_rows,
    stem_facts_box_html,
    stem_topic_short,
)

from cohort_comparison import cohort_exploratory_comparison_html
from report_styles import REPORT_CSS

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Organic_Chemistry_Video_Quiz_Report.html"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.30.1.min.js"


def plotly_chart_html(fig, div_id: str) -> str:
    """Wrap Plotly embed for responsive layout."""
    inner = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        div_id=div_id,
        config={"displayModeBar": True, "responsive": True},
    )
    return f'<div class="plotly-host">{inner}</div>'


def _interpret(text: str) -> str:
    return f'      <div class="interpret">\n        {text}\n      </div>\n'


def render_stem_answer_series(
    df: pd.DataFrame,
    fig_bundle: str,
    pooled: bool,
    cohort_note: str,
) -> str:
    """One figure per stem (a–f) with facts box then chart."""
    parts: list[str] = []
    for ix in range(6):
        slug = chr(ord("a") + ix)
        topic = stem_topic_short(ix)
        chart_title = (
            f"Pooled MQ + DD · 3{bqv.LETTER[ix]} ({topic})" if pooled else f"{cohort_note} · 3{bqv.LETTER[ix]} ({topic})"
        )
        fig_obj = figure_answer_mix_single_stem(df, ix, chart_title=chart_title, pooled=pooled)
        div_id = f"mix-{fig_bundle}-{slug}"
        facts = stem_facts_box_html(df, ix, cohort_note=cohort_note)
        parts.append(
            f"""
      <figure class="figure-block mix-stem">
        <span class="tag">Fig. {fig_bundle}{slug} · Stem 3{bqv.LETTER[ix]}</span>
        {facts}
{plotly_chart_html(fig_obj, div_id)}
        <figcaption class="fine-print">The shaded box is the narrative: keyed LMS rule, KPI chips, then verbatim incorrect option lines—stacked bars plot the same cohort.</figcaption>
      </figure>
"""
        )
    return "".join(parts)


def likert_table_sections() -> tuple[str, str]:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    rows = bqv.survey_likert_rows()
    pre = rows[:3]
    post = rows[3:]
    out_pre, out_post = [], []
    for coli, short, _full in pre:
        va = pd.to_numeric(mq.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        vb = pd.to_numeric(dd.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        out_pre.append(
            f"<tr><td>{html_mod.escape(short)}</td><td>{np.nanmean(va):+.2f}</td><td>{np.nanmean(vb):+.2f}</td></tr>"
        )
    for coli, short, _full in post:
        va = pd.to_numeric(mq.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        vb = pd.to_numeric(dd.iloc[:, coli].apply(bqv.likert_num), errors="coerce")
        out_post.append(
            f"<tr><td>{html_mod.escape(short)}</td><td>{np.nanmean(va):+.2f}</td><td>{np.nanmean(vb):+.2f}</td></tr>"
        )
    return "\n".join(out_pre), "\n".join(out_post)


def qualitative_essay_summary_html(n_mq: int, n_dd: int) -> str:
    """Counts for open-ended essay column (verbatim text stays in LMS exports only)."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)

    essay_col = 50

    def nonblank(series: pd.Series) -> int:
        n = 0
        for v in series:
            if pd.isna(v):
                continue
            t = str(v).strip()
            if t and t.lower() not in ("(blank)", "nan"):
                n += 1
        return n

    qa, qb = nonblank(mq.iloc[:, essay_col]), nonblank(dd.iloc[:, essay_col])
    header = str(mq.columns[essay_col])
    header = header[:180] + ("…" if len(header) > 180 else "")
    header_esc = html_mod.escape(header)
    pct_a = 100 * qa / n_mq if n_mq else 0.0
    pct_b = 100 * qb / n_dd if n_dd else 0.0

    return f"""      <table class="data-table"><thead><tr><th>Cohort</th><th>n (export rows)</th><th>Non-blank essay replies</th><th>% with text</th></tr></thead>
      <tbody>
        <tr><td>Section A (MQ)</td><td>{n_mq}</td><td>{qa}</td><td>{pct_a:.1f}%</td></tr>
        <tr><td>Section B (DD)</td><td>{n_dd}</td><td>{qb}</td><td>{pct_b:.1f}%</td></tr>
      </tbody></table>
      <p class="subsection-lede fine-print">Essay wording in export (truncated title): “{header_esc}” · Full replies are omitted here for readability; thematic coding can use the same column in both CSV files.</p>"""


def watch_counts_table() -> str:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    cm, cd = bqv.watch_answer_counter(mq), bqv.watch_answer_counter(dd)
    keys = bqv.resolve_watch_categories(cm, cd)
    rows = []
    for k in keys:
        full = html_mod.escape(k)
        disp = html_mod.escape(k if len(k) <= 90 else k[:87] + "…")
        rows.append(
            f'<tr><td title="{full}">{disp}</td><td>{cm.get(k, 0)}</td><td>{cd.get(k, 0)}</td></tr>'
        )
    return "\n".join(rows)


def main() -> None:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    merged = pd.concat([mq, dd], ignore_index=True)
    n_mq, n_dd = len(mq), len(dd)
    n_all = len(merged)

    d_pool = bqv.total_distribution(merged)
    pct6 = 100 * d_pool.get(6, 0) / n_all if n_all else 0
    pct_le4 = (
        100 * sum(d_pool.get(k, 0) for k in range(5)) / n_all
        if n_all
        else 0
    )

    weakest = int(np.argmin([bqv.item_stats(merged)[j]["pct"] for j in range(6)]))
    weakest_pct = float(bqv.item_stats(merged)[weakest]["pct"])

    stem_interpret = (
        f"<strong>What this shows:</strong> For each quiz stem (3A–3F), the chart compares keyed correct "
        f"rates between Section A ({n_mq} exports) and Section B ({n_dd} exports); diamonds summarize the pooled cohort. "
        f"<strong>Takeaway:</strong> Hover any bar — the weakest pooled stem right now is <strong>3{bqv.LETTER[weakest]}</strong> "
        f"(about <strong>{weakest_pct:.1f}%</strong> keyed in the combined sample), so prioritize review vocabulary or skills tied to that item."
    )

    fig_keyed, _ = figure_compare_stems()

    fig_gap, gap_ins = figure_gap_ranking()
    gid = int(gap_ins["largest_gap_idx"])

    mq_df, dd_df = mq, dd
    merged_concat = merged

    mix_head_pooled = (
        '<section class="mix-bundle" id="fig6-series">\n'
        '      <h3>Figs. 6<span class="subs">a</span>&ndash;<span class="subs">f</span> · Pooled (MQ&nbsp;+&nbsp;DD)</h3>\n'
        '      <p class="subsection-lede">Each letter (a–f) is one stem. Read each shaded <strong>narrative</strong> box (Keyed LMS definition → KPI chips → list of incorrect options), then inspect the stacked bar.</p>\n'
    )
    pooled_series = render_stem_answer_series(merged_concat, "6", True, f"Pooled (n = {n_all})")
    pooled_section_html = mix_head_pooled + pooled_series + "    </section>\n"

    mix_head_mq = (
        '    <section class="mix-bundle" id="fig7-series">\n'
        '      <h3>Figs. 7<span class="subs">a</span>&ndash;<span class="subs">f</span> · Section A (MQ only)</h3>\n'
        '      <p class="subsection-lede">Same six stems restricted to the MQ roster—pair with Figs.&nbsp;6 when checking section-specific misconceptions.</p>\n'
    )
    mq_series_html = render_stem_answer_series(mq_df, "7", False, f"MQ only (n = {n_mq})")
    mq_mix_section_html = mix_head_mq + mq_series_html + "    </section>\n"

    mix_head_dd = (
        '    <section class="mix-bundle" id="fig8-series">\n'
        '      <h3>Figs. 8<span class="subs">a</span>&ndash;<span class="subs">f</span> · Section B (DD only)</h3>\n'
        '      <p class="subsection-lede">Same six stems restricted to the CHEM14BE roster.</p>\n'
    )
    dd_series_html = render_stem_answer_series(dd_df, "8", False, f"DD only (n = {n_dd})")
    dd_mix_section_html = mix_head_dd + dd_series_html + "    </section>\n"

    stem_mix_region = (
        f'<div id="stem-narratives">\n{pooled_section_html}{mq_mix_section_html}{dd_mix_section_html}</div>\n'
    )

    fig_watch = figure_watch_compare()
    watch_interp = (
        '<p><strong>How to read:</strong> Bars show <em>percentage within each LMS section import</em> at each checklist option—the raw LMS strings label the rows.</p>'
        '<p>Hover for exact percentages; the watch table recap lists headline counts beside the verbatim checkbox text.</p>'
    )

    fig_paired_pre_post = figure_likert_paired_pre_post()
    paired_likert_interp = (
        "<p><strong>How to read:</strong> Each panel is one matched pre/post pair. "
        "<strong>Blue</strong> = Section A (MQ), <strong>gold</strong> = Section B (DD). "
        "Lines connect section <strong>means</strong> from pre-video to post-video; <strong>vertical bars</strong> at each point are ±1 <em>sample</em> SD (spread within that section at that time).</p>"
        "<p>MQ and DD are drawn with a small horizontal offset so the two lines do not sit on top of each other. Survey Likert scale −2 … +2 — not Section&nbsp;3 quiz keys.</p>"
    )

    fig_post_likert = figure_likert_post_video_feedback()
    post_likert_interp = (
        "<p><strong>How to read:</strong> <strong>Four strips</strong> = four separate post-video questions. Each strip repeats the same two-bar pattern (MQ then DD).</p>"
        "<p>Same −2 … +2 scale as Fig.&nbsp;3. Exploratory MQ vs DD p-values land in Numeric recap.</p>"
    )

    qualitative_block = qualitative_essay_summary_html(n_mq, n_dd)

    pre_tb, post_tb = likert_table_sections()

    stem_name = html_mod.escape(
        bqv.FULL_NAMES[weakest][:96] + ("…" if len(bqv.FULL_NAMES[weakest]) > 96 else "")
    )
    bullets = (
        f"<li>Softest pooled stem right now is <strong>3{bqv.LETTER[weakest]}</strong> "
        f"({stem_name}) at roughly <strong>{weakest_pct:.1f}%</strong> keyed — pair Fig.&nbsp;2 with Fig.&nbsp;5 (gap ranking) when planning reviews.</li>"
        + f"<li>About <strong>{pct6:.1f}%</strong> of exports keyed <strong>6/6</strong> stems; roughly <strong>{pct_le4:.1f}%</strong> keyed at tally 4/6 or below (from keyed tallies summarized in exports—no tally histogram in this briefing).</li>"
        + "<li>Widest spread below the strongest stem is summarized in Fig.&nbsp;5 — use it alongside the narrative mixes (Figs. 6–8) for misconception drill-down.</li>"
    )

    gap_interp_fixed = (
        "<strong>What this shows:</strong> Stems sorted by pooled gap beneath the strongest item (easiest keyed ≈ "
        f"<strong>{gap_ins['easiest_pool_pct']:.1f}%</strong>). "
        f"<strong>Takeaway:</strong> Largest gap corresponds to stem <strong>3{bqv.LETTER[gid]}</strong> — revisit that concept with examples before low-stakes follow-up."
    )

    doc = (
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Organic Chemistry Video Quiz — Data Summary</title>
  <script charset="utf-8" src="{PLOTLY_CDN}"></script>
  <style>
"""
        + REPORT_CSS
        + f"""  </style>
</head>
<body class="quiz-report">
  <div class="report-shell">
    <article class="report-article">
      <h1>Organic Chemistry Video Quiz — Student Data Summary</h1>

      <p class="lede">
        Snapshot from anonymized exports: Section A <strong>(MQ)</strong> <strong>n = {n_mq}</strong>; Section B <strong>(DD / CHEM14BE)</strong> <strong>n = {n_dd}</strong> (pooled <strong>n = {n_all}</strong>).
        Interactive Plotly charts (hover traces). <strong>Results follow the briefing outline:</strong> watch time → keyed Section&nbsp;3 (table + per-stem rates) → paired pre/post survey → post-video Likert → qualitative uptake → optional gap/distractor views.
        <strong>Stem narratives</strong> live in shaded boxes ahead of pooled/MQ/DD stacked bars — <a href="#stem-narratives">jump to Figs.&nbsp;6a–f, 7a–f, 8a–f</a>.</p>

      <h2>Outline — results track</h2>
      <p class="subsection-lede">Same sequence discussed for stakeholder review: (<strong>#6</strong>) watch exposure → (<strong>#3</strong>) chemistry content keyed table then first graph → (<strong>#1–2</strong>) pre/post paired means → (<strong>#4</strong>) post-video feedback Likerts → (<strong>#5</strong>) qualitative uptake. No tally histogram.</p>

      <h3>(Meeting #6)&nbsp;&nbsp;Watch time</h3>
      <figure class="figure-block">
        <span class="tag">Fig. 1</span>
{_interpret(watch_interp)}
{plotly_chart_html(fig_watch, "plotly-watch")}
        <figcaption>Percent within each LMS import; percentages sum to each cohort’s class size (not pooled across sections).</figcaption>
      </figure>

      <h3>(Meeting #3)&nbsp;&nbsp;Chemistry content knowledge (Section&nbsp;3 — keyed)</h3>
      <table class="data-table"><thead><tr>
        <th>Item</th><th>Topic</th><th>Section A</th><th>Section B</th><th>Combined</th><th>Blanks A/B</th>
      </tr></thead><tbody>
{html_section3_table_rows()}
      </tbody></table>

      <ul class="bullet-list">
{bullets}
      </ul>

      <figure class="figure-block">
        <span class="tag">Fig. 2</span>
{_interpret(stem_interpret)}
{plotly_chart_html(fig_keyed, "plotly-stem-compare")}
        <figcaption>
          First keyed graph — per-stem rates (3A–3F). Hover each cluster. Diamonds = pooled keyed rate; shaded band = nominal 90% benchmark.</figcaption>
      </figure>

      <h3>(Meeting #1–2)&nbsp;&nbsp;Pre/post paired prompts (Likert means)</h3>
      <figure class="figure-block">
        <span class="tag">Fig. 3</span>
{_interpret(paired_likert_interp)}
{plotly_chart_html(fig_paired_pre_post, "plotly-likert-paired")}
        <figcaption>Means connecting pre→post with ±SD error bars; legend below the figure.</figcaption>
      </figure>

      <h3>(Meeting #4)&nbsp;&nbsp;Post-video feedback (Likert)</h3>
      <figure class="figure-block">
        <span class="tag">Fig. 4</span>
{_interpret(post_likert_interp)}
{plotly_chart_html(fig_post_likert, "plotly-likert-post")}
        <figcaption>One subplot per post-video item; compare blue vs gold within each strip.</figcaption>
      </figure>

      <h3>(Meeting #5)&nbsp;&nbsp;Post-video qualitative (essay)</h3>
      <p class="subsection-lede">Open-ended prompts: uptake counts only below; thematic coding uses the LMS exports directly.</p>
{qualitative_block}

      <h2>Optional — keyed dispersion &amp; distractors</h2>
      <p class="subsection-lede">Supporting views if you dig past the headline outline.</p>

      <figure class="figure-block">
        <span class="tag">Fig. 5</span>
{_interpret(gap_interp_fixed)}
{plotly_chart_html(fig_gap, "plotly-gap")}
        <figcaption>Gap axis = percentage points below the easiest pooled stem.</figcaption>
      </figure>

{stem_mix_region}

      <h3>Numeric recap</h3>
      <p class="subsection-lede">Same aggregates as Figs.&nbsp;1–4; copy-friendly for decks. Bold stars in the exploratory table are informal (* <em>p</em> &lt; 0.05, ** &lt; 0.01, *** &lt; 0.001, uncorrected).</p>

{cohort_exploratory_comparison_html()}
      <h4>Watch checklist — counts</h4>
      <table class="data-table"><thead><tr><th>Export wording (truncated)</th><th>Section A count</th><th>Section B count</th></tr></thead>
      <tbody>{watch_counts_table()}</tbody></table>

      <h4>Pre-video prompts (Likert means)</h4>
      <table class="data-table"><thead><tr><th>Stem label</th><th>Section A mean</th><th>Section B mean</th></tr></thead>
      <tbody>{pre_tb}</tbody></table>

      <h4>Post-video prompts (Likert means)</h4>
      <table class="data-table"><thead><tr><th>Stem label</th><th>Section A mean</th><th>Section B mean</th></tr></thead>
      <tbody>{post_tb}</tbody></table>

      <p class="muted" style="margin-top:2rem;">Prepared programmatically · {html_mod.escape(str(OUTPUT.name))}</p>
    </article>
  </div>
</body>
</html>
"""
    )

    OUTPUT.write_text(doc, encoding="utf-8")

    print(f"wrote {OUTPUT} ({n_all} pooled rows)")
    print("  Note: bullets auto-generated — verify pedagogical wording for your syllabus.")


if __name__ == "__main__":
    main()
