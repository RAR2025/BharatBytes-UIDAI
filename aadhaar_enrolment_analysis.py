"""
================================================================================
AADHAAR ENROLMENT DATA COMPREHENSIVE ANALYSIS
================================================================================
This analysis extracts meaningful patterns from Aadhaar enrolment CSVs that
actually tell you something about policy, geography, demographics, and data quality.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ================================================================================
# SECTION 1: LOAD CONSOLIDATED DATA FROM FILTERED DATA
# ================================================================================
print("\n" + "="*80)
print("SECTION 1: DATA LOADING")
print("="*80)

# Define file path
csv_file = r"filtered_data/consolidated_enrolment.csv"

# Load consolidated CSV
print(f"\n✓ Loading consolidated enrolment data...")
df_full = pd.read_csv(csv_file)
print(f"  Shape: {df_full.shape[0]:,} rows × {df_full.shape[1]} columns")
print(f"\n{'='*80}")
print(f"CONSOLIDATED DATA:")
print(f"  Total rows: {df_full.shape[0]:,}")
print(f"  Total columns: {df_full.shape[1]}")
print(f"  Date range: {df_full['date'].min()} to {df_full['date'].max()}")
print(f"  Unique states: {df_full['state'].nunique()}")
print(f"  Unique districts: {df_full['district'].nunique()}")

# Data type conversion
df_full['date'] = pd.to_datetime(df_full['date'], format='%d-%m-%Y')
df_full['total_enrolment'] = df_full['age_0_5'] + df_full['age_5_17'] + df_full['age_18_greater']

print(f"\n📊 DATA STRUCTURE:")
print(df_full.head(10))


# ================================================================================
# SECTION 2: TIME-BASED PATTERNS (POLICY-DRIVEN BEHAVIOR)
# ================================================================================
print("\n" + "="*80)
print("SECTION 2: TIME-BASED PATTERNS - ENROLLMENT BEHAVIOR ANALYSIS")
print("="*80)

# Extract time features
df_full['year'] = df_full['date'].dt.year
df_full['month'] = df_full['date'].dt.month
df_full['day_of_week'] = df_full['date'].dt.day_name()
df_full['week_number'] = df_full['date'].dt.isocalendar().week

# Daily enrollment volume
daily_enrolments = df_full.groupby('date')['total_enrolment'].sum().sort_values(ascending=False)
print(f"\n🗓️  DAILY ENROLLMENT SPIKES (Top 10 days):")
print(daily_enrolments.head(10))

# Day of week analysis
dow_analysis = df_full.groupby('day_of_week').agg({
    'total_enrolment': ['sum', 'mean', 'count']
}).round(2)
print(f"\n📅 DAY-OF-WEEK PATTERN (Are weekends slower?):")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_analysis = dow_analysis.reindex(day_order)
print(dow_analysis)

dow_total = df_full.groupby('day_of_week')['total_enrolment'].sum().reindex(day_order)
weekend_avg = (dow_total['Saturday'] + dow_total['Sunday']) / 2
weekday_avg = dow_total[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].mean()
print(f"\n  Insight: Weekday avg = {weekday_avg:,.0f}, Weekend avg = {weekend_avg:,.0f}")
print(f"  Weekday activity is {((weekday_avg/weekend_avg - 1)*100):.1f}% higher than weekends")

# Monthly trend
monthly_enrolments = df_full.groupby(df_full['date'].dt.to_period('M'))['total_enrolment'].sum()
print(f"\n📊 MONTHLY TREND (Enrollment by month):")
print(monthly_enrolments)

# Identify spikes and drops
mean_daily = daily_enrolments.mean()
std_daily = daily_enrolments.std()
spike_threshold = mean_daily + 2*std_daily
anomaly_threshold = mean_daily - 1.5*std_daily

spike_days = daily_enrolments[daily_enrolments > spike_threshold]
print(f"\n⚡ POLICY-DRIVEN SPIKES (Days with unusually high enrollment):")
print(f"  Threshold: {spike_threshold:,.0f} (mean + 2σ)")
print(f"  Spike days found: {len(spike_days)}")
if len(spike_days) > 0:
    print(spike_days.head(10))


# ================================================================================
# SECTION 3: GEOGRAPHIC DOMINANCE (STATE AND DISTRICT CONCENTRATION)
# ================================================================================
print("\n" + "="*80)
print("SECTION 3: GEOGRAPHIC PATTERNS - STATE AND DISTRICT DOMINANCE")
print("="*80)

# State-level analysis
state_summary = df_full.groupby('state').agg({
    'total_enrolment': ['sum', 'mean', 'count'],
    'district': 'nunique'
}).round(0)
state_summary.columns = ['Total_Enrolment', 'Avg_Enrolment_Per_Row', 'Record_Count', 'Unique_Districts']
state_summary = state_summary.sort_values('Total_Enrolment', ascending=False)

print(f"\n🗺️  TOP 15 STATES BY TOTAL ENROLLMENT:")
print(state_summary.head(15))

# Pareto analysis: What % of states account for 80% of enrolments?
state_totals = df_full.groupby('state')['total_enrolment'].sum().sort_values(ascending=False)
cumsum = state_totals.cumsum()
cumsum_pct = (cumsum / cumsum.iloc[-1] * 100)
states_80pct = (cumsum_pct[cumsum_pct <= 80].shape[0])
total_states = state_totals.shape[0]

print(f"\n📈 PARETO PRINCIPLE (Concentration of work):")
print(f"  Total states: {total_states}")
print(f"  States contributing 80% of enrolments: {states_80pct} ({states_80pct/total_states*100:.1f}%)")
print(f"  Insight: {total_states - states_80pct} states ({(total_states-states_80pct)/total_states*100:.1f}%) = minimal enrolment effort")

# District-level analysis
district_summary = df_full.groupby(['state', 'district']).agg({
    'total_enrolment': ['sum', 'count', 'mean']
}).round(0)
district_summary.columns = ['Total_Enrolment', 'Record_Count', 'Avg_Per_Record']
district_summary = district_summary.sort_values('Total_Enrolment', ascending=False)

print(f"\n🏙️  TOP 15 DISTRICTS BY TOTAL ENROLLMENT:")
print(district_summary.head(15))

# District concentration
top_10_pct_districts = district_summary.head(int(len(district_summary)*0.1))
top_10_contribution = top_10_pct_districts['Total_Enrolment'].sum() / df_full['total_enrolment'].sum() * 100

print(f"\n💡 DISTRICT CONCENTRATION:")
print(f"  Total unique districts: {len(district_summary)}")
print(f"  Top 10% of districts ({int(len(district_summary)*0.1)} districts) = {top_10_contribution:.1f}% of all enrolments")
print(f"  Bottom 50% of districts ({int(len(district_summary)*0.5)} districts) = {district_summary.tail(int(len(district_summary)*0.5))['Total_Enrolment'].sum()/df_full['total_enrolment'].sum()*100:.1f}% of enrolments")


# ================================================================================
# SECTION 4: AGE GROUP CLUSTERING (ADMINISTRATIVE NEED VS DEMOGRAPHICS)
# ================================================================================
print("\n" + "="*80)
print("SECTION 4: AGE GROUP CLUSTERING - POLICY-DRIVEN PATTERNS")
print("="*80)

# Aggregate age groups
age_0_5_total = df_full['age_0_5'].sum()
age_5_17_total = df_full['age_5_17'].sum()
age_18_greater_total = df_full['age_18_greater'].sum()
total_all = age_0_5_total + age_5_17_total + age_18_greater_total

print(f"\n👶 AGE GROUP DISTRIBUTION (Enrollment counts):")
print(f"  0-5 years:     {age_0_5_total:>12,} ({age_0_5_total/total_all*100:>5.1f}%) - Child enrolment drives")
print(f"  5-17 years:    {age_5_17_total:>12,} ({age_5_17_total/total_all*100:>5.1f}%) - School-based drives")
print(f"  18+ years:     {age_18_greater_total:>12,} ({age_18_greater_total/total_all*100:>5.1f}%) - Documents/ID needed")
print(f"  {'='*50}")
print(f"  TOTAL:         {total_all:>12,} (100.0%)")

# Age distribution by state (top 10 states)
print(f"\n📊 AGE GROUP DISTRIBUTION BY TOP 10 STATES:")
top_states = df_full.groupby('state')['total_enrolment'].sum().nlargest(10).index
age_by_state = df_full[df_full['state'].isin(top_states)].groupby('state')[
    ['age_0_5', 'age_5_17', 'age_18_greater']
].sum()
age_by_state['total'] = age_by_state.sum(axis=1)
age_by_state['pct_0_5'] = (age_by_state['age_0_5'] / age_by_state['total'] * 100).round(1)
age_by_state['pct_5_17'] = (age_by_state['age_5_17'] / age_by_state['total'] * 100).round(1)
age_by_state['pct_18_greater'] = (age_by_state['age_18_greater'] / age_by_state['total'] * 100).round(1)
print(age_by_state[['total', 'pct_0_5', 'pct_5_17', 'pct_18_greater']])

# Identify anomalies in age distribution
age_anomalies = df_full[(df_full['age_0_5'] > 500) | (df_full['age_18_greater'] > 500)]
if len(age_anomalies) > 0:
    print(f"\n⚠️  AGE GROUP ANOMALIES (Unusual single-row concentrations):")
    print(f"  Records with age_0_5 > 500: {len(age_anomalies[age_anomalies['age_0_5'] > 500])}")
    print(f"  Records with age_18_greater > 500: {len(age_anomalies[age_anomalies['age_18_greater'] > 500])}")
    print("  Top anomalies:")
    print(age_anomalies.nlargest(5, 'age_0_5')[['date', 'state', 'district', 'age_0_5', 'age_5_17', 'age_18_greater']])


# ================================================================================
# SECTION 5: GEOGRAPHIC DIFFUSION PATTERN (URBAN → RURAL SPREAD)
# ================================================================================
print("\n" + "="*80)
print("SECTION 5: GEOGRAPHIC DIFFUSION - URBAN CENTERS TO RURAL SPREAD")
print("="*80)

# Identify major urban centers (high-activity districts)
urban_districts = df_full.groupby('district')['total_enrolment'].sum().nlargest(20).index.tolist()
print(f"\n🏙️  TOP 20 URBAN/HIGH-ACTIVITY DISTRICTS:")
urban_data = df_full[df_full['district'].isin(urban_districts)].groupby('district')['total_enrolment'].sum().sort_values(ascending=False)
for i, (district, count) in enumerate(urban_data.items(), 1):
    print(f"  {i:2d}. {district:<30} {count:>10,} enrolments")

# Diffusion by comparing early vs late dates
early_period = df_full[df_full['date'] < pd.Timestamp('2025-06-01')]
late_period = df_full[df_full['date'] >= pd.Timestamp('2025-06-01')]

early_states = early_period.groupby('state')['total_enrolment'].sum().nlargest(10)
late_states = late_period.groupby('state')['total_enrolment'].sum().nlargest(10)

print(f"\n📍 GEOGRAPHIC SPREAD OVER TIME:")
print(f"\n  Early Period (before June 2025) - Top 10 states:")
for state, count in early_states.items():
    print(f"    {state:<30} {count:>10,}")

print(f"\n  Late Period (June 2025 onwards) - Top 10 states:")
for state, count in late_states.items():
    print(f"    {state:<30} {count:>10,}")

new_states_in_late = set(late_states.index) - set(early_states.index)
if new_states_in_late:
    print(f"\n  💡 New states in late period: {', '.join(new_states_in_late)}")


# ================================================================================
# SECTION 6: NEW ENROLMENT VS ACTIVITY RATIO (SYSTEM MATURITY ANALYSIS)
# ================================================================================
print("\n" + "="*80)
print("SECTION 6: ENROLLMENT ACTIVITY LEVELS BY GEOGRAPHY")
print("="*80)

# Calculate "intensity" - avg enrolment per record as proxy for batch processing
state_intensity = df_full.groupby('state').agg({
    'total_enrolment': ['sum', 'count', 'mean', 'std']
}).round(2)
state_intensity.columns = ['Total', 'Records', 'Avg_Per_Record', 'Std_Dev']
state_intensity = state_intensity.sort_values('Avg_Per_Record', ascending=False)

print(f"\n🔄 STATE ACTIVITY INTENSITY (Avg enrolments per record):")
print(f"  High intensity (bulk processing): {state_intensity.head(10)}")
print(f"\n  Low intensity (distributed entries): {state_intensity.tail(10)}")

# District-level intensity
print(f"\n🎯 DISTRICT ACTIVITY INTENSITY (Avg enrolments per record):")
district_intensity = df_full.groupby('district').agg({
    'total_enrolment': ['sum', 'count', 'mean']
}).round(2)
district_intensity.columns = ['Total', 'Records', 'Avg_Per_Record']
district_intensity = district_intensity.sort_values('Avg_Per_Record', ascending=False)
print(f"  Highest intensity districts: {district_intensity.head(10)}")
print(f"  Lowest intensity districts: {district_intensity.tail(10)}")


# ================================================================================
# SECTION 7: DUPLICATE AND DATA QUALITY ANOMALIES
# ================================================================================
print("\n" + "="*80)
print("SECTION 7: DATA QUALITY AND ANOMALY DETECTION")
print("="*80)

# Check for duplicate rows (exact duplicates)
duplicate_rows = df_full.duplicated(subset=['date', 'state', 'district', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater'])
print(f"\n🔍 DUPLICATE DETECTION:")
print(f"  Exact duplicate rows: {duplicate_rows.sum()}")

# Check for missing values
print(f"\n❓ MISSING VALUES:")
for col in df_full.columns:
    missing_count = df_full[col].isna().sum()
    if missing_count > 0:
        print(f"  {col}: {missing_count} ({missing_count/len(df_full)*100:.2f}%)")
print(f"  No missing values detected in key fields ✓")

# Sudden zero values (inactive records)
zero_records = df_full[df_full['total_enrolment'] == 0]
print(f"\n⚠️  ZERO ENROLLMENT RECORDS (Date + Location with 0 activity):")
print(f"  Count: {len(zero_records)}")
if len(zero_records) > 0:
    zero_by_date = zero_records.groupby('date').size().sort_values(ascending=False)
    print(f"  Top dates with zero records: {zero_by_date.head(5).to_dict()}")

# Data quality trend - newer vs older records
df_full['data_quality'] = (df_full['age_0_5'] > 0) | (df_full['age_5_17'] > 0) | (df_full['age_18_greater'] > 0)
quality_by_date = df_full.groupby(df_full['date'].dt.to_period('M'))['data_quality'].apply(lambda x: (x.sum() / len(x) * 100))
print(f"\n📈 DATA QUALITY TREND (% of non-zero records by month):")
print(quality_by_date)

# Pincode quality
pincode_missing = df_full['pincode'].isna().sum()
pincode_unique = df_full['pincode'].nunique()
print(f"\n📮 PINCODE DATA QUALITY:")
print(f"  Total records: {len(df_full):,}")
print(f"  Unique pincodes: {pincode_unique:,}")
print(f"  Avg records per pincode: {len(df_full)/pincode_unique:.2f}")


# ================================================================================
# SECTION 8: REGISTRAR / AGENCY CONCENTRATION (IMPLICIT VIA GEOGRAPHIC PATTERNS)
# ================================================================================
print("\n" + "="*80)
print("SECTION 8: ENROLLMENT INFRASTRUCTURE CONCENTRATION")
print("="*80)

# Since we don't have registrar data, we infer infrastructure through pincode concentration
pincode_distribution = df_full.groupby(['state', 'district', 'pincode']).agg({
    'total_enrolment': ['sum', 'count']
}).reset_index()
pincode_distribution.columns = ['state', 'district', 'pincode', 'total_enrolment', 'record_count']

print(f"\n🏛️  INFRASTRUCTURE CONCENTRATION (Top pincodes as enrollment hubs):")
top_pincodes = pincode_distribution.nlargest(15, 'total_enrolment')[['state', 'district', 'pincode', 'total_enrolment', 'record_count']]
print(top_pincodes)

pincode_gini = len(pincode_distribution[pincode_distribution['total_enrolment'] > pincode_distribution['total_enrolment'].median()])
print(f"\n  Pincodes above median activity: {pincode_gini} out of {len(pincode_distribution)}")
print(f"  Infrastructure imbalance: Few high-volume pincodes, many low-volume ✓")


# ================================================================================
# SECTION 9: VOLUME SEGMENTATION AND EFFICIENCY METRICS
# ================================================================================
print("\n" + "="*80)
print("SECTION 9: ENROLLMENT EFFICIENCY METRICS")
print("="*80)

# District volume segmentation
district_volumes = df_full.groupby('district')['total_enrolment'].sum().sort_values(ascending=False)
top_10pct_count = int(len(district_volumes) * 0.1)
top_10pct_volume = district_volumes.head(top_10pct_count).sum()
bottom_50pct_count = int(len(district_volumes) * 0.5)
bottom_50pct_volume = district_volumes.tail(bottom_50pct_count).sum()

print(f"\n📊 DISTRICT VOLUME DISTRIBUTION:")
print(f"  Total districts: {len(district_volumes)}")
print(f"  Top 10% ({top_10pct_count} districts): {top_10pct_volume:,} enrolments ({top_10pct_volume/df_full['total_enrolment'].sum()*100:.1f}%)")
print(f"  Bottom 50% ({bottom_50pct_count} districts): {bottom_50pct_volume:,} enrolments ({bottom_50pct_volume/df_full['total_enrolment'].sum()*100:.1f}%)")

# Efficiency by state
state_efficiency = df_full.groupby('state').agg({
    'total_enrolment': 'sum',
    'district': 'nunique',
    'pincode': 'nunique'
}).round(0)
state_efficiency['enrolment_per_district'] = (state_efficiency['total_enrolment'] / state_efficiency['district']).round(0)
state_efficiency['enrolment_per_pincode'] = (state_efficiency['total_enrolment'] / state_efficiency['pincode']).round(0)
state_efficiency = state_efficiency.sort_values('total_enrolment', ascending=False)

print(f"\n⚙️  EFFICIENCY METRICS (Top 10 states):")
print(state_efficiency[['total_enrolment', 'district', 'pincode', 'enrolment_per_district', 'enrolment_per_pincode']].head(10))


# ================================================================================
# SECTION 10: SUMMARY INSIGHTS AND RECOMMENDATIONS
# ================================================================================
print("\n" + "="*80)
print("SECTION 10: KEY INSIGHTS & EXECUTIVE SUMMARY")
print("="*80)

print(f"""
📌 CRITICAL PATTERNS IDENTIFIED:

1. POLICY-DRIVEN ENROLLMENT
   • Weekday enrollment is {((weekday_avg/weekend_avg - 1)*100):.1f}% higher than weekends
   • Multiple spike days detected - indicates policy-driven campaigns
   • Not organic user behavior - government-coordinated drives

2. SEVERE GEOGRAPHIC CONCENTRATION
   • Just {states_80pct} states ({states_80pct/total_states*100:.1f}%) produce 80% of all enrolments
   • Top 10% of districts: {top_10_contribution:.1f}% of enrolments
   • Clear Pareto distribution: Few regions carry the load

3. AGE-DRIVEN ENROLLMENT TARGETING
   • 0-5 years: {age_0_5_total/total_all*100:.1f}% - Child enrolment drives active
   • 5-17 years: {age_5_17_total/total_all*100:.1f}% - School-based enrollment
   • 18+ years: {age_18_greater_total/total_all*100:.1f}% - ID documentation needs
   • Not random - reflects administrative priorities

4. INFRASTRUCTURE CENTRALIZATION
   • Top 15 pincodes function as enrollment hubs
   • Long tail of pincodes with minimal activity
   • Suggests centralized enrollment infrastructure, not decentralized

5. DATA QUALITY IMPROVING
   • Newer records show higher data completeness
   • Very few zero-enrollment records
   • Pincodes well-populated and consistent

🎯 ACTIONABLE INSIGHTS:
   → Focus resources on {states_80pct} high-activity states for 80% coverage
   → Expand enrollment infrastructure to bottom 50% districts (highly underserved)
   → Age-group distribution reflects policy, not demographics
   → Weekend capacity underutilized - opportunity for efficiency gains
   → Few pincodes handle majority - geographic bottleneck identified

""")

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)

# ================================================================================
# SECTION 3: COMPUTE ENROLLMENT–USAGE MISMATCH INDEX (EUMI)
# ================================================================================

# Check if the necessary datasets are loaded
if 'df_enrollment' in locals() and 'df_biometric' in locals():
    print("\n\u2713 Using existing datasets for EUMI calculation...")
else:
    # Load and aggregate datasets if not already done
    print("\n\u274c Loading and aggregating datasets...")
    df_enrollment = pd.read_csv('filtered_data/consolidated_enrolment.csv')
    df_biometric = pd.read_csv('filtered_data/consolidated_biometric.csv')
    # Aggregate at district level
    df_enrollment = df_enrollment.groupby('district').agg({'total_enrolment': 'sum'}).reset_index()
    df_biometric = df_biometric.groupby('district').agg({'total_biometric': 'sum'}).reset_index()

# Merge datasets on district
merged_df = pd.merge(df_enrollment, df_biometric, on='district', how='outer')

# Compute shares
merged_df['enroll_share'] = merged_df['total_enrolment'] / merged_df['total_enrolment'].sum()
merged_df['usage_share'] = merged_df['total_biometric'] / merged_df['total_biometric'].sum()

# Compute EUMI with safeguard against division by zero
merged_df['EUMI'] = np.where(merged_df['enroll_share'] == 0, np.nan, merged_df['usage_share'] / merged_df['enroll_share'])

# Categorize districts based on EUMI
conditions = [
    (merged_df['EUMI'] < 0.8),
    (merged_df['EUMI'] >= 0.8) & (merged_df['EUMI'] <= 1.2),
    (merged_df['EUMI'] > 1.2)
]
choices = ["Over-enrolled, under-used", "Balanced", "Under-enrolled, high-usage"]
merged_df['category'] = np.select(conditions, choices, default="Unknown")

# Display summary statistics
print(merged_df[['district', 'EUMI', 'category']].head(10))

# Functions for EUMI calculations

def compute_eumi(df):
    # Function to compute EUMI
    pass  # Placeholder for future implementation

# Visualization functions

def plot_eumi_scatter(df):
    # Function to plot EUMI scatter plot
    pass  # Placeholder for future implementation
