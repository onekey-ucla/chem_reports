#!/usr/bin/env python3
"""Load quiz CSVs, score 3A–3F, write PNG (+ SVG for HTML) figures (UCLA brand + Section A/B labels)."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

# UCLA Identity colors (brand.ucla.edu)
UCLA_BLUE = "#2774AE"
UCLA_GOLD = "#FFD100"
UCLA_NAVY = "#005587"
UCLA_MEDIUM_BLUE = "#8BB8E8"
WHITE = "#FFFFFF"
TEXT_DIM = "#333333"

# Distractors (non-correct, non-blank)—cycle for consistent hues across stems
ALT_COLORS = ["#E8496D", "#6C5CE7", "#00A896", "#E17055", "#F7931E", "#0984E3"]

# Section labels shown on figures
LABEL_A = "Section A (MQ)"
LABEL_B = "Section B (DD)"

# Shared copy for stacked answer-type figures — keeps Fig. 4 vs 5A/5B self-explanatory.
ANSWER_MIX_SET_EXPLAIN = (
    "How to read the set: Fig. 4 = pooled MQ+DD • Fig. 5A = Section A (MQ) • Fig. 5B = Section B (DD). "
    "Each mini-panel is one stem: the full horizontal bar always sums to 100% of responders for that stem; "
    "colored patches = keyed correct vs distractors picked vs blank."
)
LEGEND_MIX_TITLE = "Segment = LMS answer (legend shared across stems; colors hash by label)"

FILES = {
    "MQ": ROOT / "MQ_Organic Chemistry Video Quiz Student Analysis Report anon.csv",
    "DD CHEM14BE": ROOT / "DD_CHEM14BE_Organic Chemistry Video Quiz Student Analysis Report_Anonymous.csv",
}

COL = {"def": 23, "wedges": 26, "bonds": 29, "where": 32, "count": 35, "coffee": 38}
ITEM_KEYS = ["def", "wedges", "bonds", "where", "count", "coffee"]
LETTER = ["A", "B", "C", "D", "E", "F"]
FULL_NAMES = [
    "Definition of organic chemistry",
    "Wedges / hashes (3D)",
    "Bonds on carbon",
    "Implicit carbons (bond-line)",
    "Atom count (structure)",
    "Coffee example (application)",
]


def normalize(s) -> str | None:
    if pd.isna(s) or str(s).strip() == "":
        return None
    s = str(s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("\xa0", " ")
    s = " ".join(s.strip().lower().split())
    return s


def strip_display(raw) -> str:
    if pd.isna(raw) or str(raw).strip() == "":
        return ""
    s = re.sub(r"<[^>]+>", "", str(raw))
    s = " ".join(s.replace("\xa0", " ").strip().split())
    return s[:52] + ("..." if len(s) > 52 else "")


def correct(label: str, raw) -> bool | None:
    n = normalize(raw)
    if n is None:
        return None
    if label == "def":
        return ("carbon-based molecule" in n or "carbon based molecule" in n) and (
            "excluding anything man-made" not in n and "living organism" not in n
        )
    if label == "wedges":
        return "stereochemistry" in n
    if label == "bonds":
        return str(raw).strip() == "4"
    if label == "where":
        return "both where" in n and "bond" in n and ("end" in n or "connect" in n)
    if label == "count":
        return "5 carbons, 10 hydrogens" in n or ("5 carbons, 10" in n)
    if label == "coffee":
        return n == "all of the above"
    return False


def wrong_label(stem: str, raw) -> str:
    d = strip_display(raw)
    return d if d else "(unparsed wrong)"


def score_matrix(df: pd.DataFrame) -> np.ndarray:
    mat = []
    for _, row in df.iterrows():
        row_scores = []
        for k in ITEM_KEYS:
            v = correct(k, row.iloc[COL[k]])
            row_scores.append(np.nan if v is None else float(v))
        mat.append(row_scores)
    return np.asarray(mat, dtype=float)


def item_stats(df):
    m = score_matrix(df)
    stats = []
    for j in range(6):
        col = m[:, j]
        ok = np.nansum(col == 1)
        bad = np.nansum(col == 0)
        denom = ok + bad
        pct = 100 * ok / denom if denom else np.nan
        stats.append({"n_ok": int(ok), "n_bad": int(bad), "pct": pct, "n_answered": denom})
    return stats


def total_distribution(df):
    m = score_matrix(df)
    scores = []
    for i in range(len(df)):
        col = m[i]
        if np.sum(~np.isnan(col)):
            scores.append(int(np.nansum(col)))
    return Counter(scores)


def stack_fractions(df: pd.DataFrame, stem_ix: int) -> tuple[list[tuple[str, float]], int]:
    """Ordered list (label, percent) summing to 100; returned n_rows for diagnostics."""
    k = ITEM_KEYS[stem_ix]
    ix = COL[k]
    counts: Counter[str] = Counter()

    for _, row in df.iterrows():
        raw = row.iloc[ix]
        chk = correct(k, raw)
        if chk is None:
            counts["No answer"] += 1
        elif chk:
            counts["Keyed correct"] += 1
        else:
            counts[wrong_label(k, raw)] += 1

    total = sum(counts.values())
    if total == 0:
        return [], 0

    wrong_parts = [(lab, counts[lab]) for lab in counts if lab not in ("Keyed correct", "No answer")]
    wrong_parts.sort(key=lambda z: (-z[1], z[0]))

    ordered_labels: list[str] = []
    if "Keyed correct" in counts:
        ordered_labels.append("Keyed correct")
    ordered_labels.extend([w[0] for w in wrong_parts])
    if "No answer" in counts:
        ordered_labels.append("No answer")

    frac = [(lab, 100.0 * counts[lab] / total) for lab in ordered_labels]
    return frac, total


def color_for_segment(lab: str) -> str:
    if lab == "Keyed correct":
        return UCLA_BLUE
    if lab == "No answer":
        return "#9E9E9E"
    if "(blank)" in lab:
        return "#BDBDBD"
    sm = sum(ord(c) * (i + 11) for i, c in enumerate(lab[:120]))
    return ALT_COLORS[sm % len(ALT_COLORS)]


def plot_stacked_horizontal(
    ax,
    fracs: list[tuple[str, float]],
    show_pct_labels: bool = True,
    ycen: float = 0.0,
    bar_height: float = 0.65,
) -> None:
    left = 0.0
    for lab, pct in fracs:
        color = color_for_segment(lab)
        ax.barh(ycen, pct, left=left, height=bar_height, color=color, edgecolor=UCLA_NAVY, linewidth=0.35)
        if show_pct_labels and pct >= 6:
            txt_color = WHITE if (lab == "Keyed correct" or pct >= 16) else TEXT_DIM
            ax.text(
                left + pct / 2,
                ycen,
                f"{pct:.0f}%",
                ha="center",
                va="center",
                fontsize=7.5,
                color=txt_color,
                clip_on=True,
                fontweight="bold" if pct >= 12 else "normal",
            )
        left += pct
    ax.set_xlim(0, 100)
    ax.set_ylim(ycen - bar_height / 2 - 0.05, ycen + bar_height / 2 + 0.05)
    ax.set_yticks([])
    ax.set_xticks(np.arange(0, 101, 20))


def legend_ordered_labels(seen: set[str]) -> list[str]:
    rest = sorted([z for z in seen if z not in ("Keyed correct", "No answer")])
    out: list[str] = []
    if "Keyed correct" in seen:
        out.append("Keyed correct")
    out.extend(rest)
    if "No answer" in seen:
        out.append("No answer")
    return out


def legend_patches_sample(used_labels: set[str]) -> list[mpatches.Patch]:
    patches = []
    for lab in legend_ordered_labels(used_labels):
        disp = lab if len(lab) <= 90 else lab[:87] + "…"
        patches.append(mpatches.Patch(color=color_for_segment(lab), label=disp, ec=UCLA_NAVY, lw=0.3))
    return patches


def likert_num(value) -> float:
    """Map Likert label to −2 … +2."""
    if pd.isna(value) or str(value).strip() == "":
        return np.nan
    t = str(value).strip().lower()
    pairs = (
        ("strongly disagree", -2.0),
        ("disagree", -1.0),
        ("neutral", 0.0),
        ("agree", 1.0),
        ("strongly agree", 2.0),
    )
    for k, v in pairs:
        if t == k:
            return v
    return np.nan


def watch_answer_counter(df: pd.DataFrame) -> Counter[str]:
    """Count each distinct watch-time checklist response (same strings as LMS export). Column 53."""
    ctr: Counter[str] = Counter()
    for v in df.iloc[:, 53]:
        txt = "(blank)"
        if not (pd.isna(v) or str(v).strip() == ""):
            txt = str(v).strip()
        ctr[txt] += 1
    return ctr


def canonical_watch_key_order(keys: set[str]) -> list[str]:
    """Stable order matching LMS wording priority; append any unexpected keys alphabetically."""
    priority = [
        "I watched the entire video",
        "30 seconds to 2 minutes",
        "30 seconds or less",
        "I did not watch it",
        "(blank)",
    ]
    out: list[str] = []
    for p in priority:
        if p in keys:
            out.append(p)
    for k in sorted(keys):
        if k not in out:
            out.append(k)
    return out


def watch_fractions_simple(df: pd.DataFrame) -> list[tuple[str, float]]:
    """Percent of each watch-time bucket (same strings as LMS export)."""
    ctr = watch_answer_counter(df)
    total = sum(ctr.values())
    if total == 0:
        return []
    order = canonical_watch_key_order(set(ctr.keys()))
    return [(lab, 100 * ctr[lab] / total) for lab in order]


# Readable row labels next to grouped bars + table (full LMS text in numeric table column 1).
WATCH_SHORT_LABEL_FOR_DISPLAY = {
    "I watched the entire video": "Watched entire video",
    "30 seconds to 2 minutes": "30 seconds to 2 minutes",
    "30 seconds or less": "30 seconds or less",
    "I did not watch it": "Did not watch",
    "(blank)": "Blank / no response",
}


def resolve_watch_categories(ctr_mq: Counter[str], ctr_dd: Counter[str]) -> list[str]:
    union = set(ctr_mq) | set(ctr_dd)
    return canonical_watch_key_order(union)


def apply_ucla_style():
    plt.rcParams.update(
        {
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "axes.edgecolor": TEXT_DIM,
            "axes.labelcolor": TEXT_DIM,
            "axes.titlecolor": UCLA_NAVY,
            "text.color": TEXT_DIM,
            "xtick.color": TEXT_DIM,
            "ytick.color": TEXT_DIM,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
        }
    )


def save_figure_png_and_svg(fig: plt.Figure, filename_stem: str) -> None:
    """PNG for Markdown embeds; SVG for scalable HTML report figures."""
    path = OUT / filename_stem
    kwargs = {"bbox_inches": "tight", "facecolor": WHITE}
    fig.savefig(path.with_suffix(".png"), **kwargs)
    fig.savefig(path.with_suffix(".svg"), format="svg", **kwargs)


def plot_fig1_fixed_order():
    """3A→3F order (not difficulty-sorted)."""
    mq = pd.read_csv(FILES["MQ"], dtype=str)
    dd = pd.read_csv(FILES["DD CHEM14BE"], dtype=str)
    merged = pd.concat([mq, dd], ignore_index=True)

    s_mq = item_stats(mq)
    s_dd = item_stats(dd)
    s_all = item_stats(merged)

    order = np.arange(6)  # quiz order A–F
    n_items = len(ITEM_KEYS)
    x = np.arange(n_items)
    w = 0.36

    apply_ucla_style()
    fig, ax = plt.subplots(figsize=(10.8, 6.1), dpi=150)

    ax.axhspan(90, 100, color=UCLA_MEDIUM_BLUE, alpha=0.25, zorder=0)
    ax.axhline(90, color=UCLA_NAVY, linestyle="--", linewidth=1.0, zorder=1)
    ax.text(n_items - 0.45, 91.2, "90% benchmark", fontsize=9, color=UCLA_NAVY, ha="right", va="bottom")

    pmq = [s_mq[i]["pct"] for i in order]
    pdd = [s_dd[i]["pct"] for i in order]
    pall = [s_all[i]["pct"] for i in order]

    short_lbl = []
    for i in order:
        short = FULL_NAMES[i].split("(")[0].strip()
        if len(short) > 28:
            short = short[:26] + "…"
        short_lbl.append(f"3{LETTER[i]}\n{short}")

    ax.bar(x - w / 2, pmq, width=w, label=LABEL_A, color=UCLA_BLUE, edgecolor=UCLA_NAVY, linewidth=0.5, zorder=2)
    ax.bar(x + w / 2, pdd, width=w, label=LABEL_B, color=UCLA_GOLD, edgecolor=UCLA_NAVY, linewidth=0.6, zorder=2)
    ax.scatter(
        x, pall, s=52, color=UCLA_NAVY, marker="D", zorder=4, label="Pooled (MQ+DD)",
        edgecolors=WHITE, linewidths=0.8,
    )

    ax.set_ylabel(
        "Keyed correct rate (% for this stem only)\n"
        "= (# correct ÷ # who answered this stem)"
        "; blank stem excluded from denominator",
        fontsize=9.9,
        color=TEXT_DIM,
        labelpad=10,
        linespacing=1.25,
    )
    ax.set_xlabel("Quiz order: stems 3A through 3F (each stem scored separately)")
    ax.set_xticks(x)
    ax.set_xticklabels(short_lbl, fontsize=8.5, linespacing=1.05)
    ax.yaxis.grid(True, linestyle=":", alpha=0.35, color="#888888", zorder=0)
    ax.set_axisbelow(True)
    y_lo, y_hi = 70.0, 101.0
    ax.set_ylim(y_lo, y_hi)
    ax.text(
        0.985,
        0.04,
        f"Vertical scale zoomed ({y_lo:.0f}–{y_hi:.0f}%) — axis does not\nstart at 0; bar heights remain standard percents.",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.1,
        color="#555555",
        linespacing=1.22,
        bbox=dict(boxstyle="round,pad=0.38", facecolor="#f8fbff", edgecolor="#c5dcea", linewidth=0.7),
        zorder=8,
    )
    ax.legend(
        bbox_to_anchor=(1.01, 0.94),
        loc="upper left",
        bbox_transform=ax.transAxes,
        borderaxespad=0,
        framealpha=0.97,
        fontsize=9,
    )

    ax.set_title(
        "Section 3: per-stem keyed performance (different from tally /6 in Fig. 2)",
        fontweight="bold",
        pad=12,
    )

    worst_i = int(np.argmin([s_all[j]["pct"] for j in range(6)]))
    worst_pct = s_all[worst_i]["pct"]
    median_others = float(np.median([s_all[j]["pct"] for j in range(6) if j != worst_i]))

    fig.text(
        0.5,
        0.02,
        (
            f"Hardest stem in this order: 3{LETTER[worst_i]} ({FULL_NAMES[worst_i]}), pooled {worst_pct:.1f}% "
            f"(median other stems ~{median_others:.0f}%). "
            "Shaded band = 90% benchmark on this same per-stem rate."
        ),
        ha="center",
        fontsize=9.5,
        color=TEXT_DIM,
        style="italic",
    )

    fig.subplots_adjust(bottom=0.22, right=0.76)
    save_figure_png_and_svg(fig, "fig1_content_by_section")
    plt.close()


def plot_fig2_total_score_story():
    """Histogram of how many of 3A–3F each student got keyed correct (0–6). Two bars per bin: Section A vs B."""

    mq = pd.read_csv(FILES["MQ"], dtype=str)
    dd = pd.read_csv(FILES["DD CHEM14BE"], dtype=str)
    merged = pd.concat([mq, dd], ignore_index=True)

    n_m, n_d, n_all = len(mq), len(dd), len(merged)
    d_mq = total_distribution(mq)
    d_dd = total_distribution(dd)
    d_all = total_distribution(merged)

    ks = np.arange(7)
    apply_ucla_style()
    with plt.rc_context(
        {
            "font.size": 14,
            "axes.titlesize": 19,
            "axes.labelsize": 16,
            "xtick.labelsize": 15,
            "ytick.labelsize": 15,
            "legend.fontsize": 14,
        }
    ):
        fig, ax = plt.subplots(figsize=(18.0, 11.25), dpi=150)

        pct_mq = np.array([100 * d_mq.get(k, 0) / n_m for k in ks])
        pct_dd = np.array([100 * d_dd.get(k, 0) / n_d for k in ks])
        pct_all = np.array([100 * d_all.get(k, 0) / n_all for k in ks])

        w = 0.38
        x0 = ks - w / 2
        x1 = ks + w / 2

        rects_a = ax.bar(x0, pct_mq, width=w, label=f"{LABEL_A}, n={n_m}", color=UCLA_BLUE, edgecolor=UCLA_NAVY, linewidth=0.6, zorder=2)
        rects_b = ax.bar(x1, pct_dd, width=w, label=f"{LABEL_B}, n={n_d}", color=UCLA_GOLD, edgecolor=UCLA_NAVY, linewidth=0.6, zorder=2)

        def safe_labels(vals: np.ndarray, thr: float = 7.5) -> list[str]:
            return [f"{v:.0f}%" if v >= thr else "" for v in vals]

        ax.bar_label(rects_a, labels=safe_labels(pct_mq), fontsize=12, padding=3, color=TEXT_DIM)
        ax.bar_label(rects_b, labels=safe_labels(pct_dd), fontsize=12, padding=3, color=TEXT_DIM)

        full_credit = pct_all[6]
        pct_5pool = pct_all[5]
        ax.axvspan(4.42, 6.58, facecolor="#000000", alpha=0.09, zorder=0)

        pooled_pct_low = 100 * sum(d_all.get(k, 0) for k in range(5)) / n_all
        pooled_line = (
            f"Pooled (all students, n={n_all}): "
            f"{full_credit:.1f}% got all six correct  •  "
            f"{pct_5pool:.1f}% missed exactly one  •  "
            f"{pooled_pct_low:.1f}% missed two or more."
        )

        fig.text(
            0.5,
            0.93,
            pooled_line,
            ha="center",
            fontsize=14,
            color="#000000",
            style="italic",
            transform=fig.transFigure,
            fontweight="normal",
        )

        ax.set_xticks(ks)
        ax.set_xticklabels([f"{int(k)}/6" for k in ks])
        ax.tick_params(axis="x", pad=10, labelsize=15)
        ax.tick_params(axis="y", labelsize=15)
        ax.set_xlabel("Keyed items answered correctly — total out of six (3A–3F)", fontsize=16, labelpad=10)
        ax.set_ylabel("Percent of students in that section with that tally", fontsize=16, labelpad=10)
        ax.set_title(
            "Students by total keyed score (histogram: two bars per tally)",
            fontweight="bold",
            pad=14,
            fontsize=19,
        )

        ymax = float(max(np.nanmax(pct_mq), np.nanmax(pct_dd))) * 1.18
        ax.set_ylim(0, min(ymax, 104))
        ax.text(
            5.5,
            ax.get_ylim()[1] * 0.92,
            "Shaded region: keyed tallies 5/6 and 6/6 only",
            ha="center",
            va="top",
            fontsize=14,
            color="#000000",
            fontweight="bold",
            zorder=5,
        )
        ax.legend(
            bbox_to_anchor=(1.015, 0.93),
            loc="upper left",
            bbox_transform=ax.transAxes,
            borderaxespad=0,
            fontsize=14,
            framealpha=0.94,
        )

        loose = pct_all[np.arange(7) <= 4].sum()
        fig.text(
            0.5,
            0.09,
            (
                "How to read: X-axis buckets are keyed tallies — 4/6 means four of six items keyed correct "
                "for that student. Bar height is the % of that section at that tally. "
                "This is different from Fig. 1 (% correct on individual stems)."
            ),
            ha="center",
            fontsize=12.5,
            color=TEXT_DIM,
            transform=fig.transFigure,
            linespacing=1.4,
        )
        fig.text(
            0.5,
            0.02,
            f"Pooled share with tally 4/6 or worse: {loose:.1f}% of all students.",
            ha="center",
            fontsize=13,
            color=TEXT_DIM,
            style="italic",
        )
        ax.grid(axis="y", linestyle=":", alpha=0.35, linewidth=0.9, color="#BBBBBB")

        fig.subplots_adjust(top=0.86, bottom=0.24, right=0.72, left=0.09)

    save_figure_png_and_svg(fig, "fig2_score_distribution")
    plt.close()


def plot_fig3_gap_below_top():
    merged = pd.concat(
        [
            pd.read_csv(FILES["MQ"], dtype=str),
            pd.read_csv(FILES["DD CHEM14BE"], dtype=str),
        ],
        ignore_index=True,
    )
    s_all = item_stats(merged)
    best = max(s["pct"] for s in s_all)
    deficits = [best - s["pct"] for s in s_all]

    apply_ucla_style()
    with plt.rc_context(
        {
            "font.size": 14,
            "axes.titlesize": 17,
            "axes.labelsize": 16,
            "xtick.labelsize": 15,
            "ytick.labelsize": 14,
        }
    ):
        fig, ax = plt.subplots(figsize=(17.5, 10.5), dpi=150)

        order = np.argsort(deficits)[::-1]
        d_sorted = [deficits[i] for i in order]
        max_def = max(d_sorted)

        colors_b = [UCLA_GOLD if abs(d - max_def) < 1e-6 else UCLA_BLUE for d in d_sorted]
        y_pos = np.arange(6)
        bars = ax.barh(y_pos, d_sorted, height=0.58, color=colors_b, edgecolor=UCLA_NAVY, linewidth=0.8)

        labs = []
        for idx in order:
            nm = FULL_NAMES[idx]
            if len(nm) > 52:
                nm = nm[:50] + "…"
            labs.append(f"3{LETTER[idx]}  {nm}")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labs, fontsize=14)
        ax.set_xlabel(
            (
                "Relative difficulty gap (percentage points below easiest stem) — "
                f"easiest stem pooled keyed @ {best:.1f}%"
            ),
            fontsize=15,
            labelpad=10,
        )
        ax.set_title(
            (
                "Fig. 3 — Relative difficulty ranking (pooled MQ + DD merged)\n"
                "Gap (percentage points) = easiest stem pooled keyed % minus this stem pooled keyed % "
                "(larger = harder vs best item)."
            ),
            fontweight="bold",
            pad=18,
            fontsize=17,
            linespacing=1.35,
        )

        max_d = max(d_sorted)
        ax.set_xlim(0, max_d * 1.22)
        ax.tick_params(axis="x", labelsize=15, pad=6)
        for bar, d in zip(bars, d_sorted):
            ax.text(
                d + max_d * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"-{d:.1f} pp",
                va="center",
                fontsize=12,
                color=TEXT_DIM,
            )

        fig.text(
            0.5,
            0.028,
            (
                "Relative difficulty ≈ pooled item % distance from class-best stem — not alphabetical order. "
                "Easiest stem = highest pooled keyed % among 3A–3F. Gold row = largest gap below that benchmark."
            ),
            ha="center",
            fontsize=13,
            color=TEXT_DIM,
            style="italic",
            linespacing=1.42,
            transform=fig.transFigure,
        )
        fig.subplots_adjust(bottom=0.19, top=0.88, left=0.26, right=0.94)

    save_figure_png_and_svg(fig, "fig3_pooled_by_topic")
    plt.close()


def plot_fig4_answer_mix_pooled():
    """100% stacks: keyed correct vs each distractor vs no answer."""
    merged = pd.concat(
        [
            pd.read_csv(FILES["MQ"], dtype=str),
            pd.read_csv(FILES["DD CHEM14BE"], dtype=str),
        ],
        ignore_index=True,
    )

    apply_ucla_style()
    fig, axes = plt.subplots(3, 2, figsize=(12.4, 11.8), dpi=150)
    axes = axes.flatten()
    seen = set()

    for i in range(6):
        fracs, _n = stack_fractions(merged, i)
        for lab, _p in fracs:
            seen.add(lab)

        plot_stacked_horizontal(axes[i], fracs, show_pct_labels=True)
        axes[i].set_title(f"3{LETTER[i]} — {FULL_NAMES[i]}", fontsize=10, loc="left", color=UCLA_NAVY)

    axes[4].set_xlabel("Share of pooled students (percent)")
    axes[5].set_xlabel("Share of pooled students (percent)")

    patches = legend_patches_sample(seen)
    leg = fig.legend(
        handles=patches[:14],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.024),
        bbox_transform=fig.transFigure,
        ncol=4,
        fontsize=8.1,
        framealpha=0.98,
    )
    leg.set_title(LEGEND_MIX_TITLE, prop={"size": 8.4})

    fig.suptitle(
        (
            "Fig. 4 — POOLED (MQ + DD stacked): answer mix per stem\n"
            "100% stacked bar per stem • compare Section A-only and Section B-only in Fig. 5 panels"
        ),
        fontweight="bold",
        fontsize=13,
        color=UCLA_NAVY,
        y=0.995,
    )
    fig.text(
        0.5,
        0.064,
        ANSWER_MIX_SET_EXPLAIN,
        ha="center",
        fontsize=8.95,
        color=TEXT_DIM,
        linespacing=1.4,
        transform=fig.transFigure,
        wrap=False,
    )
    fig.subplots_adjust(bottom=0.38, top=0.895, hspace=0.45, wspace=0.28, left=0.08)
    save_figure_png_and_svg(fig, "fig4_answer_mix_pooled")
    plt.close()


def survey_likert_rows() -> list[tuple[int, str, str]]:
    """Column index, short y-label, fuller description line for captions."""
    return [
        (5, "Pre: nervous about ochem", "Before video: nervous about organic chemistry"),
        (8, "Pre: excited to learn ochem", "Before video: excited to learn ochem"),
        (11, "Pre: chemistry & everyday life", "Before video: chemistry ties to everyday life"),
        (41, "Post: video introduced unfamiliar ideas", "After video: video introduced unfamiliar concepts"),
        (44, "Post: immersive format helped", "After video: immersive format helped learning"),
        (47, "Post: needed rewatches", "After video: needed to rewatch clips"),
        (56, "Post: changed how I think about ochem", "After video: changed how I think about ochem"),
    ]


def plot_fig5_answer_mix_single_cohort(df: pd.DataFrame, cohort_title: str, out_name: str) -> None:
    """Six stems in quiz order — one cohort; room for titles and legend."""
    apply_ucla_style()
    fig, axes = plt.subplots(3, 2, figsize=(12.4, 11.8), dpi=150)
    axes_flat = axes.flatten()
    seen: set[str] = set()

    for i in range(6):
        fracs, ntot = stack_fractions(df, i)
        if not fracs:
            continue
        for lab, _p in fracs:
            seen.add(lab)
        plot_stacked_horizontal(axes_flat[i], fracs, show_pct_labels=True)
        axes_flat[i].set_title(
            f"3{LETTER[i]} — {FULL_NAMES[i]}",
            fontsize=10,
            loc="left",
            color=UCLA_NAVY,
            pad=8,
        )
        axes_flat[i].set_xlabel("")

    axes_flat[4].set_xlabel("Share of respondents in cohort (percent); bars sum to 100% per stem")
    axes_flat[5].set_xlabel("Share of respondents in cohort (percent); bars sum to 100% per stem")

    patches = legend_patches_sample(seen)
    leg = fig.legend(
        handles=patches[:16],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.02),
        bbox_transform=fig.transFigure,
        ncol=3,
        fontsize=8.35,
        framealpha=0.98,
    )
    leg.set_title(LEGEND_MIX_TITLE, prop={"size": 8.4})

    region = (
        "Fig. 5 — Section A (MQ) only • pair with pooled Fig. 4"
        if cohort_title == LABEL_A
        else "Fig. 5 — Section B (DD) only • pair with pooled Fig. 4"
    )
    fig.suptitle(
        (
            f"{region} only • pair with pooled Fig. 4\n"
            f"n = {len(df)} submissions • same LMS answer labels/colors as pooled; cohort restricted before stacking"
        ),
        fontweight="bold",
        fontsize=11.8,
        color=UCLA_NAVY,
        y=0.992,
    )
    fig.text(
        0.5,
        0.062,
        ANSWER_MIX_SET_EXPLAIN,
        ha="center",
        fontsize=8.95,
        color=TEXT_DIM,
        linespacing=1.4,
        transform=fig.transFigure,
    )

    fig.subplots_adjust(bottom=0.36, top=0.875, hspace=0.55, wspace=0.3, left=0.07, right=0.97)
    save_figure_png_and_svg(fig, Path(out_name).stem)
    plt.close()


def plot_fig5_answer_mix_by_section_twofile():
    mq = pd.read_csv(FILES["MQ"], dtype=str)
    dd = pd.read_csv(FILES["DD CHEM14BE"], dtype=str)

    plot_fig5_answer_mix_single_cohort(
        mq,
        LABEL_A,
        "fig5_section_a_answer_mix.png",
    )
    plot_fig5_answer_mix_single_cohort(
        dd,
        LABEL_B,
        "fig5_section_b_answer_mix.png",
    )


def plot_fig6_likert_pre_post():
    mq = pd.read_csv(FILES["MQ"], dtype=str)
    dd = pd.read_csv(FILES["DD CHEM14BE"], dtype=str)

    rows = survey_likert_rows()

    apply_ucla_style()
    fig, ax_l = plt.subplots(figsize=(10.8, 7.2), dpi=150)

    ym = []
    ym2 = []
    counts_a = []
    counts_b = []
    for coli, _short, _long in rows:
        va = pd.to_numeric(mq.iloc[:, coli].apply(likert_num), errors="coerce")
        vb = pd.to_numeric(dd.iloc[:, coli].apply(likert_num), errors="coerce")
        ym.append(float(np.nanmean(va)))
        ym2.append(float(np.nanmean(vb)))
        counts_a.append(int(va.notna().sum()))
        counts_b.append(int(vb.notna().sum()))

    y_pos = np.arange(len(rows))
    bw = 0.34
    ax_l.barh(y_pos - bw / 2, ym, bw, label=LABEL_A, color=UCLA_BLUE, edgecolor=UCLA_NAVY, linewidth=0.5)
    ax_l.barh(y_pos + bw / 2, ym2, bw, label=LABEL_B, color=UCLA_GOLD, edgecolor=UCLA_NAVY, linewidth=0.5)

    yticklbl = []
    for (_co, _short, full_lbl), ca, cb in zip(rows, counts_a, counts_b):
        yticklbl.append(f"{full_lbl}\n(non-blank coded: MQ n={ca}, CHEM14BE n={cb})")

    ax_l.set_yticks(y_pos)
    ax_l.set_yticklabels(yticklbl, fontsize=8.6)

    ax_l.set_xlim(-2.15, 2.08)
    ax_l.axvline(0.0, color="#999999", linestyle=":", linewidth=0.95)
    ax_l.set_xlabel("Mean score (Likert −2 disagree … +2 agree)")
    ax_l.set_title(
        "Pre- and post-video attitude items (outside Section 3 multiple choice)",
        loc="left",
        fontsize=11.5,
        fontweight="bold",
        pad=12,
    )
    ax_l.legend(
        bbox_to_anchor=(1.015, 0.98),
        loc="upper left",
        bbox_transform=ax_l.transAxes,
        borderaxespad=0,
        fontsize=9,
        framealpha=0.97,
    )

    fig.text(
        0.52,
        0.015,
        (
            "Scoring: Strongly disagree = −2 … Strongly agree = +2 (neutral = 0). "
            "Left labels repeat non-blank response counts — they vary by item because blanks are omitted row-by-row."
        ),
        ha="center",
        fontsize=8.5,
        color=TEXT_DIM,
        transform=fig.transFigure,
        linespacing=1.35,
    )
    fig.suptitle(
        "Survey means — not keyed exam items — compare cohort moods on matched prompts",
        fontweight="bold",
        fontsize=12,
        color=UCLA_NAVY,
        y=0.98,
    )
    fig.subplots_adjust(left=0.40, bottom=0.12, top=0.90, right=0.70)
    save_figure_png_and_svg(fig, "fig6_likert_pre_post")
    plt.close()


def plot_fig7_watch_time_by_section():
    """Grouped horizontal bars (% of cohort per category) plus raw counts — easier than stacked 100% ribbons."""
    mq = pd.read_csv(FILES["MQ"], dtype=str)
    dd = pd.read_csv(FILES["DD CHEM14BE"], dtype=str)

    ctr_m = watch_answer_counter(mq)
    ctr_d = watch_answer_counter(dd)
    n_mq, n_dd = sum(ctr_m.values()), sum(ctr_d.values())
    categories = resolve_watch_categories(ctr_m, ctr_d)

    pct_mq: list[float] = []
    pct_dd_l: list[float] = []
    count_mq_l: list[int] = []
    count_dd_l: list[int] = []

    for cat in categories:
        ca = ctr_m.get(cat, 0)
        cb = ctr_d.get(cat, 0)
        count_mq_l.append(ca)
        count_dd_l.append(cb)
        pct_mq.append(100.0 * ca / n_mq if n_mq else 0.0)
        pct_dd_l.append(100.0 * cb / n_dd if n_dd else 0.0)

    y_idx = np.arange(len(categories), dtype=float)
    bw = 0.365

    apply_ucla_style()
    fig = plt.figure(figsize=(11.2, 9.0), dpi=150)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 0.93], left=0.11, right=0.98, top=0.88, bottom=0.06, hspace=0.44)
    ax = fig.add_subplot(gs[0])

    bars_a = ax.barh(
        y_idx - bw / 2,
        pct_mq,
        height=bw,
        label=LABEL_A,
        color=UCLA_BLUE,
        edgecolor=UCLA_NAVY,
        linewidth=0.55,
        zorder=2,
    )
    bars_b = ax.barh(
        y_idx + bw / 2,
        pct_dd_l,
        height=bw,
        label=LABEL_B,
        color=UCLA_GOLD,
        edgecolor=UCLA_NAVY,
        linewidth=0.55,
        zorder=2,
    )

    bar_max = float(
        max(
            np.max(np.asarray(pct_mq)) if pct_mq else 0.0,
            np.max(np.asarray(pct_dd_l)) if pct_dd_l else 0.0,
        )
        if pct_mq or pct_dd_l
        else 0.0
    )
    x_right_chart = float(min(max(bar_max * 1.12 + 10.0, 68.0), 118.0))
    summary_margin = float(max(22.0, min(36.0, bar_max * 0.09 + 22.0)))
    ax.set_xlim(0, x_right_chart + summary_margin)

    def label_pct_inside(bar, pct: float, *, light_blue: bool) -> None:
        wbar = bar.get_width()
        if pct < 5.8:
            return
        ymid = bar.get_y() + bar.get_height() / 2
        cx = max(wbar * 0.5, pct * 0.48)
        if pct >= 18:
            txt_color = WHITE if light_blue else UCLA_NAVY
        else:
            txt_color = TEXT_DIM
        ax.text(
            cx,
            ymid,
            f"{pct:.0f}%",
            ha="center",
            va="center",
            fontsize=8.2,
            fontweight="bold",
            color=txt_color,
            zorder=3,
        )

    for bar, pct in zip(bars_a.patches, pct_mq):
        label_pct_inside(bar, pct, light_blue=True)
    for bar, pct in zip(bars_b.patches, pct_dd_l):
        label_pct_inside(bar, pct, light_blue=False)

    txt_x = x_right_chart + summary_margin - 6.8
    for yi, nm, nb, pm, pn in zip(y_idx, count_mq_l, count_dd_l, pct_mq, pct_dd_l):
        ax.text(
            txt_x,
            float(yi),
            f"n MQ = {nm} ({pm:.1f}% of MQ)\nn DD = {nb} ({pn:.1f}% of DD)",
            fontsize=7.95,
            color=TEXT_DIM,
            va="center",
            ha="right",
            linespacing=1.06,
            zorder=6,
            clip_on=False,
        )

    yticks = []
    for c in categories:
        yticks.append(WATCH_SHORT_LABEL_FOR_DISPLAY.get(c, c[:48] + ("…" if len(c) > 48 else "")))

    ax.set_yticks(y_idx)
    ax.set_yticklabels(yticks, fontsize=9.85)
    ax.invert_yaxis()
    ax.set_xlabel("Percent of each cohort answering this LMS option (stacked totals = cohort size)")
    xmax_axis = ax.get_xlim()[1]
    ax.set_xticks([t for t in np.arange(0.0, 121.0, 20.0) if t <= xmax_axis + 1e-6])
    ax.grid(axis="x", linestyle=":", alpha=0.4, linewidth=0.85, color="#BBBBBB", zorder=0)
    ax.legend(
        bbox_to_anchor=(1.02, 0.93),
        loc="upper left",
        bbox_transform=ax.transAxes,
        borderaxespad=0,
        fontsize=9.6,
        framealpha=0.97,
        ncol=1,
    )
    ax.set_axisbelow(False)

    fig.suptitle(
        (
            "Video watch exposure — same checklist item for both cohorts\n"
            f"MQ submits n={n_mq}; CHEM14BE submits n={n_dd}. Blue bars = Section A (MQ). Gold bars = Section B (DD)."
        ),
        fontsize=11.75,
        fontweight="bold",
        color=UCLA_NAVY,
        y=0.99,
        ha="center",
    )
    ax.set_title(
        "Percent labels sit inside colored bars where space allows (≥~6%); right-hand column repeats raw totals and percentages for each LMS row.",
        fontsize=9.05,
        color=TEXT_DIM,
        pad=12,
        loc="center",
        style="italic",
    )

    tbl_ax = fig.add_subplot(gs[1])
    tbl_ax.axis("off")

    tbl_rows: list[list[str]] = []
    for cat, nm, cm, pctm, pct_d in zip(categories, count_mq_l, count_dd_l, pct_mq, pct_dd_l):
        lbl = cat if len(cat) <= 85 else cat[:82] + "…"
        tbl_rows.append([lbl, str(nm), f"{pctm:.1f}%", str(cm), f"{pct_d:.1f}%"])

    tbl = tbl_ax.table(
        cellText=tbl_rows,
        colLabels=["LMS wording (survey export checklist)", "Count MQ", "% of MQ", "Count CHEM14BE", "% of CHEM14BE"],
        loc="upper center",
        cellLoc="left",
        colLoc="center",
        bbox=[0.01, 0.15, 0.988, 0.96],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.85)
    tbl.scale(1.02, 1.72)

    for idx, cell in tbl.get_celld().items():
        row_ix, col_ix = idx
        if row_ix == 0:
            cell.set_facecolor(UCLA_MEDIUM_BLUE)
            cell.set_alpha(0.4)
            t = cell.get_text()
            t.set_fontweight("bold")
            t.set_fontsize(8.6)
            continue
        if col_ix >= 1:
            cell.get_text().set_horizontalalignment("right")

    fig.text(
        0.5,
        0.032,
        "Bottom table echoes the LMS export strings verbatim and matches the chart row order (top-down = full watch downward).",
        ha="center",
        fontsize=8.5,
        color=TEXT_DIM,
        style="italic",
        transform=fig.transFigure,
    )
    fig.subplots_adjust(right=0.62)

    save_figure_png_and_svg(fig, "fig7_watch_time_by_section")
    plt.close()


if __name__ == "__main__":
    apply_ucla_style()
    plot_fig1_fixed_order()
    plot_fig2_total_score_story()
    plot_fig3_gap_below_top()
    plot_fig4_answer_mix_pooled()
    plot_fig5_answer_mix_by_section_twofile()
    plot_fig6_likert_pre_post()
    plot_fig7_watch_time_by_section()
    print("Wrote PNG + SVG to", OUT)
    r = subprocess.run(
        [sys.executable, str(ROOT / "build_html_report.py")],
        cwd=str(ROOT),
        check=False,
    )
    if r.returncode != 0:
        print("warning: build_html_report.py failed; inline HTML report not updated.", file=sys.stderr)
