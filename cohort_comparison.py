"""Exploratory two-cohort contrasts (MQ vs DD) for the HTML report — not adjusted for multiple testing."""

from __future__ import annotations

import html as html_mod

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu

import build_quiz_visualizations as bqv


def _fmt_p(p: float) -> str:
    if p != p or p < 0:  # nan
        return "—"
    if p < 1e-4:
        return "<0.0001"
    return f"{p:.4f}"


def _star(p: float) -> str:
    if p != p:
        return ""
    if p < 0.001:
        return " ***"
    if p < 0.01:
        return " **"
    if p < 0.05:
        return " *"
    return ""


def likert_series(df: pd.DataFrame, coli: int) -> np.ndarray:
    s = pd.to_numeric(df.iloc[:, coli].apply(bqv.likert_num), errors="coerce").to_numpy(dtype=float)
    return s[~np.isnan(s)]


def mann_whitney_two_sided(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return float("nan")
    try:
        r = mannwhitneyu(a, b, alternative="two-sided")
        return float(r.pvalue)
    except ValueError:
        return float("nan")


def survey_likert_comparison_rows() -> list[tuple[str, float, float, float, float]]:
    """(short label, mq_mean, dd_mean, diff_mq_minus_dd, mw_p)."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    out: list[tuple[str, float, float, float, float]] = []
    for coli, short, _full in bqv.survey_likert_rows():
        va, vb = likert_series(mq, coli), likert_series(dd, coli)
        ma, mb = float(np.mean(va)), float(np.mean(vb))
        p = mann_whitney_two_sided(va, vb)
        out.append((short, ma, mb, ma - mb, p))
    return out


def keyed_stem_comparison_rows() -> list[tuple[str, float, float, float, float]]:
    """(stem id, mq_pct, dd_pct, diff_pp, fisher_p)."""
    mq = pd.read_csv(bqv.FILES["MQ"], dtype=str)
    dd = pd.read_csv(bqv.FILES["DD CHEM14BE"], dtype=str)
    sm, sd = bqv.item_stats(mq), bqv.item_stats(dd)
    out: list[tuple[str, float, float, float, float]] = []
    for j in range(6):
        am, bm = sm[j]["n_ok"], sm[j]["n_bad"]
        ad, bd = sd[j]["n_ok"], sd[j]["n_bad"]
        pm = 100.0 * am / (am + bm) if (am + bm) else float("nan")
        pd_ = 100.0 * ad / (ad + bd) if (ad + bd) else float("nan")
        try:
            _, p = fisher_exact([[am, bm], [ad, bd]])
        except ValueError:
            p = float("nan")
        out.append((f"3{bqv.LETTER[j]}", pm, pd_, pm - pd_, float(p)))
    return out


def cohort_exploratory_comparison_html() -> str:
    """HTML tables: survey (MW) + keyed stems (Fisher)."""
    lik_rows = survey_likert_comparison_rows()
    key_rows = keyed_stem_comparison_rows()

    lik_tr = "".join(
        f"<tr><td>{html_mod.escape(short)}</td>"
        f"<td>{ma:+.3f}</td><td>{mb:+.3f}</td><td>{d:+.3f}</td>"
        f"<td>{_fmt_p(p)}{_star(p)}</td></tr>"
        for short, ma, mb, d, p in lik_rows
    )

    key_tr = "".join(
        f"<tr><td>{html_mod.escape(stem)}</td>"
        f"<td>{pm:.1f}%</td><td>{pdd:.1f}%</td><td>{dpp:+.1f}</td>"
        f"<td>{_fmt_p(p)}{_star(p)}</td></tr>"
        for stem, pm, pdd, dpp, p in key_rows
    )

    foot = (
        "Likert scale coded −2 … +2 in exports. Mann–Whitney U (two-sided) ranks individual responses. "
        "Keyed stems: Fisher’s exact test on 2×2 counts (keyed vs not, among students who answered that stem). "
        "Uncorrected p-values — many tests; exploratory only."
    )

    return f"""      <h4>Exploratory MQ vs DD contrasts</h4>
      <p class="subsection-lede fine-print">{html_mod.escape(foot)}</p>
      <table class="data-table"><thead><tr>
        <th>Survey item (Likert)</th><th>MQ mean</th><th>DD mean</th><th>MQ−DD</th><th>MW <em>p</em></th>
      </tr></thead><tbody>
{lik_tr}
      </tbody></table>
      <table class="data-table" style="margin-top:1rem;"><thead><tr>
        <th>Keyed stem</th><th>MQ % keyed</th><th>DD % keyed</th><th>Δ pp</th><th>Fisher <em>p</em></th>
      </tr></thead><tbody>
{key_tr}
      </tbody></table>"""
