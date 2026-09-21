# Data notes

- `generate_data.py` creates all data from a fixed seed (42). Nothing here is real.
- `extract_v1.0/` is the baseline extract: `dim_college`, `fact_applications`, `fact_students`.
- `extract_v1.1/` (Change Request CR-001) adds six student aid fields and the `fact_college_funding` table. It comes from the same seeded run, so every shared value is identical to v1.0.
- As-of date 2026-08-31. Graduation and dropout events are dated May of the event year.
- Cohorts 2018-2020 are treated as fully observed for 6-year graduation KPIs; later cohorts still contain active students (right-censoring).

## Regenerate
```bash
pip install numpy pandas
python data/generate_data.py --extract v1.0
python data/generate_data.py --extract v1.1
```

## Synthetic data design (read before interpreting results)
The generator builds in known effects, so patterns in the dashboards are expected, not discoveries:
- Field of study sets a base graduation likelihood (Nursing & Health Sciences highest, Arts & Humanities lowest).
- College quality (control type plus random variation), high-school GPA and aid coverage raise completion; first-generation status and loans lower it.
- Discovery channels have different yield multipliers (Campus Visit highest, Advertising lowest); Social Media share grows over time.
- Funding is generated at college and fiscal-year level; scholarship budget is awarded amount times a factor of 1.05 to 1.30.
- Discovery channel has no built-in effect on graduation, so differences by channel are noise.

Full column definitions and reconciliation counts: `docs/BA_Requirements_Workbook_v1.1.xlsx`.
