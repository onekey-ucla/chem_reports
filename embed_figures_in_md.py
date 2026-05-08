#!/usr/bin/env python3
"""
Replace the visualizations section in Organic_Chemistry_Video_Quiz_Report_Casey.md
with PNGs embedded as data: URIs so images render inside the markdown without external paths.

Run after: python3 build_quiz_visualizations.py
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD = ROOT / "Organic_Chemistry_Video_Quiz_Report_Casey.md"
FIGURES = ROOT / "figures"


def main() -> None:
    text = MD.read_text(encoding="utf-8")

    packs = [
        (
            "### Keyed performance (quiz order 3A–3F and totals)\n\n",
            [
                (
                    "Fig. 1",
                    "Per-stem keyed rate for 3A–3F (% with correct keyed answer among students who answered that stem; blanks omitted). Separate from Fig. 2 tally 0/6…6/6.",
                    "Y-axis is zoomed 70–101% (callout explains); pooled diamonds use the same numerator/denominator rule for MQ+DD combined.",
                    "fig1_content_by_section.png",
                ),
                (
                    "Fig. 2",
                    "Keyed tally per student shown as fractions 0/6 … 6/6 on the horizontal axis — two cohort bars per tally.",
                    "X-axis tallies 0/6…6/6; pooled headline and shaded 5/6–6/6 column in black; not per-stem percentages (Fig. 1).",
                    "fig2_score_distribution.png",
                ),
                (
                    "Fig. 3",
                    "Relative difficulty (pooled): horizontal bars = percentage points BELOW the single easiest keyed stem.",
                    "Not raw item % — gap is (easiest stem pooled keyed %) − (this stem pooled %). Sorted by gap; gold marks largest deficit.",
                    "fig3_pooled_by_topic.png",
                ),
            ],
        ),
        (
            "### Keyed stems — wrong options and blanks\n\n",
            [
                (
                    "Fig. 4",
                    "Pooled MQ+DD: 100% stacked answer mix per stem (same scales as Fig. 5A/5B; legend title explains patches).",
                    "Footer paragraph maps Fig. 4 → pooled · Fig. 5A MQ · Fig. 5B DD; full bar width = cohort slice for that stem.",
                    "fig4_answer_mix_pooled.png",
                ),
                (
                    "Fig. 5",
                    "Section A (MQ) only — mirrored layout to pooled Fig. 4; answer-mix attribution within this export.",
                    "Use next figure for Section B; compare both to Fig. 4 to spot cohort-specific drift in distractors.",
                    "fig5_section_a_answer_mix.png",
                ),
                (
                    "Fig. 6",
                    "Section B (DD CHEM14BE export) — same plotting rules as previous Fig. 5 with MQ.",
                    "Paired cohort deep-dive for wrong-option spectra after reading pooled Fig. 4.",
                    "fig5_section_b_answer_mix.png",
                ),
            ],
        ),
        (
            "### Attitudes & watch time (not Section 3 multiple choice)\n\n",
            [
                (
                    "Fig. 7",
                    "Pre/post Likert means paired by prompt; blanks omitted from denominators.",
                    "Y-axis repeats full prompt text plus coded non-blank MQ vs CHEM14BE totals per stem.",
                    "fig6_likert_pre_post.png",
                ),
                (
                    "Fig. 8",
                    "Watch time: grouped horizontal bars (Section A vs Section B) plus right-hand n / % and numeric table with full LMS strings.",
                    "Replaces the old single-row 100% stacks; each row is one checklist option and bar length is % of that cohort who chose it (not a strip within one bar).",
                    "fig7_watch_time_by_section.png",
                ),
            ],
        ),
    ]

    chunks: list[str] = []

    chunks.append(
        "### Visualizations (embedded PNGs)\n\n"
        "Figures encode UCLA Blue (#2774AE) vs Gold (#FFD100) with UCLA navy edging for stacked palettes. "
        "(See [UCLA color palette](https://brand.ucla.edu/identity/colors).)\n\n"
    )

    for heading, trio in packs:
        body: list[str] = [heading]
        for fig_tag, alt, caption, fname in trio:
            png = FIGURES / fname
            if not png.is_file():
                raise FileNotFoundError(png)
            b64 = base64.b64encode(png.read_bytes()).decode("ascii")
            uri = f"data:image/png;base64,{b64}"
            body.append(f"**{fig_tag} — {alt}**\n\n![{fig_tag} — {alt}]({uri})\n\n*{caption}*\n")

        chunks.append("\n".join(body))

    section = "".join(chunks)
    section += "\nRebuild charts plus inline previews: `python3 build_quiz_visualizations.py && python3 embed_figures_in_md.py`.\n"

    pattern = r"### Visualizations[^\n]*\n\n.*?---\n\n## Section 3 \(3A–3F\)"
    if not re.search(pattern, text, re.DOTALL):
        raise SystemExit(
            "Could not find visualizations block. Expected '### Visualizations …' "
            "through '## Section 3 (3A–3F)'."
        )

    out = re.sub(pattern, section + "\n---\n\n## Section 3 (3A–3F)", text, count=1, flags=re.DOTALL)
    MD.write_text(out, encoding="utf-8")
    print(f"Updated {MD} ({len(out) // 1024} KB)")


if __name__ == "__main__":
    main()
