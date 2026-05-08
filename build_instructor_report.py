#!/usr/bin/env python3
"""
Instructor-facing report — Section A (MQ) vs Section B (DD), interactive Plotly visuals + interpretation.

Charts: Plotly.js (CDN) embedded from Python; legends sit below traces (see plotly_quiz_figures._base_layout).
Run: python3 build_instructor_report.py
"""

from __future__ import annotations

import html as html_mod
from pathlib import Path

import numpy as np
import pandas as pd

import build_quiz_visualizations as bqv
from build_html_report import plotly_chart_html, render_stem_answer_series
from plotly_quiz_figures import (
    figure_compare_stems,
    figure_likert_paired_pre_post,
    figure_likert_post_video_feedback,
    figure_single_cohort_stems,
    figure_watch_compare,
)

from report_styles import REPORT_CSS

ROOT = Path(__file__).resolve().parent
OUT_HTML = ROOT / "Instructor_Report.html"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.30.1.min.js"


def interp(text: str) -> str:
    return f'<div class="interpret">{text}</div>\n'


def cohort_story(df: pd.DataFrame, cohort_name: str) -> tuple[str, int, float, int, float]:
    """Bullets-ready stats."""
    stats = [bqv.item_stats(df)[j]["pct"] for j in range(6)]
    worst = int(np.argmin(stats))
    best = int(np.argmax(stats))
    dist = bqv.total_distribution(df)
    n = len(df)
    pct_full = 100 * dist.get(6, 0) / n if n else 0
    m = bqv.score_matrix(df)
    tally_means = []
    for i in range(len(df)):
        row = m[i]
        if np.sum(~np.isnan(row)):
            tally_means.append(float(np.nansum(row)))
    mean_tally = float(np.mean(tally_means)) if tally_means else float("nan")

    bullets = (
        f"<strong>Snapshot — {cohort_name}</strong><br>"
        f"Exports <em>n = {n}</em>. Mean tally ≈ <strong>{mean_tally:.2f}/6</strong>; "
        f"<strong>{pct_full:.1f}%</strong> keyed all six. "
        f"Hot/cold stems: highest <strong>3{bqv.LETTER[best]}</strong> ({stats[best]:.1f}%), "
        f"lowest <strong>3{bqv.LETTER[worst]}</strong> ({stats[worst]:.1f}%)."
    )
    return bullets, worst, stats[worst], best, stats[best]


def main() -> None:
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    n_mq, n_dd = len(mq), len(dd)

    mq_story, mq_w_i, mq_w_pct, mq_b_i, mq_b_pct = cohort_story(mq, "Section A (MQ)")
    dd_story, dd_w_i, dd_w_pct, dd_b_i, dd_b_pct = cohort_story(dd, "Section B (DD / CHEM14BE)")
    mq_dd_delta = np.array([bqv.item_stats(mq)[j]["pct"] - bqv.item_stats(dd)[j]["pct"] for j in range(6)])
    focus_i = int(np.argmax(np.abs(mq_dd_delta)))

    comparative = interp(
        "<strong>Teaching read-across MQ vs DD:</strong><br>"
        "The first chart reproduces pooled comparison (always start class debrief here). Blue vs gold bars surface roster-level differences; "
        "hover to quote exact numbers. "
        f"The largest absolute gap this term sits on <strong>3{bqv.LETTER[focus_i]}</strong> "
        f"(MQ − DD ≈ <strong>{mq_dd_delta[focus_i]:+.1f}</strong> percentage points) — dig into that stem’s distractors in the stacks below. "
        "Single-cohort bars remove cross-talk so you can script section-specific warm-ups."
    )

    fig_cmp, _ = figure_compare_stems()

    mq_mix_html = (
        '<section class="mix-bundle" id="stem-narratives-mq">\n'
        '<h3>MQ · answer mixtures (per stem)</h3>'
        '<p class="subsection-lede">Same layout as stakeholder Figs. 7<span class="subs">a</span>–<span class="subs">f</span>; each shaded <strong>narrative</strong> box lists keyed rule, KPI chips, then wrong LMS options ahead of the bar.</p>'
        + render_stem_answer_series(mq, "7", pooled=False, cohort_note=f"MQ only (n = {n_mq})")
        + "</section>\n"
    )

    mq_section = "".join(
        [
            interp(
                mq_story + "<br><strong>Use charts below:</strong> per-stem keyed rates, then six narrative + distractor stacks."
            ),
            interp(
                "<strong>Recall:</strong> each percentage conditions on MQ exports only."
            ),
            '<figure class="figure-block">\n<span class="tag">MQ · stems</span>\n'
            + plotly_chart_html(
                figure_single_cohort_stems(mq, "MQ: keyed rates on each stem", bqv.UCLA_BLUE),
                "mq-stems",
            )
            + "<figcaption>Isolate MQ before blaming cross-section pooling.</figcaption></figure>",
            mq_mix_html,
        ]
    )

    dd_mix_html = (
        '<section class="mix-bundle" id="stem-narratives-dd">\n'
        '<h3>DD · answer mixtures (per stem)</h3>'
        '<p class="subsection-lede">Parallel to stakeholder Figs. 8<span class="subs">a</span>–<span class="subs">f</span> — same shaded narrative boxes as the MQ mixes.</p>'
        + render_stem_answer_series(dd, "8", pooled=False, cohort_note=f"DD only (n = {n_dd})")
        + "</section>\n"
    )

    dd_section = "".join(
        [
            interp(dd_story),
            '<figure class="figure-block">\n<span class="tag">DD · stems</span>\n'
            + plotly_chart_html(
                figure_single_cohort_stems(dd, "DD (CHEM14BE): keyed rates on each stem", bqv.UCLA_GOLD),
                "dd-stems",
            )
            + "<figcaption>Same layout as MQ for apples-to-apples debriefs.</figcaption></figure>",
            dd_mix_html,
        ]
    )

    shared = "".join(
        [
            interp(
                "<strong>Signals outside Section 3:</strong><br>"
                "Order matches the stakeholder briefing: declared watch exposure first, paired pre/post survey means, post-video Likert block. "
                "Hover traces; legends may sit beneath charts or beside dense mix dashboards."
            ),
            '<figure class="figure-block">\n<span class="tag">Watch-time checklist</span>\n'
            + plotly_chart_html(figure_watch_compare(), "inst-watch")
            + "</figure>",
            '<figure class="figure-block">\n<span class="tag">Pre/post paired prompts</span>\n'
            + plotly_chart_html(figure_likert_paired_pre_post(), "inst-likert-paired")
            + "</figure>",
            '<figure class="figure-block">\n<span class="tag">Post-video Likert</span>\n'
            + plotly_chart_html(figure_likert_post_video_feedback(), "inst-likert-post")
            + "</figure>",
        ]
    )

    doc = (
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Instructor Report — Organic Chemistry Video Quiz</title>
  <script charset="utf-8" src="{PLOTLY_CDN}"></script>
  <style>
"""
        + REPORT_CSS
        + f"""  </style>
</head>
<body class="quiz-report">
  <div class="report-shell">
    <article class="report-article">
      <h1>Instructor playbook — Sections A&nbsp;&amp;&nbsp;B</h1>

      <p class="report-instructor-lede">
        Interactive dashboards use the same anonymized LMS exports as the stakeholder report. Hover traces; legends sit below canvases.<br/>
        MQ <code>{html_mod.escape(Path(bqv.FILES["MQ"]).name)}</code> (<strong>n = {n_mq}</strong>);
        DD <code>{html_mod.escape(Path(bqv.FILES["DD CHEM14BE"]).name)}</code> (<strong>n = {n_dd}</strong>).<br/>
        <strong>Stem narratives:</strong> each shaded box (Keyed rule → KPIs → verbatim wrong LMS options before the stacked bar) lives in <a href="#stem-narratives-mq">MQ mixes</a> and <a href="#stem-narratives-dd">DD mixes</a>.
      </p>

      <section class="report-section">
        <h2>Compare cohorts first</h2>
{comparative}
        <figure class="figure-block">
          <span class="tag">Pooled keyed detail</span>
{plotly_chart_html(fig_cmp, "inst-cmp")}
          <figcaption>Same chart as stakeholder Fig.&nbsp;2 (per-stem keyed rates) — start every debrief here before drilling into MQ or DD stacks.</figcaption>
        </figure>
      </section>

      <section class="report-section">
        <h2>MQ-only lane</h2>
{mq_section}
      </section>

      <section class="report-section">
        <h2>DD-only lane</h2>
{dd_section}
      </section>

      <section class="report-section">
        <h2>Cross-cutting survey cues</h2>
{shared}
      </section>

      <p class="muted" style="margin-top: 2rem;">Regenerate with <code>python3 build_instructor_report.py</code> when exports refresh.</p>
    </article>
  </div>
</body>
</html>
"""
    )
    OUT_HTML.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
