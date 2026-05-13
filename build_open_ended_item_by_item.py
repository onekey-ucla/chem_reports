#!/usr/bin/env python3
"""Emit Open_Ended_Responses_Item_by_Item.md — one heading per LMS essay submission."""

from __future__ import annotations

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main() -> None:
    essays = {}
    with open(BASE / "open_ended_essay_only.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r["cohort"], int(r["submission_n"]))
            essays[key] = r

    codes: dict[tuple[str, int], dict] = {}
    slim = BASE / "open_ended_essay_theme_codes_all_submissions_slim.csv"
    if slim.exists():
        with open(slim, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                codes[(r["cohort"], int(r["submission_n"]))] = r

    lines = [
        "# Open-ended responses — item by item",
        "",
        'Each block is **one LMS submission** (essay prompt: “What stood out to you most about this video…”). '
        'If the export has no essay text (`essay_blank` in CSV), it is labeled **Blank: yes**. '
        'Otherwise the full reply is verbatim from the anonymized export (HTML stripped).',
        "",
        "*Theme codes* are automated flags from `extract_theme_codes.py` (`themes_flagged`); treat as illustrative.",
        "",
        "---",
        "",
    ]

    order = sorted(essays.keys(), key=lambda x: (0 if x[0] == "MQ" else 1, x[1]))

    for i, key in enumerate(order, start=1):
        co, n = key
        row = essays[key]
        text = (row.get("essay") or "").strip()
        blank = not text
        c = codes.get(key, {})
        tf = (c.get("themes_flagged") or "").strip() or "—"
        manual = c.get("needs_manual_review", "0")

        lines.append(f"## Item {i}: [{co}] submission `{n}`")
        lines.append("")
        lines.append(f"- **Submitted (UTC):** {row.get('submitted_utc', '')}")
        lines.append(f"- **Blank:** {'yes' if blank else 'no'}")
        if not blank:
            lines.append(f"- **Approx. characters:** {len(text)}")
        lines.append(f"- **Automated themes:** `{tf}`")
        if manual == "1" and not blank:
            lines.append(
                "- **Note:** `needs_manual_review` — no keyword pattern fired; consider hand coding."
            )
        lines.append("")
        lines.append("*(No text submitted.)*" if blank else text)
        lines.append("")
        lines.append("---")
        lines.append("")

    path = BASE / "Open_Ended_Responses_Item_by_Item.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path} ({len(order)} submissions)")


if __name__ == "__main__":
    main()
