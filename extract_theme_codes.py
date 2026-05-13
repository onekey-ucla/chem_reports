#!/usr/bin/env python3
"""
Deductive keyword coding for open-ended video reflections (six themes).
Outputs wide CSV (one row per submission), slim CSV (no essay text), long CSV
(one row per theme hit), and optionally includes blank essays (all submissions).

Themes align with Thematic_Analysis_Open_Ended_Essays.md (interpretive memo).
Automated codes are supplementary; rows with needs_manual_review=1 need human eyes.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

PATTERNS = {
    "T1_everyday_coffee": re.compile(
        r"coffee|cafe|café|everyday|every day|daily life|real[\s-]?world|mundane|real life"
        r"|application|applied to|around us|everywhere"
        r"|smell|taste|olfactory|receptor|volatile|caffeine|adenosine|barista|stimulant"
        r"|sucralose|drinking caffeine|brain\b",
        re.I,
    ),
    "T2_clarity_pace": re.compile(
        r"simple|straightforward|straight forward|easy to understand|easier to understand|clear\b|concisely|concise|digestib"
        r"|approachable|broken down|demystif|plain\b|not overwhelming|good pace|pacing|brief\b"
        r"|summarized|summarised|understandable|explained well|nice and plain|summarize"
        r"|succinct|straight to the point",
        re.I,
    ),
    "T3_visual_immersion": re.compile(
        r"\bvisual|diagram|animation|animated|graphics?|\b3d\b|three[\s-]?dimensional|immers"
        r"|moving diagram|moving visuals|\bmodels?\b|wedge|hash|hashes|stereochem"
        r"|coffee shop|cafe setting|set(?:ting)? was engaging|friendly faces"
        r"|interactive\b",
        re.I,
    ),
    "T4_affect_stigma": re.compile(
        r"intimidat|scared|scary|nervous|anxious|anxiety|fear|dread|dreading|terrified|worried|stress"
        r"|weeder|grade tanking|negative things|sterotype|stereotype|reassur|comfort|peace"
        r"|less intimidat|feel validated|acknowledg.{0,18}worries|worries about"
        r"|don't fear|do not fear|not fear|afraid\b|ease[d]?\s+(?:my|the)"
        r"|horror stories|heard.*hard|made out to be",
        re.I,
    ),
    "T5_concepts_prior": re.compile(
        r"\bcarbon\b|carbon-based|compounds? with carbon|study of carbon|implicit\s+h"
        r"|line structure|bond-line|skeletal|general chemistry|gen chem|\b14a\b|\b14b\b|14ae|14be"
        r"|definition of organic|what organic chemistry (?:is|means|was)"
        r"|wedges and hashes|hashes tell us"
        r"|shorthand|drawing(?:s)? of|structures?\s+(?:of|in)|count(?:ing)?\s+(?:the\s+)?(?:c|carbon|h|hydrogen)\b",
        re.I,
    ),
    "T6_limits_friction": re.compile(
        r"didn'?t change|did not change|nothing stood|nothing changed|nothing really stood"
        r"|did not really change|no change|not really.{0,30}(?:change|stood)"
        r"|couldn'?t find|could not find|unclear where"
        r"|did not watch fully|didn'?t watch fully|couldnt find a video"
        r"|^(?:na|n/?a)\s*$"
        r"|don'?t resonate|doesn'?t resonate|trick them|doesn'?t need to lie|dont need to lie"
        r"|doesn'?t cover what makes organic chemistry hard"
        r"|neutral about taking|\bno\b[\.\,\s]+(?:it )?didn'?t",
        re.I,
    ),
}

TMAP = [
    ("T1_everyday_coffee", "Theme 1 — Everyday anchoring (coffee / real world / sensory)"),
    ("T2_clarity_pace", "Theme 2 — Clarity / pace / digestibility"),
    ("T3_visual_immersion", "Theme 3 — Visual / multimodal / immersion"),
    ("T4_affect_stigma", "Theme 4 — Affect / fear / stigma"),
    ("T5_concepts_prior", "Theme 5 — Concepts / prior knowledge"),
    ("T6_limits_friction", "Theme 6 — Limits / skepticism / friction"),
]


def code_essay(text: str) -> dict[str, int]:
    raw = text or ""
    s = raw.strip()
    if not s:
        return {k: 0 for k in PATTERNS}
    out = {key: (1 if pat.search(s) else 0) for key, pat in PATTERNS.items()}
    if re.match(r"^na\s*$", s, re.I):
        out["T6_limits_friction"] = 1
    if len(s) < 35:
        low = s.lower()
        if low in {"volatility", "the beginning", "learning about carbon", "organic chemistry is everywhere"}:
            out["T5_concepts_prior"] = max(out["T5_concepts_prior"], 1)
        if "couldn't find" in low or "couldnt find" in low:
            out["T6_limits_friction"] = 1
        if sum(out.values()) == 0:
            if any(w in low for w in ["visual", "diagram", "animations", "models", "graphic"]):
                out["T3_visual_immersion"] = 1
            elif "coffee" in low or ("cool" in low and "chem" in low):
                out["T1_everyday_coffee"] = 1
    return out


def process_input(infile: Path) -> list[dict]:
    rows_out: list[dict] = []
    with open(infile, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            essay = row.get("essay", "") or ""
            blank = 1 if not essay.strip() else 0
            codes = code_essay(essay)
            tc = sum(codes.values())
            manual = 1 if (not blank and tc == 0) else 0
            flagged = ";".join(k for k, v in codes.items() if v)
            rec = {
                "cohort": row["cohort"],
                "submission_n": row["submission_n"],
                "submitted_utc": row["submitted_utc"],
                "essay_blank": blank,
                "essay_chars": len(essay),
                **codes,
                "theme_count": tc,
                "themes_flagged": flagged,
                "needs_manual_review": manual,
                "essay": essay,
            }
            rows_out.append(rec)
    return rows_out


def write_wide(rows: list[dict], path: Path) -> None:
    keys = [
        "cohort",
        "submission_n",
        "submitted_utc",
        "essay_blank",
        "essay_chars",
        *PATTERNS.keys(),
        "theme_count",
        "themes_flagged",
        "needs_manual_review",
        "essay",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


def write_slim(rows: list[dict], path: Path) -> None:
    keys = [k for k in rows[0].keys() if k != "essay"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in keys})


def write_long(rows: list[dict], path: Path) -> None:
    long_rows = []
    for r in rows:
        for col, label in TMAP:
            if r[col]:
                long_rows.append(
                    {
                        "cohort": r["cohort"],
                        "submission_n": r["submission_n"],
                        "submitted_utc": r["submitted_utc"],
                        "essay_blank": r["essay_blank"],
                        "theme_column": col,
                        "theme_label": label,
                        "coded": 1,
                    }
                )
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "cohort",
                "submission_n",
                "submitted_utc",
                "essay_blank",
                "theme_column",
                "theme_label",
                "coded",
            ],
        )
        w.writeheader()
        w.writerows(long_rows)


def main() -> None:
    for name_in, name_out in [
        ("open_ended_essay_only_nonempty.csv", "open_ended_essay_theme_codes.csv"),
        ("open_ended_essay_only.csv", "open_ended_essay_theme_codes_all_submissions.csv"),
    ]:
        inp = BASE / name_in
        if not inp.exists():
            continue
        rows = process_input(inp)
        wide = BASE / name_out
        write_wide(rows, wide)
        write_slim(rows, BASE / name_out.replace(".csv", "_slim.csv"))
        write_long(rows, BASE / name_out.replace(".csv", "_long.csv"))
        nb_mc = sum(1 for r in rows if r["needs_manual_review"])
        print(f"{name_out}: {len(rows)} rows; needs_manual_review={nb_mc}")


if __name__ == "__main__":
    main()
