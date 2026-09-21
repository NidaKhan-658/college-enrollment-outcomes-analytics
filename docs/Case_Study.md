# Case Study: From Discovery to Graduation (U.S. College Enrollment & Outcomes Analytics)

> Simulated engagement with synthetic data. Sponsor, stakeholders, colleges and students are fictional. Findings describe the synthetic data only.

**Role:** Business Analyst | **Tool:** Tableau | **Tableau Public:** [add link after publishing] | **Repository:** this repo

## 1. Summary
A fictional university system needed one view connecting how students discover a college, what aid they receive, and whether they graduate or leave. I ran the project end to end as a BA: baseline requirements, synthetic data, a governed KPI set, a formal change request that added funding and scholarships, and a Tableau "LOD vs Table Calculation Lab" that explains why the same KPI can change with the calculation method.

## 2. Business questions
- Which discovery channels convert admitted applicants into enrolled students?
- Which fields of study graduate the most students, and which lose the most?
- Which colleges perform best on a transparent index?
- How do scholarships, aid and college funding relate to outcomes? (added by CR-001)
- Why do table calculations and LOD expressions give different answers?

## 3. What I delivered
| Deliverable | Location |
|---|---|
| Business Requirements Document v1.0 and v1.1 | `docs/` |
| Functional Requirements Document v1.0 and v1.1 (26 then 34 FRs, KPI dictionary, calculated fields) | `docs/` |
| Requirements workbook: data model, dictionary, mapping, reconciliation, 38 user stories, 15 KPIs, reference values, traceability, 36 test cases, CR log | `docs/` |
| Change Request Pack: CR-001 approved, CR-002 deferred, CR-003 rejected | `change-control/` |
| Seeded synthetic data generator and two extracts (v1.0, v1.1) | `data/` |
| Tableau build guide, LOD lab and CR-001 addendum | `docs/` |

## 4. Approach
1. **Baseline requirements.** 10 business requirements, 5 objectives, risks and a KPI dictionary before any build. Each requirement traces to functional requirements, user stories and test cases.
2. **Data.** Generated 92,555 applications, 23,121 students and 30 colleges (cohorts 2018-2025) with a seeded script, plus a dictionary, mapping and 17 reconciliation checks.
3. **Change control.** After baseline, a request added funding and scholarships. I wrote the impact analysis (scope, data, effort about 4 days, risk), compared three options, and the board approved with conditions: KPI regression must pass and funding totals must reconcile. Two other requests were deferred and rejected with reasons.
4. **Build and validate.** Every dashboard number is checked against independently computed reference values.

## 5. Findings (synthetic data)
- **Channels:** Campus Visit / Open House has the highest yield (53.1%); Advertising / Direct Mail the lowest (19.4%).
- **Fields:** Nursing & Health Sciences has the highest 6-year graduation rate (79.3%); Arts & Humanities the highest dropout rate (38.5%).
- **Aid:** graduation rises with aid coverage, from 60.6% with no aid to 81.8% above 50% coverage. The generator builds this link in, so it illustrates the analysis, not a real-world result.
- **Funding:** funding per student is about $11,700 at public colleges and $300 at for-profit colleges.

## 6. Analytical judgment calls
- **Right-censoring.** Recent cohorts still have active students, so graduation KPIs use only cohorts 2018-2020 and a separate "attrition to date" KPI is labeled as such.
- **Pooled versus averaged rates.** KPI definitions are student-weighted (pooled); averaging college rates gives a different answer, shown in the lab.
- **Minimum sample size.** The top-ranked college had only 78 completed students; I raised it as an open issue and added a minimum-students control.

## 7. LOD vs table calculation lab
| Demo | Lesson | Reference result |
|---|---|---|
| A | Table calculations and EXCLUDE follow filters; FIXED does not | Benchmark stays 29.46% under FIXED while the filtered benchmark is 37.92% |
| B | Percent of total: share of the view versus share of the whole | 100% versus 43.3% under a Public filter |
| C / C2 | Weighting changes a KPI | Scholarship: $5,949 pooled versus $6,498 averaged across colleges |
| D | Context filters run before FIXED; normal filters run after | FIXED benchmark moves from 29.46% to 37.92% |
| E | Joining data of different grain inflates sums; FIXED at the smaller grain fixes it | $39.6 billion naive versus $330.7 million correct (119.8 times) |

## 8. Resume bullets (adjust to what you have completed)
- Authored a BRD, FRD, 38 user stories, data mapping, KPI dictionary, 36 test cases and a traceability matrix for a Tableau analytics project on U.S. college enrollment, admissions and outcomes.
- Managed formal change control: assessed a scope-adding change request (impact on requirements, data, effort and risk), obtained approval with conditions, and re-baselined documents from v1.0 to v1.1 with regression testing of 10 baseline KPIs.
- Designed a synthetic dataset (about 93K applications, 23K students, 30 colleges) with a reproducible generator and 27 reconciliation checks to validate Tableau against independent reference values.
- Built a Tableau "LOD vs Table Calculation" lab with five documented demos showing how FIXED, INCLUDE, EXCLUDE and table calculations differ under filters and mixed-grain data. [add once built and published]

## 9. Interview talking points
- **Change control story.** "After baseline sign-off a request added scholarships and funding. I wrote an impact analysis, compared three options, got approval with a regression condition, and versioned the documents from v1.0 to v1.1."
- **LOD versus table calc.** "A table calculation works on the marks in the view, so it changes with filters. FIXED works on the data at a level I name, so it ignores normal filters unless they are in context."
- **Data quality.** "I noticed recent cohorts looked worse only because outcomes were not yet known, so I defined completed cohorts and labeled a separate attrition KPI."
- **Traceability.** "Every business requirement maps to functional requirements, stories and tests, and the workbook flags any gap with formulas."

## 10. What I would do next (v2.0)
Handle transfer-outs (CR-002), which redefines graduation and dropout and needs a major version; add statistical controls before interpreting aid effects on real data.
