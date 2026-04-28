import pandas as pd
import re
import pickle
from sklearn.linear_model import LinearRegression

# -------- CLEAN FUNCTION --------
def convert_days(val):
    if pd.isna(val):
        return 0
    val = str(val).lower()

    if "week" in val:
        return float(re.findall(r'\d+', val)[0]) * 7
    elif "month" in val:
        return float(re.findall(r'\d+', val)[0]) * 30
    elif "--" in val:
        nums = re.findall(r'\d+', val)
        return (float(nums[0]) + float(nums[1])) / 2
    else:
        nums = re.findall(r'\d+', val)
        return float(nums[0]) if nums else 0

def yes_no(val):
    if str(val).lower() == "yes":
        return 1
    elif str(val).lower() == "no":
        return 0
    return 0

# -------- LOAD CSV --------
df = pd.read_csv("dengue.csv")

# -------- RENAME COLUMNS --------
df.columns = [c.replace("dengue.", "") for c in df.columns]

# -------- CLEAN DATA --------
df["days"] = df["days"].apply(convert_days)

cols_yes_no = [
    "servere_headche","pain_behind_the_eyes","joint_muscle_aches",
    "metallic_taste_in_the_mouth","appetite_loss","addominal_pain",
    "nausea_vomiting","diarrhoea","dengue"
]

for col in cols_yes_no:
    df[col] = df[col].apply(yes_no)

# Convert numeric columns
num_cols = ["current_temp","wbc","hemoglobin","_hematocri","platelet"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -------- FEATURES --------
X = df[[
    "days","current_temp","wbc",
    "servere_headche","pain_behind_the_eyes","joint_muscle_aches",
    "metallic_taste_in_the_mouth","appetite_loss","addominal_pain",
    "nausea_vomiting","diarrhoea",
    "hemoglobin","_hematocri","platelet"
]]

y = df["dengue"]

# -------- TRAIN MODEL --------
model = LinearRegression()
model.fit(X, y)

# -------- SAVE MODEL --------
pickle.dump(model, open("linear_model.pkl", "wb"))

print("✅ Linear Model Saved!")