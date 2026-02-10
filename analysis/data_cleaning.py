import pandas as pd
import numpy as np
import re

df = pd.read_csv("data/processed/job_details.csv")
print("Initial shape:", df.shape)

# ================= LOCATION =================
def normalize_location(loc):
    if pd.isna(loc):
        return None
    loc = loc.lower()
    if "hyderabad" in loc:
        return "Hyderabad"
    if "bangalore" in loc or "bengaluru" in loc:
        return "Bengaluru"
    if "chennai" in loc:
        return "Chennai"
    if "mumbai" in loc:
        return "Mumbai"
    return "Other"

df["location_clean"] = df["location"].apply(normalize_location)

# ================= EXPERIENCE =================
def extract_experience(exp):
    if pd.isna(exp):
        return None
    match = re.search(r"(\d+)", exp)
    return int(match.group(1)) if match else None

df["experience_min"] = df["experience"].apply(extract_experience)

def exp_bucket(x):
    if x is None:
        return "Unknown"
    if x <= 2:
        return "Entry"
    if x <= 5:
        return "Mid"
    return "Senior"

df["experience_level"] = df["experience_min"].apply(exp_bucket)

# ================= SALARY =================
def extract_salary(sal):
    if pd.isna(sal):
        return None
    
    sal = str(sal).lower()

    if 'not disclosed' in sal:
        return None

    parts = sal.split('\n')

    for part in parts:
        part = part.strip()

        if 'years' in part and 'lacs' not in part and 'lpa' not in part:
            continue

        match = re.search(r'(\d+)(?:\s*[-–]\s*\d+)?\s*(?:lacs?|lakhs?|lpa)', part)
        if match:
            return int(match.group(1))

    return None

df["salary_lpa_min"] = df["salary"].apply(extract_salary)

# ================= SKILL TAXONOMY =================

ROLE_TERMS = ["data analysis","data analytics","analytics","data analyst"]

CORE_SKILLS = ["sql","python","excel"]
BI_SKILLS = ["power bi","tableau"]
ADVANCED_SKILLS = ["machine learning","statistics"]
CLOUD_SKILLS = ["aws","azure","gcp"]

SKILL_BLACKLIST = [
    "terms & conditions","employer home","summons/notices",
    "website","http","https"
]

# ================= CLEAN SKILL LIST =================
def clean_skill_list(skill_text):
    if pd.isna(skill_text):
        return []

    raw = str(skill_text).lower()

    # split by comma + newline
    parts = re.split(r"[,\n]+", raw)

    cleaned = []

    for p in parts:
        p = p.strip()

        if not p:
            continue

        # 🚨 remove anything containing digits ANYWHERE
        if re.search(r"\d", p):
            continue

        # remove phrases like "1259 reviews"
        if "review" in p:
            continue

        # blacklist junk
        if any(b in p for b in [
            "terms & conditions",
            "terms and conditions",
            "employer home",
            "summons/notices",
            "notices",
            "website",
            "http",
            "https"
        ]):
            continue

        # normalize aliases
        if p in ["data analyst","data analytics","analytics"]:
            p = "data analysis"

        if p == "bi":
            p = "power bi"

        # remove very short junk
        if len(p) < 2:
            continue

        cleaned.append(p)

    # remove duplicates
    cleaned = list(set(cleaned))

    return cleaned



df["skill_list"] = df["key_skills"].apply(clean_skill_list)

# overwrite key_skills with cleaned version
df["key_skills"] = df["skill_list"].apply(
    lambda x: ", ".join(sorted(x)) if x else None
)


# ================= ROLE FLAG =================
def check_role(skills):
    for s in skills:
        if any(term in s for term in ROLE_TERMS):
            return 1
    return 0

df["is_data_role"] = df["skill_list"].apply(check_role)

# ================= BINARY TOOL COLUMNS =================
def has_skill(skill_list, keywords):
    for s in skill_list:
        for k in keywords:
            if k in s:
                return 1
    return 0

df["SQL"] = df["skill_list"].apply(lambda x: has_skill(x, ["sql"]))
df["Python"] = df["skill_list"].apply(lambda x: has_skill(x, ["python"]))
df["Excel"] = df["skill_list"].apply(lambda x: has_skill(x, ["excel"]))

df["Power BI"] = df["skill_list"].apply(lambda x: has_skill(x, ["power bi"]))
df["Tableau"] = df["skill_list"].apply(lambda x: has_skill(x, ["tableau"]))

df["Machine Learning"] = df["skill_list"].apply(lambda x: has_skill(x, ["machine learning"]))
df["Statistics"] = df["skill_list"].apply(lambda x: has_skill(x, ["statistics"]))

df["AWS"] = df["skill_list"].apply(lambda x: has_skill(x, ["aws"]))
df["Azure"] = df["skill_list"].apply(lambda x: has_skill(x, ["azure"]))

df["Data visualization"] = df["skill_list"].apply(
    lambda x: has_skill(x, ["data visualization","visualization","dashboard","reporting"])
)

df["Data Analysis"] = df["skill_list"].apply(
    lambda x: 1 if any(s in x for s in ["data analysis"]) else 0
)

# ================= SCORES =================
df["core_tools_score"] = df[["SQL","Python","Excel"]].sum(axis=1)
df["bi_tools_score"] = df[["Power BI","Tableau"]].sum(axis=1)
df["advanced_score"] = df[["Machine Learning","Statistics"]].sum(axis=1)
df["cloud_score"] = df[["AWS","Azure"]].sum(axis=1)

# ================= SAVE =================
df.to_csv("data/processed/job_details_cleaned.csv", index=False)

print("Final shape:", df.shape)
print("Cleaned file saved.")
