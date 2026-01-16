"""
================================================================================
AADHAAR BIOMETRIC DATA COMPREHENSIVE ANALYSIS
================================================================================
Analysis of biometric authentication patterns by age group. Reveals usage patterns,
system behavior, demographic engagement, and regional differences.
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
csv_file = r"filtered_data/consolidated_biometric.csv"

# Load consolidated CSV
print(f"\n✓ Loading consolidated biometric data...")
df_full = pd.read_csv(csv_file)
print(f"  Shape: {df_full.shape[0]:,} rows × {df_full.shape[1]} columns")
print(f"\n{'='*80}")
print(f"CONSOLIDATED DATA:")
print(f"  Total rows: {df_full.shape[0]:,}")
print(f"  Total columns: {df_full.shape[1]}")
print(f"  Date range: {df_full['date'].min()} to {df_full['date'].max()}")
print(f"  Unique states: {df_full['state'].nunique()}")
print(f"  Unique districts: {df_full['district'].nunique()}")
print(f"  Unique pincodes: {df_full['pincode'].nunique()}")

# Data type conversion
df_full['date'] = pd.to_datetime(df_full['date'], format='%d-%m-%Y')
df_full['total_biometric'] = df_full['bio_age_5_17'] + df_full['bio_age_17_']

print(f"\n📊 DATA STRUCTURE:")
print(df_full.head(10))

print(f"\n📋 COLUMN SUMMARY:")
print(df_full.info())


# ================================================================================
# SECTION 2: AGE-BASED BIOMETRIC ANALYSIS - OVERALL PATTERNS
# ================================================================================
print("\n" + "="*80)
print("SECTION 2: AGE-BASED BIOMETRIC USAGE PATTERNS")
print("="*80)

# Overall biometric counts by age group
total_youth = df_full['bio_age_5_17'].sum()
total_adult = df_full['bio_age_17_'].sum()
total_all = total_youth + total_adult

print(f"\n🔢 TOTAL BIOMETRIC TRANSACTIONS BY AGE GROUP:")
print(f"  Youth (5-17):    {total_youth:,} ({total_youth/total_all*100:.2f}%)")
print(f"  Adult (17+):     {total_adult:,} ({total_adult/total_all*100:.2f}%)")
print(f"  TOTAL:           {total_all:,}")

# Calculate age engagement ratios
youth_to_adult_ratio = total_youth / total_adult if total_adult > 0 else np.inf
print(f"\n📊 AGE ENGAGEMENT RATIO:")
print(f"  Youth-to-Adult ratio: {youth_to_adult_ratio:.3f}")
print(f"  Interpretation: For every adult biometric transaction, {youth_to_adult_ratio:.2f} youth transactions occur")

# Per-day averages
df_full['year'] = df_full['date'].dt.year
df_full['month'] = df_full['date'].dt.month
df_full['day_of_week'] = df_full['date'].dt.day_name()
df_full['week_number'] = df_full['date'].dt.isocalendar().week

daily_avg = df_full.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum().mean()
print(f"\n📅 DAILY AVERAGE TRANSACTIONS:")
print(f"  Youth (5-17): {daily_avg['bio_age_5_17']:,.0f}")
print(f"  Adult (17+):  {daily_avg['bio_age_17_']:,.0f}")


# ================================================================================
# SECTION 3: TIME-BASED PATTERNS (SYSTEM LOAD AND TEMPORAL BEHAVIOR)
# ================================================================================
print("\n" + "="*80)
print("SECTION 3: TIME-BASED PATTERNS - SYSTEM LOAD ANALYSIS")
print("="*80)

# Daily biometric transaction volume
daily_biometrics = df_full.groupby('date')['total_biometric'].sum().sort_values(ascending=False)
print(f"\n🗓️  TOP 10 HIGHEST TRANSACTION DAYS:")
print(daily_biometrics.head(10))

# Identify system stress spikes
mean_daily = daily_biometrics.mean()
std_daily = daily_biometrics.std()
spike_threshold = mean_daily + 2*std_daily
spikes = daily_biometrics[daily_biometrics > spike_threshold]
print(f"\n⚡ SYSTEM STRESS ANALYSIS:")
print(f"  Mean daily transactions: {mean_daily:,.0f}")
print(f"  Std deviation: {std_daily:,.0f}")
print(f"  Spike threshold (μ + 2σ): {spike_threshold:,.0f}")
print(f"  Days with spikes: {len(spikes)}")
if len(spikes) > 0:
    print(f"\n  Spike dates:")
    print(spikes)

# Monthly trends
monthly_biometrics = df_full.groupby(df_full['date'].dt.to_period('M'))[['bio_age_5_17', 'bio_age_17_', 'total_biometric']].sum()
print(f"\n📊 MONTHLY TRANSACTION TRENDS:")
print(monthly_biometrics)

# Day of week patterns
dow_analysis = df_full.groupby('day_of_week')[['bio_age_5_17', 'bio_age_17_', 'total_biometric']].sum()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_analysis = dow_analysis.reindex(day_order)
print(f"\n📅 DAY-OF-WEEK TRANSACTION PATTERNS:")
print(dow_analysis)

weekend_total = dow_analysis.loc[['Saturday', 'Sunday'], 'total_biometric'].sum()
weekday_total = dow_analysis.loc[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'total_biometric'].sum()
weekday_avg = weekday_total / 5
weekend_avg = weekend_total / 2
print(f"\n  Weekday avg: {weekday_avg:,.0f} | Weekend avg: {weekend_avg:,.0f}")
print(f"  Weekday activity is {((weekday_avg/weekend_avg - 1)*100):.1f}% {'higher' if weekday_avg > weekend_avg else 'lower'} than weekends")


# ================================================================================
# SECTION 4: GEOGRAPHIC DISTRIBUTION - STATE AND DISTRICT PATTERNS
# ================================================================================
print("\n" + "="*80)
print("SECTION 4: GEOGRAPHIC DISTRIBUTION - STATE AND DISTRICT ANALYSIS")
print("="*80)

# State-level analysis
state_biometrics = df_full.groupby('state')[['bio_age_5_17', 'bio_age_17_', 'total_biometric']].sum().sort_values('total_biometric', ascending=False)
print(f"\n🗺️  TOP 15 STATES BY TOTAL BIOMETRIC TRANSACTIONS:")
print(state_biometrics.head(15))

# State concentration analysis
state_cumulative = state_biometrics['total_biometric'].cumsum() / state_biometrics['total_biometric'].sum() * 100
states_for_50pct = (state_cumulative <= 50).sum()
states_for_80pct = (state_cumulative <= 80).sum()
print(f"\n📍 GEOGRAPHIC CONCENTRATION:")
print(f"  States covering 50% of transactions: {states_for_50pct} out of {len(state_biometrics)}")
print(f"  States covering 80% of transactions: {states_for_80pct} out of {len(state_biometrics)}")

# District-level analysis
district_biometrics = df_full.groupby(['state', 'district'])['total_biometric'].sum().sort_values(ascending=False)
print(f"\n🏘️  TOP 15 DISTRICTS BY TOTAL BIOMETRIC TRANSACTIONS:")
print(district_biometrics.head(15))

# District concentration
n_districts = len(district_biometrics)
top10pct_n = max(1, int(n_districts * 0.10))
top10pct_share = district_biometrics.head(top10pct_n).sum() / district_biometrics.sum() * 100
print(f"\n  Top 10% of districts account for: {top10pct_share:.1f}% of all transactions")


# ================================================================================
# SECTION 5: AGE ENGAGEMENT BY GEOGRAPHY
# ================================================================================
print("\n" + "="*80)
print("SECTION 5: AGE-BASED ENGAGEMENT BY REGION")
print("="*80)

# Calculate age percentages by state
state_age_analysis = df_full.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum()
state_age_analysis['total'] = state_age_analysis.sum(axis=1)
state_age_analysis['youth_pct'] = (state_age_analysis['bio_age_5_17'] / state_age_analysis['total'] * 100).round(2)
state_age_analysis['adult_pct'] = (state_age_analysis['bio_age_17_'] / state_age_analysis['total'] * 100).round(2)
state_age_analysis['youth_to_adult_ratio'] = (state_age_analysis['bio_age_5_17'] / state_age_analysis['bio_age_17_']).round(3)

# States with highest youth engagement
youth_heavy = state_age_analysis.nlargest(10, 'youth_pct')[['youth_pct', 'adult_pct', 'youth_to_adult_ratio']]
print(f"\n👶 TOP 10 YOUTH-HEAVY STATES (High 5-17 age biometric usage):")
print(youth_heavy)

# States with highest adult engagement
adult_heavy = state_age_analysis.nlargest(10, 'adult_pct')[['youth_pct', 'adult_pct', 'youth_to_adult_ratio']]
print(f"\n👨 TOP 10 ADULT-HEAVY STATES (High 17+ age biometric usage):")
print(adult_heavy)

# States with highest youth-to-adult ratio
high_ratio_states = state_age_analysis.nlargest(10, 'youth_to_adult_ratio')[['bio_age_5_17', 'bio_age_17_', 'youth_to_adult_ratio']]
print(f"\n📊 HIGHEST YOUTH-TO-ADULT ENGAGEMENT RATIOS:")
print(high_ratio_states)
print("  Interpretation: These states have disproportionately high youth biometric activity")

# States with lowest youth-to-adult ratio (adult-dominated)
low_ratio_states = state_age_analysis.nsmallest(10, 'youth_to_adult_ratio')[['bio_age_5_17', 'bio_age_17_', 'youth_to_adult_ratio']]
print(f"\n📉 LOWEST YOUTH-TO-ADULT ENGAGEMENT RATIOS:")
print(low_ratio_states)
print("  Interpretation: These states have predominantly adult biometric activity")


# ================================================================================
# SECTION 6: DEMOGRAPHIC ENGAGEMENT PATTERNS
# ================================================================================
print("\n" + "="*80)
print("SECTION 6: DEMOGRAPHIC ENGAGEMENT PATTERNS")
print("="*80)

# District-level youth engagement analysis
district_age = df_full.groupby(['state', 'district'])[['bio_age_5_17', 'bio_age_17_']].sum()
district_age['youth_to_adult_ratio'] = district_age['bio_age_5_17'] / district_age['bio_age_17_'].replace(0, np.nan)
district_age = district_age.dropna(subset=['youth_to_adult_ratio'])

print(f"\n📊 DISTRICT-LEVEL YOUTH ENGAGEMENT:")
print("  Top 15 districts with highest youth biometric engagement:")
top_youth_districts = district_age.nlargest(15, 'youth_to_adult_ratio')['youth_to_adult_ratio']
print(top_youth_districts)

print("\n  Bottom 15 districts (adult-dominated biometric usage):")
bottom_youth_districts = district_age.nsmallest(15, 'youth_to_adult_ratio')['youth_to_adult_ratio']
print(bottom_youth_districts)

# Calculate engagement balance
median_ratio = district_age['youth_to_adult_ratio'].median()
mean_ratio = district_age['youth_to_adult_ratio'].mean()
print(f"\n📈 ENGAGEMENT DISTRIBUTION STATISTICS:")
print(f"  Median youth-to-adult ratio: {median_ratio:.3f}")
print(f"  Mean youth-to-adult ratio: {mean_ratio:.3f}")

# Classify districts by engagement pattern
balanced = district_age[(district_age['youth_to_adult_ratio'] > 0.3) & (district_age['youth_to_adult_ratio'] < 0.7)]
youth_dominant = district_age[district_age['youth_to_adult_ratio'] >= 0.7]
adult_dominant = district_age[district_age['youth_to_adult_ratio'] <= 0.3]

print(f"\n🎯 DISTRICT CLASSIFICATION BY ENGAGEMENT PATTERN:")
print(f"  Youth-dominant (ratio ≥ 0.7): {len(youth_dominant)} districts")
print(f"  Balanced (0.3 < ratio < 0.7): {len(balanced)} districts")
print(f"  Adult-dominant (ratio ≤ 0.3): {len(adult_dominant)} districts")


# ================================================================================
# SECTION 7: TEMPORAL EVOLUTION - AGE ENGAGEMENT SHIFTS OVER TIME
# ================================================================================
print("\n" + "="*80)
print("SECTION 7: TEMPORAL EVOLUTION - AGE ENGAGEMENT MIGRATION")
print("="*80)

# Split into early vs late period
cutoff = df_full['date'].median()
early_period = df_full[df_full['date'] <= cutoff]
late_period = df_full[df_full['date'] > cutoff]

print(f"\n📅 PERIOD SPLIT (median date cutoff):")
print(f"  Early period: {early_period['date'].min().date()} to {early_period['date'].max().date()}")
print(f"  Late period:  {late_period['date'].min().date()} to {late_period['date'].max().date()}")

# Compare age group usage percentages
early_totals = early_period[['bio_age_5_17', 'bio_age_17_']].sum()
late_totals = late_period[['bio_age_5_17', 'bio_age_17_']].sum()

early_total = early_totals.sum()
late_total = late_totals.sum()

print(f"\n🔄 AGE GROUP USAGE EVOLUTION:")
print(f"  Early Period:")
print(f"    Youth (5-17): {early_totals['bio_age_5_17']/early_total*100:.2f}%")
print(f"    Adult (17+):  {early_totals['bio_age_17_']/early_total*100:.2f}%")
print(f"\n  Late Period:")
print(f"    Youth (5-17): {late_totals['bio_age_5_17']/late_total*100:.2f}%")
print(f"    Adult (17+):  {late_totals['bio_age_17_']/late_total*100:.2f}%")

# Calculate percentage point changes
youth_change = (late_totals['bio_age_5_17']/late_total*100) - (early_totals['bio_age_5_17']/early_total*100)
adult_change = (late_totals['bio_age_17_']/late_total*100) - (early_totals['bio_age_17_']/early_total*100)

print(f"\n📈 PERCENTAGE POINT CHANGE (late vs early):")
print(f"  Youth (5-17): {youth_change:+.2f}pp")
print(f"  Adult (17+):  {adult_change:+.2f}pp")

# State-wise youth engagement shifts
early_state = early_period.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum()
late_state = late_period.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum()

early_state['youth_pct'] = early_state['bio_age_5_17'] / early_state.sum(axis=1) * 100
late_state['youth_pct'] = late_state['bio_age_5_17'] / late_state.sum(axis=1) * 100

youth_adoption_change = (late_state['youth_pct'] - early_state['youth_pct']).dropna()
print(f"\n👶 STATES WITH HIGHEST YOUTH ENGAGEMENT INCREASE (late vs early):")
print(youth_adoption_change.nlargest(10))

print(f"\n👨 STATES WITH HIGHEST ADULT ENGAGEMENT INCREASE:")
print((-youth_adoption_change).nlargest(10))


# ================================================================================
# SECTION 8: DATA QUALITY AND ANOMALY DETECTION
# ================================================================================
print("\n" + "="*80)
print("SECTION 8: DATA QUALITY AND ANOMALY DETECTION")
print("="*80)

# Exact duplicates
duplicates = df_full.duplicated(subset=['date', 'state', 'district', 'pincode', 'bio_age_5_17', 'bio_age_17_'])
print(f"\n🔍 EXACT DUPLICATE ROWS: {duplicates.sum():,}")

# Missing values
print(f"\n❌ MISSING VALUES:")
missing = df_full.isnull().sum()
for col, count in missing.items():
    if count > 0:
        print(f"  {col}: {count:,} ({count/len(df_full)*100:.2f}%)")
if missing.sum() == 0:
    print("  None - dataset is complete!")

# Zero transaction records
zero_records = df_full[df_full['total_biometric'] == 0]
print(f"\n⚪ ZERO-TRANSACTION RECORDS: {len(zero_records):,} ({len(zero_records)/len(df_full)*100:.2f}%)")

# Both age groups zero (suspicious)
all_zero = df_full[(df_full['bio_age_5_17'] == 0) & (df_full['bio_age_17_'] == 0)]
print(f"  Both age groups zero: {len(all_zero):,}")

# Unusual patterns - extremely high single-day values
print(f"\n⚠️  ANOMALOUS HIGH-VALUE RECORDS:")

# Find outliers using IQR method
for age_group in ['bio_age_5_17', 'bio_age_17_']:
    q1 = df_full[age_group].quantile(0.25)
    q3 = df_full[age_group].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 3*iqr  # 3*IQR for extreme outliers
    outliers = df_full[df_full[age_group] > upper_bound]
    
    if len(outliers) > 0:
        age_label = "Youth (5-17)" if age_group == 'bio_age_5_17' else "Adult (17+)"
        print(f"\n  {age_label} outliers (> Q3 + 3*IQR = {upper_bound:.0f}): {len(outliers)}")
        print(f"    Top 5:")
        top_outliers = outliers.nlargest(5, age_group)[['date', 'state', 'district', 'bio_age_5_17', 'bio_age_17_']]
        print(top_outliers)

# States with only youth or only adult activity (unusual)
state_active_ages = (state_age_analysis[['bio_age_5_17', 'bio_age_17_']] > 0).sum(axis=1)
single_age_states = state_active_ages[state_active_ages == 1]
print(f"\n🚨 STATES WITH ONLY ONE ACTIVE AGE GROUP (unusual pattern): {len(single_age_states)}")
if len(single_age_states) > 0:
    print(single_age_states)


# ================================================================================
# SECTION 9: DIGITAL INFRASTRUCTURE READINESS INDICATORS
# ================================================================================
print("\n" + "="*80)
print("SECTION 9: DIGITAL INFRASTRUCTURE READINESS")
print("="*80)

# Transaction density by district
district_density = df_full.groupby(['state', 'district']).agg({
    'total_biometric': 'sum',
    'date': 'count'  # Number of reporting days
})
district_density.columns = ['total_transactions', 'reporting_days']
district_density['avg_daily_transactions'] = district_density['total_transactions'] / district_density['reporting_days']
district_density = district_density.sort_values('avg_daily_transactions', ascending=False)

print(f"\n🏆 HIGHEST AVERAGE DAILY TRANSACTION DISTRICTS (strong digital infrastructure):")
print(district_density.head(15))

print(f"\n📉 LOWEST AVERAGE DAILY TRANSACTION DISTRICTS (weak infrastructure signals):")
print(district_density.tail(15))

# State-level readiness score (based on volume and engagement balance)
state_readiness = state_age_analysis.copy()
state_readiness['volume_score'] = (state_readiness['total'] / state_readiness['total'].max() * 100).round(2)

# Balance score: how close to 50-50 split (0.5 ratio is perfect balance)
state_readiness['balance_deviation'] = abs(state_readiness['youth_to_adult_ratio'] - 0.5)
state_readiness['balance_score'] = (1 - (state_readiness['balance_deviation'] / state_readiness['balance_deviation'].max())) * 100
state_readiness['balance_score'] = state_readiness['balance_score'].round(2)

state_readiness['readiness_score'] = (state_readiness['volume_score'] * 0.7 + state_readiness['balance_score'] * 0.3).round(2)
state_readiness = state_readiness.sort_values('readiness_score', ascending=False)

print(f"\n🌟 TOP 15 STATES BY DIGITAL READINESS SCORE:")
print(state_readiness[['total', 'youth_to_adult_ratio', 'volume_score', 'balance_score', 'readiness_score']].head(15))


# ================================================================================
# SECTION 10: MERGE-READY SUMMARY AND INTEGRATION NOTES
# ================================================================================
print("\n" + "="*80)
print("SECTION 10: INTEGRATION AND MERGE GUIDELINES")
print("="*80)

print(f"\n🔗 MERGE KEYS FOR JOINING WITH OTHER DATASETS:")
print(f"  Primary keys: ['date', 'state', 'district', 'pincode']")
print(f"  Available measures: bio_age_5_17, bio_age_17_, total_biometric")
print(f"\n📊 DATASET SUMMARY:")
print(f"  Date range: {df_full['date'].min().date()} to {df_full['date'].max().date()}")
print(f"  Geographic coverage: {df_full['state'].nunique()} states, {df_full['district'].nunique()} districts")
print(f"  Total records: {len(df_full):,}")
print(f"  Total transactions tracked: {df_full['total_biometric'].sum():,}")

print(f"\n💡 CROSS-DATASET ANALYSIS OPPORTUNITIES:")
print(f"  1. Merge with DEMOGRAPHIC data → compare demographic counts vs biometric usage")
print(f"  2. Merge with ENROLMENT data → analyze enrollment vs authentication patterns")
print(f"  3. Combined analysis → identify gaps between enrollment, demographics, and biometric usage")
print(f"  4. Age correlation → compare bio_age patterns with demo_age patterns")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
