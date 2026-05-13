# Deductive coding scheme — open-ended video reflections

Each **submission** (one LMS row per student attempt) can receive **multiple theme flags** (`1` = pattern matched). Columns are independent; overlap is expected and matches reflexive thematic analysis practice.

## Output files

| File | Rows | Contents |
|------|------|-----------|
| `open_ended_essay_theme_codes.csv` | 369 | Non-empty essays only; binary **T1…T6**, `theme_count`, `themes_flagged`, **`needs_manual_review`**, full `essay`. |
| `open_ended_essay_theme_codes_slim.csv` | 369 | Same without `essay` column (easier filtering in Excel). |
| `open_ended_essay_theme_codes_long.csv` | ~variable | One row **per theme hit** (`coded`=1); use for pivot / NVivo import. |
| `open_ended_essay_theme_codes_all_submissions*.csv` | 381 | Includes **12 blank** essays (`essay_blank=1`, all themes 0 unless NA placeholder). |

Regenerate anytime:

```bash
python3 extract_theme_codes.py
```

## Column ↔ analytic theme (memo alignment)

| Column | Memo theme |
|--------|------------|
| `T1_everyday_coffee` | Theme 1 — Everyday anchoring (coffee, sensory, real-world) |
| `T2_clarity_pace` | Theme 2 — Clarity / pace / digestibility |
| `T3_visual_immersion` | Theme 3 — Visual / multimodal / immersion |
| `T4_affect_stigma` | Theme 4 — Affect / fear / stigma |
| `T5_concepts_prior` | Theme 5 — Concepts / prior knowledge bridges |
| `T6_limits_friction` | Theme 6 — Limits / skepticism / logistics |

## `needs_manual_review`

`1` if the essay is **non-blank** but **no automated pattern fired** (`theme_count = 0`). Those rows should be **hand-coded** or the regex rules expanded—do **not** treat as “no themes.”

## Rule basis (transparent)

Rules live in **`extract_theme_codes.py`** (`PATTERNS` dict). They are **deductive keyword / phrase matchers**, not manual TA codes. Counts will **not** match a human codebook exactly.

### Limitations

- Synonyms and negation are only partially handled.  
- Short replies get a **minimal heuristic** (`code_essay` length &lt; 35).  
- **Blank** essays: all zeros unless text is literal `NA` (flagged as T6 for administration).

---

*Companion interpretive write-up: `Thematic_Analysis_Open_Ended_Essays.md`.*
