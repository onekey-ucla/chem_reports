"""
Shared CSS for Organic Chemistry Video Quiz HTML reports.

Used by build_html_report.py and build_instructor_report.py so stakeholder and instructor
exports share one typography scale, colors, and component styles.
"""

# Single stylesheet: keep all font sizes in rem off --fs-body (16px default).
REPORT_CSS = """
:root {
  --ucla-blue: #2774AE;
  --ucla-gold: #FFD100;
  --ucla-navy: #005587;
  --text: #212121;
  --muted: #444;
  --rule: #c5dcea;
  --max-w: 56rem;
  --font-sans: "Helvetica Neue", Helvetica, Arial, system-ui, sans-serif;
  --fs-body: 1rem;
  --fs-small: 0.9375rem;
  --fs-caption: 0.8125rem;
  --fs-tag: 0.75rem;
  --fs-h1: 1.5rem;
  --fs-h2: 1.2rem;
  --fs-h3: 1.1rem;
}

* { box-sizing: border-box; }

body.quiz-report {
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--fs-body);
  color: var(--text);
  line-height: 1.5;
  background: #fafafa;
}

a { color: var(--ucla-blue); }
a:visited { color: #1a5f8a; }

.report-shell {
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 1.75rem 1.25rem 3rem;
}

.report-article > h1 {
  color: var(--ucla-navy);
  font-size: var(--fs-h1);
  font-weight: 700;
  margin: 0 0 0.75rem;
  line-height: 1.25;
}

.report-article > .lede,
.report-instructor-lede {
  font-size: var(--fs-small);
  color: var(--muted);
  line-height: 1.55;
  margin-bottom: 1rem;
}

h2 {
  color: var(--ucla-blue);
  font-size: var(--fs-h2);
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.65rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid var(--ucla-gold);
}

h3 {
  color: var(--ucla-navy);
  font-size: var(--fs-h3);
  font-weight: 600;
  margin: 1.5rem 0 0.5rem;
}

h4 {
  font-size: var(--fs-small);
  font-weight: 600;
  color: var(--ucla-navy);
  margin: 1rem 0 0.4rem;
}

.muted {
  color: var(--muted);
  font-size: var(--fs-caption);
}

table.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0 1.25rem;
  font-size: var(--fs-small);
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 87, 135, 0.08);
}

table.data-table th {
  background: var(--ucla-blue);
  color: #fff;
  text-align: left;
  padding: 0.5rem 0.65rem;
  font-weight: 600;
}

table.data-table td {
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--rule);
}

table.data-table tbody tr:nth-child(even) {
  background: #f8fcff;
}

.figure-block {
  margin: 1.75rem 0;
  padding: 1rem;
  background: #fff;
  border: 1px solid var(--rule);
  border-radius: 4px;
}

.figure-block figcaption,
.fine-print {
  font-size: var(--fs-caption);
  color: var(--muted);
  margin-top: 0.6rem;
  line-height: 1.45;
}

.tag {
  display: block;
  font-size: var(--fs-tag);
  font-weight: 700;
  letter-spacing: 0.03em;
  color: var(--ucla-navy);
  margin-bottom: 0.4rem;
  text-transform: none;
}

.interpret {
  border-left: 4px solid var(--ucla-gold);
  padding-left: 0.85rem;
  margin: 0 0 0.95rem;
  font-size: var(--fs-small);
  color: var(--muted);
  line-height: 1.55;
}

.interpret p {
  margin: 0 0 0.45rem;
}

.interpret p:last-child {
  margin-bottom: 0;
}

.mix-bundle {
  margin-bottom: 2rem;
}

.mix-bundle > h3 {
  margin-top: 0.5rem;
}

.subsection-lede {
  font-size: var(--fs-small);
  color: var(--muted);
  margin: 0 0 0.85rem;
  line-height: 1.48;
}

.subs {
  font-size: 0.85em;
  vertical-align: sub;
}

.stem-facts {
  margin: 0 0 0.95rem;
  padding: 0.85rem 0.95rem;
  border: 1px solid var(--rule);
  border-radius: 6px;
  background: linear-gradient(165deg, #f8fbff 0%, #fff 58%);
  font-size: var(--fs-small);
}

.stem-facts-lead {
  margin: 0 0 0.4rem;
  font-size: var(--fs-body);
  font-weight: 600;
  color: var(--ucla-navy);
}

.cohort-badge {
  display: inline-block;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  background: #e8f4ff;
  font-size: var(--fs-caption);
  margin-left: 0.25rem;
  font-weight: 500;
}

.stem-rubric {
  margin: 0 0 0.65rem;
  line-height: 1.42;
}

.stem-kpis {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin: 0.25rem 0 0.35rem;
}

.kpi {
  min-width: 6rem;
  padding: 0.4rem 0.65rem;
  border: 1px solid #c5dcea;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 87, 135, 0.06);
  text-align: center;
}

.kpi-val {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ucla-blue);
  line-height: 1.25;
}

.kpi-lbl {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
}

.wrong-wrap {
  margin-top: 0.45rem;
}

.wrong-h {
  margin: 0 0 0.2rem;
  font-size: var(--fs-caption);
  font-weight: 600;
  color: var(--ucla-navy);
}

.wrong-ul {
  margin: 0;
  padding-left: 1rem;
  font-size: var(--fs-small);
}

.wrong-ul li {
  margin-bottom: 0.28rem;
}

.wrong-pct {
  display: inline-block;
  min-width: 2.85rem;
  padding-right: 0.35rem;
  font-weight: 700;
  color: var(--ucla-blue);
  font-variant-numeric: tabular-nums;
}

.wrong-txt {
  font-size: var(--fs-small);
}

.plotly-host {
  width: 100%;
  overflow-x: auto;
  margin-top: 0.35rem;
}

.plotly-host .js-plotly-plot,
.plotly-host .plotly-graph-div {
  max-width: 100% !important;
}

code {
  font-size: 0.9em;
  background: #eef6fc;
  padding: 0.1em 0.35em;
  border-radius: 3px;
}

.report-section {
  margin-bottom: 0.5rem;
}

ul.bullet-list {
  padding-left: 1.35rem;
  font-size: var(--fs-small);
}

ul.bullet-list li {
  margin-bottom: 0.35rem;
}

#stem-narratives,
[id^="stem-narratives-"] {
  scroll-margin-top: 5rem;
}
"""
