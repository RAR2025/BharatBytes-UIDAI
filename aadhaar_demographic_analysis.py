"""
AADHAAR DEMOGRAPHIC DATA ANALYSIS
Covers all five demographic CSV shards as one logical table.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# -----------------------------------------------------------------------------
# 1) LOAD CONSOLIDATED DATA
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print("AADHAAR DEMOGRAPHIC DATA ANALYSIS")
print("="*80)

CSV_FILE = r"filtered_data/consolidated_demographic.csv"

print(f"Loading consolidated demographic data...")
raw = pd.read_csv(CSV_FILE)
print(f"Loaded consolidated_demographic.csv: {raw.shape[0]:,} rows, {raw.shape[1]} cols")

# Normalize types
raw["date"] = pd.to_datetime(raw["date"], format="%d-%m-%Y")
raw["total_demo"] = raw["demo_age_5_17"] + raw["demo_age_17_"]

print("\nBASIC SHAPE AND RANGE")
print(f"Rows: {len(raw):,}")
print(f"Columns: {raw.shape[1]}")
print(f"Date range: {raw['date'].min().date()} -> {raw['date'].max().date()}")
print(f"States: {raw['state'].nunique()} | Districts: {raw['district'].nunique()} | Pincodes: {raw['pincode'].nunique()}")
print("Sample:")
print(raw.head(5))

# -----------------------------------------------------------------------------
# 2) TIME TRENDS (GROWTH, SPIKES)
# -----------------------------------------------------------------------------
raw["year"] = raw["date"].dt.year
raw["month"] = raw["date"].dt.month
raw["week"] = raw["date"].dt.isocalendar().week
raw["dow"] = raw["date"].dt.day_name()

daily = raw.groupby("date")["total_demo"].sum().sort_index()
monthly = raw.groupby(raw["date"].dt.to_period("M"))["total_demo"].sum()

print("\nTIME PATTERNS")
print("Top 5 daily volumes (possible drives):")
print(daily.sort_values(ascending=False).head(5))

mean_d = daily.mean(); std_d = daily.std()
spike_threshold = mean_d + 2*std_d
spikes = daily[daily > spike_threshold]
print(f"Spike threshold (mean+2σ): {spike_threshold:,.0f}; spike days: {len(spikes)}")
if len(spikes):
    print(spikes.head(10))

print("\nMonthly totals:")
print(monthly)

# -----------------------------------------------------------------------------
# 3) GEOGRAPHIC DISTRIBUTION (STATE / DISTRICT)
# -----------------------------------------------------------------------------
state_totals = raw.groupby("state")["total_demo"].sum().sort_values(ascending=False)
state_cum = state_totals.cumsum() / state_totals.sum() * 100
states_80 = state_cum[state_cum <= 80].shape[0]

district_totals = raw.groupby(["state", "district"])["total_demo"].sum().sort_values(ascending=False)

top_states = state_totals.head(10)
top_districts = district_totals.head(15)

print("\nGEOGRAPHIC CONCENTRATION")
print("Top 10 states by demographic counts:")
print(top_states)
print(f"States covering 80% of population counts: {states_80} of {len(state_totals)}")

print("Top 15 districts:")
print(top_districts)

# District concentration ratios
n_districts = len(district_totals)
top10pct_n = max(1, int(n_districts * 0.10))
bot50pct_n = max(1, int(n_districts * 0.50))
top10pct_share = district_totals.head(top10pct_n).sum() / district_totals.sum() * 100
bot50pct_share = district_totals.tail(bot50pct_n).sum() / district_totals.sum() * 100

print(f"District concentration: top 10% = {top10pct_share:.1f}% | bottom 50% = {bot50pct_share:.1f}%")

# -----------------------------------------------------------------------------
# 4) AGE STRUCTURE (DEPENDENCY, MATURITY)
# -----------------------------------------------------------------------------
age_5_17 = raw["demo_age_5_17"].sum()
age_17_plus = raw["demo_age_17_"].sum()
total_age = age_5_17 + age_17_plus

print("\nAGE STRUCTURE")
print(f"5-17 years: {age_5_17:,} ({age_5_17/total_age*100:.1f}%)")
print(f"17+ years: {age_17_plus:,} ({age_17_plus/total_age*100:.1f}%)")
print(f"Total counts: {total_age:,}")

# Dependency proxy: youth-to-adult ratio by district
ratio = raw.groupby(["state", "district"]).agg({"demo_age_5_17": "sum", "demo_age_17_": "sum"})
ratio["youth_to_adult"] = ratio["demo_age_5_17"] / ratio["demo_age_17_"].replace(0, np.nan)
ratio = ratio.dropna(subset=["youth_to_adult"])
print("\nHighest youth-to-adult ratios (top 10 districts):")
print(ratio.sort_values("youth_to_adult", ascending=False).head(10)["youth_to_adult"])

print("Lowest youth-to-adult ratios (top 10 aging districts):")
print(ratio.sort_values("youth_to_adult").head(10)["youth_to_adult"])

# -----------------------------------------------------------------------------
# 5) GROWTH & SHIFT OVER TIME (EARLY VS LATE)
# -----------------------------------------------------------------------------
cutoff = raw["date"].median()
early = raw[raw["date"] <= cutoff]
late = raw[raw["date"] > cutoff]

early_states = early.groupby("state")["total_demo"].sum().nlargest(10)
late_states = late.groupby("state")["total_demo"].sum().nlargest(10)

print("\nGEOGRAPHIC SHIFT (early vs late period)")
print(f"Cutoff date: {cutoff.date()}")
print("Early top states:")
print(early_states)
print("Late top states:")
print(late_states)

new_late_states = set(late_states.index) - set(early_states.index)
if new_late_states:
    print(f"States emerging in late period: {', '.join(new_late_states)}")

# -----------------------------------------------------------------------------
# 6) DATA QUALITY & ANOMALIES
# -----------------------------------------------------------------------------
print("\nDATA QUALITY")
# Exact duplicates
dupes = raw.duplicated(subset=["date", "state", "district", "pincode", "demo_age_5_17", "demo_age_17_"])
print(f"Exact duplicate rows: {dupes.sum():,}")

# Missing values
for col in ["date", "state", "district", "pincode", "demo_age_5_17", "demo_age_17_"]:
    miss = raw[col].isna().sum()
    if miss:
        print(f"Missing {col}: {miss}")

# Zero-count records
zero_rows = raw[raw["total_demo"] == 0]
print(f"Zero-count rows: {len(zero_rows):,}")

# Suspicious high single-row values
high_5_17 = raw[raw["demo_age_5_17"] > 500]
high_17 = raw[raw["demo_age_17_"] > 5000]
print(f"Rows with demo_age_5_17 > 500: {len(high_5_17):,}")
print(f"Rows with demo_age_17_ > 5,000: {len(high_17):,}")
if len(high_5_17):
    print(high_5_17.nlargest(5, "demo_age_5_17")[["date", "state", "district", "demo_age_5_17", "demo_age_17_"]])
if len(high_17):
    print(high_17.nlargest(5, "demo_age_17_")[["date", "state", "district", "demo_age_5_17", "demo_age_17_"]])

# -----------------------------------------------------------------------------
# 7) MERGE-READY NOTES (FOR ENROLMENT + DEMOGRAPHIC JOIN)
# -----------------------------------------------------------------------------
print("\nMERGE-READY KEYS")
print("Use ['date','state','district','pincode'] as join keys against enrolment data.")
print("Measures here: demo_age_5_17, demo_age_17_, total_demo")

print("\nAnalysis complete.")
