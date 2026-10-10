"""
CareFlow - Week 4: Ideal Pathway Definition (Day 2 to Day 7)

Input : careflow_event_log_clean_sorted.csv  (Case_ID, Activity_Name, Timestamp)
Output: ideal_pathway_stages.md, required_vs_optional.md, allowed_transitions.csv,
        exceptions.md, ideal_pathway_rules.md, ideal_pathway.json,
        validation_report.txt, README_week4.md

Run   : python week4_ideal_pathway.py
Tip   : agar tumhare activity names alag hain, sirf STAGES ke keywords badlo.
"""
import json
import pandas as pd

LOG = "careflow_event_log_clean_sorted.csv"
CASE, ACT, TS = "Case_ID", "Activity_Name", "Timestamp"

# ---------------------------------------------------------------
# DAY 2 - Stages (name, keywords to match activity names, meaning, who)
# ---------------------------------------------------------------
STAGES = [
    ("Registration", ["regist", "admit", "admission"],
     "Patient ka record banta hai aur basic details li jaati hain", "Front desk / reception staff"),
    ("Triage", ["triag"],
     "Severity check hoti hai aur priority decide hoti hai", "Triage nurse"),
    ("Tests", ["test", "lab", "diagnos", "xray", "x-ray", "scan", "imaging"],
     "Triage ke baad X-Ray / imaging hoti hai taaki doctor ke paas report ready ho", "Lab technician / radiology"),
    ("Consultation", ["consult", "doctor", "exam"],
     "Doctor patient ko dekhta hai aur diagnosis / plan banata hai", "Doctor"),
    ("Treatment", ["treat", "medic", "procedure", "therapy", "surgery"],
     "Medicine ya procedure di jaati hai", "Doctor / nurse"),
    ("Discharge", ["discharge"],
     "Patient ko summary ke saath ghar bheja jaata hai", "Doctor / ward staff"),
]
ORDER = [s[0] for s in STAGES]


def stage_of(activity):
    a = str(activity).lower()
    for name, keywords, _, _ in STAGES:
        if any(k in a for k in keywords):
            return name
    return None


# ---------------------------------------------------------------
# DAY 3 - Required vs Optional (stage, clinical reason)
# ---------------------------------------------------------------
REQUIRED = {
    "Registration": "Bina registration ke patient ka record aur billing nahi ban sakta",
    "Triage": "Priority aur severity pata karna safety ke liye zaroori hai (emergency mein skip ho sakta hai)",
    "Consultation": "Diagnosis aur treatment ka decision doctor hi leta hai",
    "Discharge": "Visit officially close hone ke liye discharge zaroori hai",
}
OPTIONAL = {
    "Tests": "Sirf tab hote hain jab doctor ne manga ho",
    "Treatment": "Kuch patients ko sirf advice milti hai, procedure ya medicine nahi",
}


# ---------------------------------------------------------------
# DAY 4 - Allowed order rules (stage level)
# ---------------------------------------------------------------
def rule(a, b):
    """Return (Y/N, reason) for stage a -> stage b."""
    i, j = ORDER.index(a), ORDER.index(b)
    if a == "Discharge":
        return "N", "Discharge ke baad koi step nahi ho sakta"
    if b == "Registration":
        return "N", "Registration sirf sabse pehla step hai"
    if (a, b) == ("Registration", "Consultation"):
        return "Y", "Exception: emergency patient Triage skip kar sakta hai"
    if (a, b) == ("Tests", "Triage"):
        return "N", "Rework loop: X-Ray ke baad dobara Triage (ideal path mein nahi)"
    if a == b:
        if a in ("Tests", "Consultation"):
            return "Y", "Repeat allowed (repeat test / multiple consultations)"
        return "N", "Same step dobara clinically meaningful nahi"
    if j < i:
        return "N", "Backward move: order violation"
    skipped = ORDER[i + 1:j]
    missing_required = [s for s in skipped if s in REQUIRED]
    if missing_required:
        return "N", "Required step skip ho raha hai: " + ", ".join(missing_required)
    return "Y", "Forward move" + (" (optional step skipped)" if skipped else "")


# ---------------------------------------------------------------
# DAY 5 - Edge cases
# ---------------------------------------------------------------
EXCEPTIONS = [
    ("Emergency patient Triage skip kare (Registration -> Consultation)", "Clinical", "Valid, direct doctor ke paas jaata hai"),
    ("Repeat tests", "Clinical", "Valid, result unclear ho ya follow-up test ho"),
    ("Multiple consultations", "Clinical", "Valid, specialist referral ya follow-up"),
    ("X-Ray ke baad dobara Triage, phir X-Ray (rework loop)", "Clinical rework", "Clinically possible (re-assessment ya repeat imaging) par ideal path nahi, conformance mein deviation ginte hain"),
    ("Discharge ke baad koi activity", "Data error", "Visit close ho chuka hai, timestamp ya logging galti"),
    ("Registration pehla step nahi", "Data error", "Missing ya galat sorted event"),
    ("Same timestamp ya reversed order", "Data error", "Sorting ya logging issue"),
]


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("saved:", path)


# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
df = pd.read_csv(LOG)
df[TS] = pd.to_datetime(df[TS])
df = df.sort_values([CASE, TS]).reset_index(drop=True)
activities = sorted(df[ACT].dropna().unique())
act_stage = {a: stage_of(a) for a in activities}
unmatched = [a for a, s in act_stage.items() if s is None]

# Day 2 output
lines = ["# Ideal Pathway Stages", "",
         "| # | Stage | Meaning | Who | Activities in data |", "|---|---|---|---|---|"]
for n, (name, _, meaning, who) in enumerate(STAGES, 1):
    acts = ", ".join(a for a in activities if act_stage[a] == name) or "-"
    lines.append(f"| {n} | {name} | {meaning} | {who} | {acts} |")
lines += ["", "## Unmatched activities (kisi stage se match nahi hui)", ""]
lines += [f"- {a}" for a in unmatched] or ["- None, sab activities match ho gayi"]
write("ideal_pathway_stages.md", "\n".join(lines) + "\n")

# Day 3 output
lines = ["# Required vs Optional Steps", "", "| Step | Type | Clinical reason |", "|---|---|---|"]
lines += [f"| {s} | Required | {r} |" for s, r in REQUIRED.items()]
lines += [f"| {s} | Optional | {r} |" for s, r in OPTIONAL.items()]
write("required_vs_optional.md", "\n".join(lines) + "\n")

# Day 4 output
pairs = df.assign(next_act=df.groupby(CASE)[ACT].shift(-1)).dropna(subset=["next_act"])
seen = pairs.groupby([ACT, "next_act"]).size().to_dict()
rows = []
mapped = [a for a in activities if act_stage[a]]
for a in mapped:
    for b in mapped:
        ok, why = rule(act_stage[a], act_stage[b])
        rows.append({"from": a, "to": b, "allowed": ok, "reason": why,
                     "seen_in_data": seen.get((a, b), 0)})
trans = pd.DataFrame(rows)
trans.to_csv("allowed_transitions.csv", index=False)
print("saved: allowed_transitions.csv")
violations = trans[(trans["allowed"] == "N") & (trans["seen_in_data"] > 0)]

# Day 5 output
lines = ["# Exceptions and Edge Cases", "", "| Situation | Type | Note |", "|---|---|---|"]
lines += [f"| {s} | {t} | {n} |" for s, t, n in EXCEPTIONS]
lines += ["", "## Team review feedback", "",
          "- (Yahan apne teammates ke actual suggestions likho)"]
write("exceptions.md", "\n".join(lines) + "\n")

# Day 6 output
allowed_map = {a: [b for b in ORDER if rule(a, b)[0] == "Y"] for a in ORDER}
forbidden = [[a, b] for a in ORDER for b in ORDER if rule(a, b)[0] == "N"]
rules = {
    "stages": ORDER,
    "required": list(REQUIRED),
    "optional": list(OPTIONAL),
    "first_step": "Registration",
    "last_step": "Discharge",
    "allowed_transitions": allowed_map,
    "forbidden_transitions": forbidden,
    "activity_to_stage": act_stage,
    "exceptions": [{"situation": s, "type": t} for s, t, _ in EXCEPTIONS],
}
with open("ideal_pathway.json", "w", encoding="utf-8") as f:
    json.dump(rules, f, indent=2)
print("saved: ideal_pathway.json")

lines = ["# Ideal Pathway Rules", "",
         "## 1. Stages", "", " -> ".join(ORDER), "",
         "## 2. Required steps", ""]
lines += [f"- {s}: {r}" for s, r in REQUIRED.items()]
lines += ["", "## 3. Optional steps", ""]
lines += [f"- {s}: {r}" for s, r in OPTIONAL.items()]
lines += ["", "## 4. Order rules", "",
          "- Registration sabse pehle, Discharge sabse last",
          "- Triage ke baad Tests (X-Ray), phir Consultation (imaging-first pathway)",
          "- Backward moves allowed nahi (X-Ray -> Triage rework loop deviation hai)",
          "- Required step skip allowed nahi (sirf emergency mein Triage skip)",
          "", "## 5. Exceptions", ""]
lines += [f"- {s} ({t})" for s, t, _ in EXCEPTIONS]
lines += ["", "Machine-readable version: ideal_pathway.json"]
write("ideal_pathway_rules.md", "\n".join(lines) + "\n")

# ---------------------------------------------------------------
# DAY 7 - Validation
# ---------------------------------------------------------------
bad_cases, reasons = 0, {}
n_cases = df[CASE].nunique()
for cid, g in df.groupby(CASE):
    seq = [stage_of(a) for a in g[ACT]]
    problems = []
    if None in seq:
        problems.append("unmatched activity")
    seq = [s for s in seq if s]
    if not seq:
        problems.append("no valid activity")
    else:
        if seq[0] != "Registration":
            problems.append("does not start with Registration")
        if seq[-1] != "Discharge":
            problems.append("does not end with Discharge")
        emergency = any(p == ("Registration", "Consultation") for p in zip(seq, seq[1:]))
        for r in REQUIRED:
            if r not in seq and not (r == "Triage" and emergency):
                problems.append(f"missing required step: {r}")
        for a, b in zip(seq, seq[1:]):
            if rule(a, b)[0] == "N":
                problems.append(f"forbidden transition: {a} -> {b}")
    if problems:
        bad_cases += 1
        for p in set(problems):
            reasons[p] = reasons.get(p, 0) + 1

good = n_cases - bad_cases
report = [
    "VALIDATION REPORT",
    f"Events: {len(df)} | Cases: {n_cases}",
    f"Cases following ideal pathway: {good} ({good / n_cases * 100:.1f}%)",
    f"Cases with deviations: {bad_cases}",
    f"Unmatched activities: {unmatched or 'none'}",
    f"Forbidden transitions seen in data: {len(violations)}",
    "Deviation reasons:",
] + [f"  - {k}: {v}" for k, v in sorted(reasons.items(), key=lambda x: -x[1])]
write("validation_report.txt", "\n".join(report) + "\n")
print("\n".join(report))

readme = f"""# CareFlow Week 4: Ideal Pathway Definition

## Input
- `{LOG}` (Case_ID, Activity_Name, Timestamp)
- Week 3 outputs (`transitions.csv`, `top_variants.csv`) for comparison

## Rules summary
- Stages: {" -> ".join(ORDER)}
- Required: {", ".join(REQUIRED)} | Optional: {", ".join(OPTIONAL)}
- Registration is always first, Discharge always last, no backward moves
- Exceptions: emergency Triage skip, repeat tests, multiple consultations

## Output files
- `ideal_pathway_stages.md`, `required_vs_optional.md`, `allowed_transitions.csv`
- `exceptions.md`, `ideal_pathway_rules.md`, `ideal_pathway.json`
- `validation_report.txt` ({good}/{n_cases} cases follow the ideal pathway)

## Handoff notes for next members
- Use `ideal_pathway.json` directly for conformance checking
  (`allowed_transitions`, `forbidden_transitions`, `activity_to_stage`)
- `allowed_transitions.csv` has a `seen_in_data` column to spot violations quickly
- If activity names change, update the keywords in `STAGES` and rerun the script
"""
write("README_week4.md", readme)