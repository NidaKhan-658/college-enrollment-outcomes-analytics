"""
Independent check of the reference values used in the docs and workbook.
Recomputes KPI-01..KPI-15 and the LOD Lab demo values from the CSV extract with pandas,
so Tableau results can be compared with a second, independent calculation.
Usage: python data/validate_reference_values.py [v1.0|v1.1]   (default v1.1; KPI-11..15 and demo E need v1.1)
"""
import sys, os, pandas as pd
ver = sys.argv[1] if len(sys.argv) > 1 else "v1.1"
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"extract_{ver}")
col = pd.read_csv(f"{D}/dim_college.csv"); A = pd.read_csv(f"{D}/fact_applications.csv"); S = pd.read_csv(f"{D}/fact_students.csv")
S = S.merge(col, on="college_id")
S["grad"] = (S.enrollment_status == "Graduated").astype(int); S["drop"] = (S.enrollment_status == "Dropped Out").astype(int)
C = S[S.cohort_year <= 2020]                                   # completed cohorts (Last Complete Cohort = 2020)
fy = lambda d: ((d["drop"] == 1) & (d.years_to_outcome == 1)).sum()
pct = lambda x: f"{x*100:.2f}%"
print(f"== KPIs ({ver}) ==")
print("KPI-01 Total Applications      ", f"{len(A):,}")
print("KPI-02 Admit Rate              ", pct(A.admitted_flag.mean()))
print("KPI-03 Yield Rate              ", pct(A.enrolled_flag.sum() / A.admitted_flag.sum()))
print("KPI-04 Enrolled Students       ", f"{len(S):,}")
print("KPI-05 Graduation Rate (6-yr)  ", pct(C.grad.mean()))
print("KPI-06 Dropout Rate (completed)", pct(C["drop"].mean()))
print("KPI-07 Attrition to Date       ", pct(S["drop"].mean()))
print("KPI-08 First-Year Retention    ", pct(1 - fy(C) / len(C)))
g = C.groupby("college_id"); idx = 100 * (0.60 * g.grad.mean() + 0.25 * g.apply(lambda d: 1 - fy(d) / len(d)) + 0.15 * g.cumulative_gpa.mean() / 4)
top = idx.idxmax(); print("KPI-09 Top Performance Index   ", f"{idx.max():.1f}", col.set_index("college_id").loc[top, "college_name"], f"({int(g.size()[top])} completed students)")
y = A.groupby("discovery_channel").apply(lambda d: d.enrolled_flag.sum() / d.admitted_flag.sum()).sort_values(ascending=False)
print("KPI-10 Top channel by yield    ", y.index[0], pct(y.iloc[0]))
if ver == "v1.1":
    F = pd.read_csv(f"{D}/fact_college_funding.csv")
    print("KPI-11 Avg Annual Scholarship  ", f"${S.annual_scholarship_usd.mean():,.0f}")
    print("KPI-12 Recipient Rate          ", pct((S.annual_scholarship_usd > 0).mean()))
    print("KPI-13 Avg Annual Net Cost     ", f"${S.annual_net_cost_usd.mean():,.0f}")
    print("KPI-14 Scholarship Utilization ", pct(F.scholarship_awarded_usd.sum() / F.scholarship_budget_usd.sum()))
    print("KPI-15 Funding per Student     ", f"${(F.state_appropriation_usd.sum()+F.federal_research_grants_usd.sum()+F.endowment_payout_usd.sum())/F.total_enrollment_est.sum():,.0f}")
print("\n== LOD Lab ==")
rate = lambda d: d["drop"].sum() / len(d)
fp = C[C.control_type == "Private For-Profit"]; sub = ["Engineering", "Computer Science", "Arts & Humanities"]
print("A  benchmark: none / For-Profit / For-Profit + 3 fields:", pct(rate(C)), pct(rate(fp)), pct(rate(fp[fp.field_of_study.isin(sub)])))
pub = S[S.control_type == "Public"]; print("B  Public students:", f"{len(pub):,}", "share of all:", pct(len(pub) / len(S)))
cr = C.groupby("college_id").grad.mean(); print("C  pooled vs avg of college graduation rate:", pct(C.grad.mean()), pct(cr.mean()))
if ver == "v1.1":
    print("C2 pooled vs avg of college scholarship: ", f"${S.annual_scholarship_usd.mean():,.0f}", f"${S.groupby('college_id').annual_scholarship_usd.mean().mean():,.0f}")
    j = S.merge(F, left_on=["college_id", "cohort_year"], right_on=["college_id", "fiscal_year"])
    print("E  naive vs true state appropriation:", f"${j.state_appropriation_usd.sum():,}", f"${F.state_appropriation_usd.sum():,}", f"({j.state_appropriation_usd.sum()/F.state_appropriation_usd.sum():.1f}x)")
