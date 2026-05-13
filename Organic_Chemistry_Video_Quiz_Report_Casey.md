# Organic Chemistry Video Quiz — Student Data Summary

**Purpose:** Snapshot of anonymized quiz exports for messaging to stakeholders (example: Casey).  
**Video (instructional asset):**  
[https://drive.google.com/file/d/1tVXl61cqf6g5cvm2p4G_TSNd5LP-W8DD/view](https://drive.google.com/file/d/1tVXl61cqf6g5cvm2p4G_TSNd5LP-W8DD/view)  

**Data files:** **Section A** uses the MQ export (`MQ_Organic Chemistry Video Quiz Student Analysis Report anon.csv`); **Section B** uses the DD export (`DD_CHEM14BE_Organic Chemistry Video Quiz Student Analysis Report_Anonymous.csv`).  
**Response counts:** Section A (MQ) **171** submits · Section B (DD) **210** submits (**381** combined).  
**Scoring:** For **Section 3 items (3A–3F)** below, student answers were coded **1 = selected the keyed correct option** vs **0 = other selected response**. **Blanks** (no selection for that stem) are reported separately and **excluded** from item-level percentages.

---

### Visualizations (embedded PNGs)

Figures encode UCLA Blue (#2774AE) vs Gold (#FFD100) with UCLA navy edging for stacked palettes. (See [UCLA color palette](https://brand.ucla.edu/identity/colors).)

### Keyed performance (quiz order 3A–3F and totals)

**Fig. 1 — Per-stem keyed rate for 3A–3F (% with correct keyed answer among students who answered that stem; blanks omitted). Separate from Fig. 2 tally 0/6…6/6.**

Fig. 1 — Per-stem keyed rate for 3A–3F (% with correct keyed answer among students who answered that stem; blanks omitted). Separate from Fig. 2 tally 0/6…6/6.

*Y-axis is zoomed 70–101% (callout explains); pooled diamonds use the same numerator/denominator rule for MQ+DD combined.*

**Fig. 2 — Keyed tally per student shown as fractions 0/6 … 6/6 on the horizontal axis — two cohort bars per tally.**

Fig. 2 — Keyed tally per student shown as fractions 0/6 … 6/6 on the horizontal axis — two cohort bars per tally.

*X-axis tallies 0/6…6/6; pooled headline and shaded 5/6–6/6 column in black; not per-stem percentages (Fig. 1).*

**Fig. 3 — Relative difficulty (pooled): horizontal bars = percentage points BELOW the single easiest keyed stem.**

Fig. 3 — Relative difficulty (pooled): horizontal bars = percentage points BELOW the single easiest keyed stem.

*Not raw item % — gap is (easiest stem pooled keyed %) − (this stem pooled %). Sorted by gap; gold marks largest deficit.*

### Keyed stems — wrong options and blanks

**Fig. 4 — Pooled MQ+DD: 100% stacked answer mix per stem (same scales as Fig. 5A/5B; legend title explains patches).**

Fig. 4 — Pooled MQ+DD: 100% stacked answer mix per stem (same scales as Fig. 5A/5B; legend title explains patches).

*Footer paragraph maps Fig. 4 → pooled · Fig. 5A MQ · Fig. 5B DD; full bar width = cohort slice for that stem.*

**Fig. 5 — Section A (MQ) only — mirrored layout to pooled Fig. 4; answer-mix attribution within this export.**

Fig. 5 — Section A (MQ) only — mirrored layout to pooled Fig. 4; answer-mix attribution within this export.

*Use next figure for Section B; compare both to Fig. 4 to spot cohort-specific drift in distractors.*

**Fig. 6 — Section B (DD CHEM14BE export) — same plotting rules as previous Fig. 5 with MQ.**

Fig. 6 — Section B (DD CHEM14BE export) — same plotting rules as previous Fig. 5 with MQ.

*Paired cohort deep-dive for wrong-option spectra after reading pooled Fig. 4.*

### Attitudes & watch time (not Section 3 multiple choice)

**Fig. 7 — Pre/post Likert means paired by prompt; blanks omitted from denominators.**

Fig. 7 — Pre/post Likert means paired by prompt; blanks omitted from denominators.

*Y-axis repeats full prompt text plus coded non-blank MQ vs CHEM14BE totals per stem.*

**Fig. 8 — Watch time: grouped horizontal bars (Section A vs Section B) plus right-hand n / % and numeric table with full LMS strings.**

Fig. 8 — Watch time: grouped horizontal bars (Section A vs Section B) plus right-hand n / % and numeric table with full LMS strings.

*Replaces the old single-row 100% stacks; each row is one checklist option and bar length is % of that cohort who chose it (not a strip within one bar).*

Rebuild charts plus inline previews: `python3 build_quiz_visualizations.py && python3 embed_figures_in_md.py`.

---

## Section 3 (3A–3F): Binary results — combined and by section

*"Percent correct"* = correct ÷ (correct + incorrect) for that stem; blanks listed separately.


| Item   | Topic                | Section A (MQ) — correct % (n) | Section B (DD) — correct % (n) | **Combined — correct % (n)** | Blanks Sec A / B |
| ------ | -------------------- | ------------------------------ | ------------------------------ | ---------------------------- | ---------------- |
| **3A** | Definition           | 95.8% (168)                    | 94.7% (208)                    | **95.2%** **(376)**          | 7 / 2            |
| **3B** | Wedges/hashes        | 97.6% (167)                    | 97.1% (207)                    | **97.3%** **(374)**          | 8 / 3            |
| **3C** | Bonds on C           | 95.2% (168)                    | 97.1% (208)                    | **96.3%** **(376)**          | 8 / 2            |
| **3D** | Carbons in shorthand | 82.6% (167)                    | 83.1% (207)                    | **82.9%** **(374)**          | 8 / 3            |
| **3E** | Structure count      | 91.6% (166)                    | 93.8% (209)                    | **92.8%** **(375)**          | 9 / 1            |
| **3F** | Coffee molecules     | 94.5% (165)                    | 95.2% (207)                    | **94.9% (372)**              | 12 / 3           |


**Takeaways (content)**

- **3D** (implicit carbons / line-angle interpretation) was the hardest item for **both** sections (~83% correct vs mid‑90s for most other stems).
- **3B** and **3C** showed the strongest performance (mid‑/high‑90% correct pooled).
- Differences **between Section A (MQ) and Section B (DD)** were small overall (typically within a few percentage points per item).

**Total binary score:** Count of six items correct **per student** (only items answered count toward totals below; omitting blanks slightly shifts individual totals).

**Distribution — students scoring k out of 6 items correct**


| k (correct of 6) | Sec A (MQ) | Sec B (DD) | Combined |
| ---------------- | ---------- | ---------- | -------- |
| 0                | 1          | —          | 1        |
| 1                | 2          | 1          | 3        |
| 2                | 3          | 4          | 7        |
| 3                | 5          | 4          | 9        |
| 4                | 14         | 11         | 25       |
| 5                | 25         | 40         | 65       |
| 6                | 121        | 150        | 271      |


Roughly **71%** of all students (**271 / 381**) answered all six content items correctly. Most of the remainder missed only one item (typically consistent with weaker performance on **3D** alone).

---

## Other survey content (non-binary overview)

Likert anchors are treated numerically **Strongly disagree = −2 … Strongly agree = +2** for simple means (not substitutes for qualitative review).

### Pre-video attitudes — first occurrence of each stem


| Stem                            | Sec A (MQ) approx. mean | Sec B (DD) approx. mean |
| ------------------------------- | ----------------------- | ----------------------- |
| Nervous about organic chemistry | +1.06                   | +1.15                   |
| Excited to learn ochem          | +0.46                   | +0.38                   |
| Connection chem ↔ real world    | +0.96                   | +0.89                   |


*(The export lists some attitude prompts twice — means above use **first block** columns only.)*

### Post-video perceptions (experience items)


| Stem                                                | Sec A mean | Sec B mean |
| --------------------------------------------------- | ---------- | ---------- |
| Video helped introduce less-familiar concepts       | **+1.00**  | +0.86      |
| Immersive format helped understanding               | **+1.00**  | +0.85      |
| Needed to rewatch parts                             | −0.02      | −0.13      |
| “Video changed how I think about organic chemistry” | +0.60      | +0.29      |


**Section A (MQ)** showed **slightly higher** mean agreement on introducing concepts and immersion in this snapshot; Section A also averaged **higher agreement** that the video changed how students think about organic chemistry (difference should be interpreted cautiously — different cohorts and self-report).

### Honest estimate — how long watched the video


| Response      | Sec A (MQ) (n) | Sec B (DD) (n) |
| ------------- | -------------- | -------------- |
| Entire video  | 143            | 166            |
| 30 s–2 min    | 16             | 25             |
| 30 s or less  | 3              | 10             |
| Did not watch | 2              | 5              |


Essay prompts (open-ended) were not summarized here; they remain in the CSV for qualitative/thematic coding if desired.

---

## Implementation notes / QA

- **HTML stripping:** Multiple-choice answers arrive as HTML snippets; correctness was evaluated on **stripped/plain** text equivalence to keyed options above.
- **Edge cases:** A few respondents left individual stems blank — treated as blanks, not incorrect.
- **Section identity:** Rows are **anonymous** — **Section A (MQ)** ↔ `MQ` export; **Section B (DD)** ↔ `DD_CHEM14BE` export.
- **Charts:** `build_quiz_visualizations.py` writes **eight** PNGs (`fig1`, `fig2`, `fig3`, `fig4`, two section-specific `fig5`_* answer-mix files, `fig6_likert_pre_post`, `fig7_watch_time_by_section`). `embed_figures_in_md.py` inlines them as base64 in this file; rerun both scripts after edits.

---

*Prepared for stakeholder review · Source: quiz CSV exports dated March 2026 submissions.*