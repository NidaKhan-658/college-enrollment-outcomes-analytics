"""
Synthetic data generator - U.S. College Enrollment, Admissions, Funding & Outcomes.
All institutions, students and applicants are FICTIONAL. Seeded for reproducibility.
Data as-of date: 2026-08-31. Cohort (entry) years: 2018-2025.
Usage:
  python generate_data.py --extract v1.0   -> baseline extract (3 tables, no aid or funding fields)
  python generate_data.py --extract v1.1   -> adds aid fields and college funding table (Change Request CR-001)
Both extracts come from the same seeded run, so shared values are identical across versions.
"""
import numpy as np, pandas as pd, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--extract", choices=["v1.0", "v1.1"], default="v1.0"); args = ap.parse_args()

SEED = 42
rng = np.random.default_rng(SEED)
YEARS = list(range(2018, 2026))
AS_OF_YEAR = 2026            # events dated May 15 of event year; as-of Aug 31, 2026
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_" + args.extract)
sig = lambda x: 1 / (1 + np.exp(-x))
logit = lambda p: np.log(p / (1 - p))

# ---------------- dim_college ----------------
places = ["Alder","Brookhaven","Cedar Ridge","Dunmore","Eastgate","Fairhaven","Glenmoor","Harborview","Ironwood",
          "Juniper Falls","Kestrel","Lakemont","Maplewood","Northfield","Oakhurst","Pinecrest","Quarry Hill","Redwater",
          "Stonebridge","Timberline","Upland","Valemont","Westbrook","Yarrow","Zephyr Bay","Ashford","Briarwood",
          "Copperfield","Driftwood","Elmhurst"]
regions = {"Northeast":["NY","PA","MA","NJ"],"Midwest":["OH","IL","MI","MN","WI"],
           "South":["TX","FL","GA","NC","VA","TN"],"West":["CA","WA","CO","AZ","OR"]}
state_region = {s: r for r, ss in regions.items() for s in ss}
all_states = list(state_region)
controls = ["Public"]*12 + ["Private Nonprofit"]*12 + ["Private For-Profit"]*6
rng.shuffle(controls)
rows = []
for i, (pl, ctl) in enumerate(zip(places, controls), 1):
    st = all_states[i % len(all_states)] if i % 3 else rng.choice(all_states)
    name = {"Public": f"{pl} State University", "Private Nonprofit": rng.choice([f"{pl} College", f"University of {pl}"]),
            "Private For-Profit": f"{pl} Institute"}[ctl]
    admit = {"Public": 0.70, "Private Nonprofit": 0.55, "Private For-Profit": 0.90}[ctl] + rng.normal(0, 0.10)
    q = {"Public": 0.0, "Private Nonprofit": 0.35, "Private For-Profit": -0.9}[ctl] + rng.normal(0, 0.55)
    apps = int(rng.uniform(150, 600))
    tin = {"Public": 11000, "Private Nonprofit": 38000, "Private For-Profit": 18000}[ctl] * rng.uniform(0.85, 1.15)
    tout = tin * (2.4 if ctl == "Public" else 1.0)
    rows.append(dict(college_id=f"C{i:02d}", college_name=name, state=st, region=state_region[st], control_type=ctl,
                     _admit=float(np.clip(admit, 0.30, 0.95)), _q=q, _apps=apps, _tin=tin, _tout=tout,
                     _yield=float(np.clip(rng.normal(0.34, 0.05), 0.2, 0.5))))
col = pd.DataFrame(rows)
col["size_tier"] = pd.cut(col["_apps"], [0, 280, 420, 10**6], labels=["Small", "Medium", "Large"]).astype(str)
col["selectivity_tier"] = pd.cut(col["_admit"], [0, 0.50, 0.75, 1.01], labels=["Highly Selective", "Moderately Selective", "Open Admission"]).astype(str)

# ---------------- applications ----------------
channels = ["College Website","Campus Visit / Open House","High School Counselor","Social Media",
            "Friends / Family / Alumni","College Fair","Online Search / Rankings Sites","Advertising / Direct Mail"]
def ch_weights(y):
    t = (y - 2018) / 7
    w = np.array([0.22, 0.14, 0.16, 0.08 + 0.14 * t, 0.14, 0.10 - 0.04 * t, 0.10, 0.06 - 0.03 * t])
    return w / w.sum()
ch_yield_mult = dict(zip(channels, [1.0, 1.6, 1.2, 0.7, 1.4, 0.9, 0.8, 0.6]))
fields = ["Nursing & Health Sciences","Business","Engineering","Computer Science","Biology & Life Sciences",
          "Psychology","Social Sciences","Education","Arts & Humanities","Physical Sciences & Math"]
f_w = np.array([0.14, 0.15, 0.10, 0.11, 0.09, 0.09, 0.08, 0.08, 0.10, 0.06]); f_w /= f_w.sum()
app_rows = []
aid = 0
for _, c in col.iterrows():
    for y in YEARS:
        n = int(c._apps * (1 + 0.03 * (y - 2018)) * (0.92 if y == 2020 else 1) * rng.uniform(0.9, 1.1))
        ch = rng.choice(channels, n, p=ch_weights(y))
        admitted = rng.random(n) < np.clip(c._admit + np.where(ch == "Campus Visit / Open House", 0.03, 0), 0, 0.98)
        ymult = np.array([ch_yield_mult[x] for x in ch])
        enrolled = admitted & (rng.random(n) < np.clip(c._yield * ymult, 0.05, 0.85))
        in_state_p = 0.60 if c.control_type == "Public" else 0.35
        a_state = np.where(rng.random(n) < in_state_p, c.state, rng.choice(all_states, n))
        fld = rng.choice(fields, n, p=f_w)
        for k in range(n):
            aid += 1
            app_rows.append((f"A{aid:06d}", c.college_id, y, ch[k], a_state[k], fld[k], int(admitted[k]), int(enrolled[k])))
apps = pd.DataFrame(app_rows, columns=["application_id","college_id","application_year","discovery_channel",
                                        "applicant_state","intended_field","admitted_flag","enrolled_flag"])

# ---------------- students (enrolled applicants) ----------------
base_grad = {"Nursing & Health Sciences": 0.82, "Education": 0.74, "Business": 0.72, "Biology & Life Sciences": 0.70,
             "Engineering": 0.68, "Psychology": 0.68, "Computer Science": 0.66, "Social Sciences": 0.66,
             "Physical Sciences & Math": 0.65, "Arts & Humanities": 0.58}
stem = {"Engineering", "Computer Science", "Biology & Life Sciences", "Physical Sciences & Math", "Nursing & Health Sciences"}
inc_bands = ["Under $30K", "$30K-$60K", "$60K-$100K", "$100K-$150K", "$150K+"]
inc_p = [0.22, 0.20, 0.24, 0.20, 0.14]; fg_p = dict(zip(inc_bands, [0.55, 0.42, 0.28, 0.18, 0.10]))
enr = apps[apps.enrolled_flag == 1].merge(col, on="college_id")
n = len(enr)
field = np.where(rng.random(n) < 0.85, enr.intended_field.values, rng.choice(fields, n, p=f_w))
income = rng.choice(inc_bands, n, p=inc_p)
first_gen = (rng.random(n) < np.array([fg_p[i] for i in income])).astype(int)
sel = (0.6 - enr._admit.values)
hs_gpa = np.clip(rng.normal(3.35 + 0.25 * sel, 0.40, n), 2.0, 4.0).round(2)
in_state = (enr.applicant_state.values == enr.state.values).astype(int)
infl = 1.03 ** (enr.application_year.values - 2018)
tuition = (np.where(in_state == 1, enr._tin.values, enr._tout.values) * infl * rng.uniform(0.97, 1.03, n)).round(-1)
low_inc = np.isin(income, ["Under $30K", "$30K-$60K"])
ctl = enr.control_type.values
p_any = np.select([ctl == "Public", ctl == "Private Nonprofit"], [0.42, 0.72], 0.30) \
        + 0.35 * (hs_gpa - 3.3) + 0.12 * low_inc + 0.05 * np.isin(field, list(stem))
has_sch = rng.random(n) < np.clip(p_any, 0.05, 0.95)
stype = np.array(["None"] * n, dtype=object)
frac = np.zeros(n)
for i in np.where(has_sch)[0]:
    w = np.array([0.35 + 0.40 * (hs_gpa[i] > 3.6), 0.35 if low_inc[i] else 0.15, 0.15, 0.06]); w /= w.sum()
    t = rng.choice(["Merit", "Need-Based", "Departmental", "Athletic"], p=w)
    lo, hi = {"Merit": (0.15, 0.55), "Need-Based": (0.20, 0.70), "Departmental": (0.05, 0.25), "Athletic": (0.30, 0.80)}[t]
    stype[i] = t; frac[i] = rng.uniform(lo, hi)
scholarship = (np.round(tuition * frac / 50) * 50).astype(int)
grant = np.where(low_inc & (rng.random(n) < 0.6), rng.integers(2000, 7000, n), 0).astype(int)
grant = np.minimum(grant, np.maximum(tuition - scholarship, 0)).astype(int)
remaining = np.maximum(tuition - scholarship - grant, 0)
loan = np.where(rng.random(n) < 0.5, (remaining * rng.uniform(0.3, 0.7, n)).round(-2), 0).astype(int)
net_cost = np.maximum(tuition - scholarship - grant, 0).astype(int)
coverage = (scholarship + grant) / tuition
fg_arr = np.array([base_grad[f] for f in field])
lg = logit(fg_arr) + 0.45 * enr._q.values + 0.9 * (hs_gpa - 3.3) + 1.6 * coverage - 0.35 * first_gen - 0.30 * (loan > 0) + rng.normal(0, 0.5, n)
grad_ult = rng.random(n) < sig(lg)
cohort = enr.application_year.values
t_grad = rng.choice([4, 5, 6], n, p=[0.62, 0.28, 0.10])
t_drop = rng.choice([1, 2, 3, 4], n, p=[0.42, 0.30, 0.18, 0.10])
t = np.where(grad_ult, t_grad, t_drop)
event_year = cohort + t
resolved = event_year <= AS_OF_YEAR
status = np.where(~resolved, "Enrolled (Active)", np.where(grad_ult, "Graduated", "Dropped Out"))
gpa_base = 3.0 + 0.3 * (hs_gpa - 3.3)
cum_gpa = np.where(status == "Dropped Out", rng.normal(gpa_base - 0.6, 0.5, n), rng.normal(gpa_base, 0.35, n))
cum_gpa = np.clip(cum_gpa, 0.5, 4.0).round(2)
stu = pd.DataFrame(dict(
    student_id=[f"S{i:06d}" for i in range(1, n + 1)], application_id=enr.application_id.values,
    discovery_channel=enr.discovery_channel.values,
    college_id=enr.college_id.values, cohort_year=cohort, field_of_study=field,
    stem_flag=np.where(np.isin(field, list(stem)), "STEM", "Non-STEM"),
    family_income_band=income, first_gen_flag=first_gen, in_state_flag=in_state, hs_gpa=hs_gpa,
    annual_tuition_usd=tuition.astype(int), scholarship_type=stype, annual_scholarship_usd=scholarship,
    annual_grant_usd=grant, annual_loan_usd=loan, annual_net_cost_usd=net_cost,
    enrollment_status=status,
    graduation_year=np.where(status == "Graduated", event_year, np.nan),
    dropout_year=np.where(status == "Dropped Out", event_year, np.nan),
    years_to_outcome=np.where(status == "Enrolled (Active)", np.nan, t),
    cumulative_gpa=cum_gpa))
for c_ in ["graduation_year", "dropout_year", "years_to_outcome"]:
    stu[c_] = stu[c_].astype("Int64")

# ---------------- college_funding (college x fiscal year) ----------------
intake = stu.groupby(["college_id", "cohort_year"]).size().rename("intake").reset_index()
sch = stu.groupby(["college_id", "cohort_year"]).agg(avg_sch=("annual_scholarship_usd", "mean"),
        avg_net=("annual_net_cost_usd", "mean")).reset_index()
f = intake.merge(sch, on=["college_id", "cohort_year"]).merge(col[["college_id", "control_type"]], on="college_id")
m = len(f)
enroll_est = (f.intake.values * 3.7 * rng.uniform(0.93, 1.07, m)).round().astype(int)
yr = f.cohort_year.values - 2018
ct = f.control_type.values
state_app = np.where(ct == "Public", enroll_est * rng.uniform(6500, 9500, m) * (1 + 0.02 * yr),
                     np.where(ct == "Private Nonprofit", enroll_est * rng.uniform(300, 900, m), 0))
fed = np.where(ct == "Private Nonprofit", enroll_est * rng.uniform(1500, 3500, m),
               np.where(ct == "Public", enroll_est * rng.uniform(800, 2800, m), enroll_est * rng.uniform(100, 500, m)))
endow = np.where(ct == "Private Nonprofit", enroll_est * rng.uniform(3000, 12000, m),
                 np.where(ct == "Public", enroll_est * rng.uniform(500, 2500, m), 0))
awarded = enroll_est * f.avg_sch.values
budget = awarded * rng.uniform(1.05, 1.30, m)
fund = pd.DataFrame(dict(college_id=f.college_id.values, fiscal_year=f.cohort_year.values,
    total_enrollment_est=enroll_est, state_appropriation_usd=state_app.round(-3).astype(np.int64),
    federal_research_grants_usd=fed.round(-3).astype(np.int64), endowment_payout_usd=endow.round(-3).astype(np.int64),
    net_tuition_revenue_usd=(enroll_est * f.avg_net.values).round(-3).astype(np.int64),
    scholarship_awarded_usd=awarded.round(-3).astype(np.int64), scholarship_budget_usd=budget.round(-3).astype(np.int64)))

col_out = col[["college_id","college_name","state","region","control_type","size_tier","selectivity_tier"]]
AID_COLS = ["annual_tuition_usd","scholarship_type","annual_scholarship_usd","annual_grant_usd","annual_loan_usd","annual_net_cost_usd"]
os.makedirs(OUT, exist_ok=True)
col_out.to_csv(f"{OUT}/dim_college.csv", index=False)
apps.to_csv(f"{OUT}/fact_applications.csv", index=False)
if args.extract == "v1.0":
    stu.drop(columns=AID_COLS).to_csv(f"{OUT}/fact_students.csv", index=False)
    print({k: len(v) for k, v in dict(dim_college=col_out, fact_applications=apps, fact_students=stu).items()})
else:
    stu.to_csv(f"{OUT}/fact_students.csv", index=False)
    fund.to_csv(f"{OUT}/fact_college_funding.csv", index=False)
    print({k: len(v) for k, v in dict(dim_college=col_out, fact_applications=apps, fact_students=stu, fact_college_funding=fund).items()})
