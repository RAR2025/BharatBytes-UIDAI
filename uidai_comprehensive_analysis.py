"""
================================================================================
UIDAI DATA HACKATHON - COMPREHENSIVE ANALYSIS SOLUTION
================================================================================
This script implements end-to-end analysis for UIDAI Aadhaar data to extract
trends, anomalies, and predictive indicators related to:
  1. Biometric deployment lag vs demographic/enrolment
  2. Age-cohort efficiency (0-5 vs 5-17 vs 18+)
  3. Geographic efficiency patterns (Tier-1 vs Tier-2 vs Tier-3)

Output CSVs are saved to the `outputs/` directory.

Author: UIDAI Data Hackathon Solution
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from collections import defaultdict

# Machine Learning imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# Visualization imports
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ================================================================================
# CONFIGURATION CONSTANTS (Easily adjustable parameters)
# ================================================================================

# Age cohort effort weights (units of effort per enrolment)
EFFORT_WEIGHT_0_5 = 4.0     # Infants/toddlers require most effort
EFFORT_WEIGHT_5_17 = 1.5    # Youth require moderate effort
EFFORT_WEIGHT_18_PLUS = 1.0 # Adults - baseline effort

# Re-enrolment detection window (days)
REENROLMENT_WINDOW_DAYS = 14

# Staff utilization theoretical capacity per center per day
THEORETICAL_CAPACITY_PER_CENTER = 100

# High backlog threshold (percentile)
HIGH_BACKLOG_PERCENTILE = 75

# ================================================================================
# TIER DEFINITIONS FOR GEOGRAPHIC ANALYSIS
# ================================================================================

# Tier-1: Major metropolitan cities (identified by state + district)
TIER_1_METROS = [
    ("Delhi", "New Delhi"),
    ("Delhi", "Central Delhi"),
    ("Delhi", "North Delhi"),
    ("Delhi", "South Delhi"),
    ("Delhi", "East Delhi"),
    ("Delhi", "West Delhi"),
    ("Delhi", "North West Delhi"),
    ("Delhi", "North East Delhi"),
    ("Delhi", "South West Delhi"),
    ("Delhi", "South East Delhi"),
    ("Delhi", "Shahdara"),
    ("Maharashtra", "Mumbai City"),
    ("Maharashtra", "Mumbai Suburban"),
    ("Karnataka", "Bengaluru Urban"),
    ("Telangana", "Hyderabad"),
    ("Tamil Nadu", "Chennai"),
    ("West Bengal", "Kolkata"),
    ("Gujarat", "Ahmedabad"),
    ("Maharashtra", "Pune"),
    ("Rajasthan", "Jaipur"),
    ("Uttar Pradesh", "Lucknow"),
]

# Tier-2: State capitals and major cities
TIER_2_CITIES = [
    ("Madhya Pradesh", "Bhopal"),
    ("Madhya Pradesh", "Indore"),
    ("Bihar", "Patna"),
    ("Jharkhand", "Ranchi"),
    ("Odisha", "Khordha"),  # Bhubaneswar
    ("Kerala", "Thiruvananthapuram"),
    ("Kerala", "Ernakulam"),  # Kochi
    ("Assam", "Kamrup Metropolitan"),  # Guwahati
    ("Punjab", "Ludhiana"),
    ("Punjab", "Jalandhar"),
    ("Haryana", "Gurugram"),
    ("Haryana", "Faridabad"),
    ("Uttarakhand", "Dehradun"),
    ("Chhattisgarh", "Raipur"),
    ("Andhra Pradesh", "Krishna"),  # Vijayawada
    ("Andhra Pradesh", "East Godavari"),
    ("Gujarat", "Surat"),
    ("Gujarat", "Vadodara"),
    ("Tamil Nadu", "Coimbatore"),
    ("Maharashtra", "Nagpur"),
    ("Maharashtra", "Nashik"),
    ("Uttar Pradesh", "Kanpur Nagar"),
    ("Uttar Pradesh", "Varanasi"),
    ("Uttar Pradesh", "Ghaziabad"),
    ("Uttar Pradesh", "Agra"),
    ("West Bengal", "North 24 Parganas"),
    ("West Bengal", "Howrah"),
    ("Rajasthan", "Jodhpur"),
    ("Rajasthan", "Udaipur"),
    ("Karnataka", "Mysuru"),
    ("Telangana", "Rangareddy"),
    ("Jammu and Kashmir", "Srinagar"),
    ("Jammu and Kashmir", "Jammu"),
]

# Output directory
OUTPUT_DIR = "outputs"

# ================================================================================
# DATA LOADING AND CLEANING
# ================================================================================

def load_and_clean_data():
    """
    Load and clean all CSV chunks for demographic, enrolment, and biometric data.
    
    Returns:
        tuple: (df_demo, df_enrol, df_bio) - Three cleaned DataFrames
    """
    print("\n" + "=" * 80)
    print("SECTION 1: DATA INGESTION & CLEANING")
    print("=" * 80)
    
    # Define data paths (consolidated files in filtered_data folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filtered_dir = os.path.join(base_dir, "filtered_data")
    
    # Load Demographic Data
    print("\n📊 Loading DEMOGRAPHIC data...")
    demo_path = os.path.join(filtered_dir, "consolidated_demographic.csv")
    df_demo = pd.read_csv(demo_path)
    df_demo = _clean_dataframe(df_demo, "demographic")
    print(f"  ✓ Loaded: consolidated_demographic.csv ({df_demo.shape[0]:,} rows)")
    
    # Load Enrolment Data
    print("\n📊 Loading ENROLMENT data...")
    enrol_path = os.path.join(filtered_dir, "consolidated_enrolment.csv")
    df_enrol = pd.read_csv(enrol_path)
    df_enrol = _clean_dataframe(df_enrol, "enrolment")
    print(f"  ✓ Loaded: consolidated_enrolment.csv ({df_enrol.shape[0]:,} rows)")
    
    # Load Biometric Data
    print("\n📊 Loading BIOMETRIC data...")
    bio_path = os.path.join(filtered_dir, "consolidated_biometric.csv")
    df_bio = pd.read_csv(bio_path)
    df_bio = _clean_dataframe(df_bio, "biometric")
    print(f"  ✓ Loaded: consolidated_biometric.csv ({df_bio.shape[0]:,} rows)")
    
    # Print summary statistics
    _print_data_summary(df_demo, df_enrol, df_bio)
    
    return df_demo, df_enrol, df_bio


def _clean_dataframe(df, data_type):
    """
    Clean dataframe: parse dates, convert numerics, remove duplicates/junk.
    
    Args:
        df: Input dataframe
        data_type: Type of data ("demographic", "enrolment", "biometric")
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    if df.empty:
        return df
    
    original_rows = len(df)
    
    # Parse date column (day-first format: DD-MM-YYYY)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Standardize text columns (strip spaces, standardize case)
    for col in ['state', 'district']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    
    # Convert pincode to string and validate
    if 'pincode' in df.columns:
        df['pincode'] = df['pincode'].astype(str).str.strip()
        # Remove rows with invalid pincodes (not 6 digits)
        valid_pincode = df['pincode'].str.match(r'^\d{6}$')
        df = df[valid_pincode]
    
    # Convert numeric columns and fill missing with 0
    numeric_cols = _get_numeric_columns(data_type)
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Remove rows with missing essential fields
    essential_cols = ['date', 'state', 'district']
    df = df.dropna(subset=essential_cols)
    
    # Remove rows with 'nan' or empty state
    df = df[~df['state'].isin(['Nan', 'nan', ''])]
    
    # Drop exact duplicate rows
    df = df.drop_duplicates()
    
    cleaned_rows = len(df)
    removed = original_rows - cleaned_rows
    print(f"  🧹 Cleaned: {removed:,} rows removed, {cleaned_rows:,} rows remaining")
    
    return df


def _get_numeric_columns(data_type):
    """Get numeric column names for each data type."""
    if data_type == "demographic":
        return ['demo_age_5_17', 'demo_age_17_']
    elif data_type == "enrolment":
        return ['age_0_5', 'age_5_17', 'age_18_greater']
    elif data_type == "biometric":
        return ['bio_age_5_17', 'bio_age_17_']
    return []


def _print_data_summary(df_demo, df_enrol, df_bio):
    """Print summary statistics for all datasets."""
    print("\n" + "-" * 80)
    print("DATA SUMMARY")
    print("-" * 80)
    
    datasets = [
        ("Demographic", df_demo),
        ("Enrolment", df_enrol),
        ("Biometric", df_bio)
    ]
    
    for name, df in datasets:
        if not df.empty:
            print(f"\n{name}:")
            print(f"  Rows: {len(df):,}")
            print(f"  Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
            print(f"  States: {df['state'].nunique()}")
            print(f"  Districts: {df['district'].nunique()}")
            print(f"  Pincodes: {df['pincode'].nunique()}")


# ================================================================================
# INSIGHT 1: BIOMETRIC DEPLOYMENT LAG & BACKLOG
# ================================================================================

def compute_biometric_lag(df_demo, df_bio):
    """
    Analyze biometric deployment lag compared to demographic data.
    Quantifies how much biometric capture lags demographic and estimates backlog.
    
    Args:
        df_demo: Cleaned demographic dataframe
        df_bio: Cleaned biometric dataframe
    
    Saves:
        - biometric_lag_national.csv
        - biometric_lag_by_state.csv
    """
    print("\n" + "=" * 80)
    print("SECTION 2: BIOMETRIC DEPLOYMENT LAG & BACKLOG ANALYSIS")
    print("=" * 80)
    
    if df_demo.empty or df_bio.empty:
        print("  ⚠️ Cannot compute: Missing demographic or biometric data")
        return
    
    # Create total columns
    df_demo = df_demo.copy()
    df_bio = df_bio.copy()
    
    df_demo['total_demo'] = df_demo['demo_age_5_17'] + df_demo['demo_age_17_']
    df_bio['total_bio'] = df_bio['bio_age_5_17'] + df_bio['bio_age_17_']
    
    # -------------------------------------------------------------------------
    # NATIONAL LEVEL ANALYSIS
    # -------------------------------------------------------------------------
    print("\n📊 National Level Analysis")
    
    # Daily national totals
    demo_daily = df_demo.groupby('date')['total_demo'].sum().reset_index()
    bio_daily = df_bio.groupby('date')['total_bio'].sum().reset_index()
    
    # Find start dates (first date with data > 0)
    demo_start = demo_daily[demo_daily['total_demo'] > 0]['date'].min()
    bio_start = bio_daily[bio_daily['total_bio'] > 0]['date'].min()
    
    # Compute lag in days
    lag_days = (bio_start - demo_start).days if pd.notna(bio_start) and pd.notna(demo_start) else 0
    
    print(f"  Demographic start date: {demo_start.date() if pd.notna(demo_start) else 'N/A'}")
    print(f"  Biometric start date: {bio_start.date() if pd.notna(bio_start) else 'N/A'}")
    print(f"  Deployment lag: {lag_days} days")
    
    # Compute cumulative curves
    demo_daily = demo_daily.sort_values('date')
    bio_daily = bio_daily.sort_values('date')
    
    demo_daily['demo_cum'] = demo_daily['total_demo'].cumsum()
    bio_daily['bio_cum'] = bio_daily['total_bio'].cumsum()
    
    # Merge on date for backlog calculation
    combined = pd.merge(demo_daily, bio_daily, on='date', how='outer').sort_values('date')
    combined = combined.fillna(method='ffill').fillna(0)
    
    # Recompute cumulative after merge
    combined = combined.sort_values('date')
    combined['demo_cum'] = combined['total_demo'].cumsum()
    combined['bio_cum'] = combined['total_bio'].cumsum()
    
    # Compute backlog (clipped at 0)
    combined['backlog'] = (combined['demo_cum'] - combined['bio_cum']).clip(lower=0)
    
    # Extract key metrics
    max_backlog = combined['backlog'].max()
    max_backlog_date = combined.loc[combined['backlog'].idxmax(), 'date']
    
    # Compute bio-to-demo ratio
    combined['bio_to_demo_ratio'] = np.where(
        combined['demo_cum'] > 0,
        combined['bio_cum'] / combined['demo_cum'],
        0
    )
    
    print(f"  Maximum backlog: {max_backlog:,.0f} (on {max_backlog_date.date()})")
    
    # Monthly milestones
    monthly_metrics = []
    for month in combined['date'].dt.to_period('M').unique():
        month_end = combined[combined['date'].dt.to_period('M') == month].iloc[-1]
        monthly_metrics.append({
            'month': str(month),
            'backlog': month_end['backlog'],
            'bio_to_demo_ratio': month_end['bio_to_demo_ratio']
        })
    
    # Final metrics
    end_date = combined['date'].max()
    end_backlog = combined.iloc[-1]['backlog']
    end_ratio = combined.iloc[-1]['bio_to_demo_ratio']
    
    print(f"  End-of-period backlog: {end_backlog:,.0f}")
    print(f"  End-of-period ratio: {end_ratio:.4f}")
    
    # Save national metrics
    national_metrics = pd.DataFrame([
        {'metric': 'demo_start_date', 'value': str(demo_start.date()) if pd.notna(demo_start) else 'N/A'},
        {'metric': 'bio_start_date', 'value': str(bio_start.date()) if pd.notna(bio_start) else 'N/A'},
        {'metric': 'deployment_lag_days', 'value': lag_days},
        {'metric': 'max_backlog', 'value': max_backlog},
        {'metric': 'max_backlog_date', 'value': str(max_backlog_date.date())},
        {'metric': 'end_backlog', 'value': end_backlog},
        {'metric': 'end_bio_to_demo_ratio', 'value': round(end_ratio, 4)},
        {'metric': 'total_demo_cum', 'value': combined.iloc[-1]['demo_cum']},
        {'metric': 'total_bio_cum', 'value': combined.iloc[-1]['bio_cum']},
    ])
    
    national_path = os.path.join(OUTPUT_DIR, "biometric_lag_national.csv")
    national_metrics.to_csv(national_path, index=False)
    print(f"\n  💾 Saved: {national_path}")
    
    # -------------------------------------------------------------------------
    # STATE LEVEL ANALYSIS
    # -------------------------------------------------------------------------
    print("\n📊 State Level Analysis")
    
    state_metrics = []
    
    for state in df_demo['state'].unique():
        # State-level daily totals
        state_demo = df_demo[df_demo['state'] == state].groupby('date')['total_demo'].sum().reset_index()
        state_bio = df_bio[df_bio['state'] == state].groupby('date')['total_bio'].sum().reset_index()
        
        if state_demo.empty:
            continue
        
        # Start dates
        s_demo_start = state_demo[state_demo['total_demo'] > 0]['date'].min()
        s_bio_start = state_bio[state_bio['total_bio'] > 0]['date'].min() if not state_bio.empty else pd.NaT
        
        # Lag
        s_lag = (s_bio_start - s_demo_start).days if pd.notna(s_bio_start) and pd.notna(s_demo_start) else None
        
        # Cumulative
        state_demo = state_demo.sort_values('date')
        state_demo['demo_cum'] = state_demo['total_demo'].cumsum()
        
        if not state_bio.empty:
            state_bio = state_bio.sort_values('date')
            state_bio['bio_cum'] = state_bio['total_bio'].cumsum()
            
            # Merge for backlog
            state_combined = pd.merge(state_demo, state_bio, on='date', how='outer').sort_values('date')
            state_combined = state_combined.fillna(method='ffill').fillna(0)
            state_combined['demo_cum'] = state_combined['total_demo'].cumsum()
            state_combined['bio_cum'] = state_combined['total_bio'].cumsum()
            state_combined['backlog'] = (state_combined['demo_cum'] - state_combined['bio_cum']).clip(lower=0)
            
            max_bl = state_combined['backlog'].max()
            max_bl_date = state_combined.loc[state_combined['backlog'].idxmax(), 'date']
            end_ratio = state_combined.iloc[-1]['bio_cum'] / state_combined.iloc[-1]['demo_cum'] if state_combined.iloc[-1]['demo_cum'] > 0 else 0
        else:
            max_bl = state_demo.iloc[-1]['demo_cum'] if not state_demo.empty else 0
            max_bl_date = s_demo_start
            end_ratio = 0
        
        state_metrics.append({
            'state': state,
            'start_date_demo': str(s_demo_start.date()) if pd.notna(s_demo_start) else 'N/A',
            'start_date_bio': str(s_bio_start.date()) if pd.notna(s_bio_start) else 'N/A',
            'lag_days': s_lag,
            'max_backlog': max_bl,
            'backlog_date': str(max_bl_date.date()) if pd.notna(max_bl_date) else 'N/A',
            'bio_to_demo_ratio_end': round(end_ratio, 4)
        })
    
    state_df = pd.DataFrame(state_metrics)
    state_path = os.path.join(OUTPUT_DIR, "biometric_lag_by_state.csv")
    state_df.to_csv(state_path, index=False)
    print(f"  💾 Saved: {state_path}")
    print(f"  States analyzed: {len(state_df)}")
    
    # -------------------------------------------------------------------------
    # GENERATE VISUALIZATION
    # -------------------------------------------------------------------------
    print("\n📈 Generating visualization...")
    
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(combined['date'], combined['demo_cum'], label='Demographic (Cumulative)', 
                color='blue', linewidth=2)
        ax.plot(combined['date'], combined['bio_cum'], label='Biometric (Cumulative)', 
                color='green', linewidth=2)
        ax.fill_between(combined['date'], combined['bio_cum'], combined['demo_cum'], 
                        alpha=0.3, color='red', label='Backlog')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')
        ax.set_title('Biometric Deployment Lag: Cumulative Demographic vs Biometric')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = os.path.join(OUTPUT_DIR, "biometric_lag_plot.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"  💾 Saved: {plot_path}")
    except Exception as e:
        print(f"  ⚠️ Could not generate plot: {e}")


# ================================================================================
# INSIGHT 2: AGE COHORT EFFICIENCY
# ================================================================================

def compute_age_cohort_efficiency(df_enrol):
    """
    Measure efficiency across age cohorts (0-5 vs 5-17 vs 18+).
    Computes volume, effort units, variance metrics, and re-enrolment rates.
    
    Args:
        df_enrol: Cleaned enrolment dataframe
    
    Saves:
        - age_cohort_efficiency.csv
    """
    print("\n" + "=" * 80)
    print("SECTION 3: AGE COHORT EFFICIENCY ANALYSIS")
    print("=" * 80)
    
    if df_enrol.empty:
        print("  ⚠️ Cannot compute: Missing enrolment data")
        return
    
    df = df_enrol.copy()
    
    # -------------------------------------------------------------------------
    # VOLUME ANALYSIS
    # -------------------------------------------------------------------------
    print("\n📊 Volume Analysis")
    
    total_0_5 = df['age_0_5'].sum()
    total_5_17 = df['age_5_17'].sum()
    total_18_plus = df['age_18_greater'].sum()
    total_all = total_0_5 + total_5_17 + total_18_plus
    
    print(f"  Age 0-5:   {total_0_5:>15,} ({total_0_5/total_all*100:.2f}%)")
    print(f"  Age 5-17:  {total_5_17:>15,} ({total_5_17/total_all*100:.2f}%)")
    print(f"  Age 18+:   {total_18_plus:>15,} ({total_18_plus/total_all*100:.2f}%)")
    print(f"  Total:     {total_all:>15,}")
    
    # -------------------------------------------------------------------------
    # EFFORT UNITS CALCULATION
    # -------------------------------------------------------------------------
    print("\n📊 Effort Units (Weighted Analysis)")
    
    effort_0_5 = total_0_5 * EFFORT_WEIGHT_0_5
    effort_5_17 = total_5_17 * EFFORT_WEIGHT_5_17
    effort_18_plus = total_18_plus * EFFORT_WEIGHT_18_PLUS
    effort_total = effort_0_5 + effort_5_17 + effort_18_plus
    
    print(f"  Weight 0-5: {EFFORT_WEIGHT_0_5}x | 5-17: {EFFORT_WEIGHT_5_17}x | 18+: {EFFORT_WEIGHT_18_PLUS}x")
    print(f"  Effort 0-5:   {effort_0_5:>18,.0f} ({effort_0_5/effort_total*100:.2f}%)")
    print(f"  Effort 5-17:  {effort_5_17:>18,.0f} ({effort_5_17/effort_total*100:.2f}%)")
    print(f"  Effort 18+:   {effort_18_plus:>18,.0f} ({effort_18_plus/effort_total*100:.2f}%)")
    
    # -------------------------------------------------------------------------
    # VARIANCE METRICS (Operational Complexity)
    # -------------------------------------------------------------------------
    print("\n📊 Variance Metrics (by District-Day)")
    
    # Daily district-level aggregation
    daily_district = df.groupby(['date', 'state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    # Compute coefficient of variation for each age group
    cv_0_5 = daily_district['age_0_5'].std() / daily_district['age_0_5'].mean() if daily_district['age_0_5'].mean() > 0 else 0
    cv_5_17 = daily_district['age_5_17'].std() / daily_district['age_5_17'].mean() if daily_district['age_5_17'].mean() > 0 else 0
    cv_18_plus = daily_district['age_18_greater'].std() / daily_district['age_18_greater'].mean() if daily_district['age_18_greater'].mean() > 0 else 0
    
    print(f"  CV (0-5):   {cv_0_5:.4f}")
    print(f"  CV (5-17):  {cv_5_17:.4f}")
    print(f"  CV (18+):   {cv_18_plus:.4f}")
    
    # -------------------------------------------------------------------------
    # RE-ENROLMENT RATE ESTIMATION
    # -------------------------------------------------------------------------
    print(f"\n📊 Re-enrolment Rate Estimation (Window: {REENROLMENT_WINDOW_DAYS} days)")
    
    # Heuristic: For each (state, district, pincode), sort by date
    # If there are multiple enrolments within window days, flag as potential re-enrolment
    
    reenrol_rates = {}
    
    for age_col, age_name in [('age_0_5', '0-5'), ('age_5_17', '5-17'), ('age_18_greater', '18+')]:
        # Group by location
        grouped = df.groupby(['state', 'district', 'pincode', 'date'])[age_col].sum().reset_index()
        grouped = grouped.sort_values(['state', 'district', 'pincode', 'date'])
        
        total_records = len(grouped[grouped[age_col] > 0])
        potential_reenrol = 0
        
        # Check for repeated enrolments within window
        for (state, district, pincode), group in grouped.groupby(['state', 'district', 'pincode']):
            if len(group) > 1:
                dates = group[group[age_col] > 0]['date'].values
                for i in range(1, len(dates)):
                    if (dates[i] - dates[i-1]).astype('timedelta64[D]').astype(int) <= REENROLMENT_WINDOW_DAYS:
                        potential_reenrol += 1
        
        reenrol_rate = potential_reenrol / total_records if total_records > 0 else 0
        reenrol_rates[age_name] = reenrol_rate
        print(f"  {age_name}: {reenrol_rate*100:.2f}% estimated re-enrolment rate")
    
    # -------------------------------------------------------------------------
    # SAVE RESULTS
    # -------------------------------------------------------------------------
    
    results = pd.DataFrame([
        {
            'age_group': '0-5',
            'volume_total': total_0_5,
            'volume_percent': round(total_0_5/total_all*100, 2),
            'effort_units': effort_0_5,
            'effort_percent': round(effort_0_5/effort_total*100, 2),
            'coefficient_of_variation': round(cv_0_5, 4),
            'approx_reenrolment_rate': round(reenrol_rates.get('0-5', 0), 4),
            'effort_weight': EFFORT_WEIGHT_0_5
        },
        {
            'age_group': '5-17',
            'volume_total': total_5_17,
            'volume_percent': round(total_5_17/total_all*100, 2),
            'effort_units': effort_5_17,
            'effort_percent': round(effort_5_17/effort_total*100, 2),
            'coefficient_of_variation': round(cv_5_17, 4),
            'approx_reenrolment_rate': round(reenrol_rates.get('5-17', 0), 4),
            'effort_weight': EFFORT_WEIGHT_5_17
        },
        {
            'age_group': '18+',
            'volume_total': total_18_plus,
            'volume_percent': round(total_18_plus/total_all*100, 2),
            'effort_units': effort_18_plus,
            'effort_percent': round(effort_18_plus/effort_total*100, 2),
            'coefficient_of_variation': round(cv_18_plus, 4),
            'approx_reenrolment_rate': round(reenrol_rates.get('18+', 0), 4),
            'effort_weight': EFFORT_WEIGHT_18_PLUS
        }
    ])
    
    output_path = os.path.join(OUTPUT_DIR, "age_cohort_efficiency.csv")
    results.to_csv(output_path, index=False)
    print(f"\n  💾 Saved: {output_path}")
    
    # Print key insight
    print("\n  📌 KEY INSIGHT: Age Cohort Misallocation")
    print(f"     0-5 group: {total_0_5/total_all*100:.1f}% of volume but {effort_0_5/effort_total*100:.1f}% of effort")


# ================================================================================
# INSIGHT 3: GEOGRAPHIC TIER EFFICIENCY
# ================================================================================

def _assign_tier(state, district):
    """
    Assign geographic tier based on state and district.
    
    Returns:
        str: 'Tier-1', 'Tier-2', or 'Tier-3'
    """
    # Normalize for comparison
    state_norm = state.strip().title()
    district_norm = district.strip().title()
    
    if (state_norm, district_norm) in TIER_1_METROS:
        return 'Tier-1'
    elif (state_norm, district_norm) in TIER_2_CITIES:
        return 'Tier-2'
    else:
        return 'Tier-3'


def compute_geographic_efficiency(df_demo, df_enrol, df_bio):
    """
    Compare efficiency across Tier-1, Tier-2, and Tier-3 regions.
    
    Args:
        df_demo: Cleaned demographic dataframe
        df_enrol: Cleaned enrolment dataframe
        df_bio: Cleaned biometric dataframe
    
    Saves:
        - geographic_tier_efficiency.csv
    """
    print("\n" + "=" * 80)
    print("SECTION 4: GEOGRAPHIC EFFICIENCY (TIER-1 vs TIER-2 vs TIER-3)")
    print("=" * 80)
    
    if df_enrol.empty:
        print("  ⚠️ Cannot compute: Missing enrolment data")
        return
    
    # -------------------------------------------------------------------------
    # ASSIGN TIERS TO DATA
    # -------------------------------------------------------------------------
    print("\n📊 Assigning geographic tiers...")
    
    df_enrol = df_enrol.copy()
    df_enrol['tier'] = df_enrol.apply(lambda x: _assign_tier(x['state'], x['district']), axis=1)
    
    if not df_demo.empty:
        df_demo = df_demo.copy()
        df_demo['tier'] = df_demo.apply(lambda x: _assign_tier(x['state'], x['district']), axis=1)
    
    if not df_bio.empty:
        df_bio = df_bio.copy()
        df_bio['tier'] = df_bio.apply(lambda x: _assign_tier(x['state'], x['district']), axis=1)
    
    # Print tier distribution
    tier_counts = df_enrol['tier'].value_counts()
    print(f"  Tier-1 records: {tier_counts.get('Tier-1', 0):,}")
    print(f"  Tier-2 records: {tier_counts.get('Tier-2', 0):,}")
    print(f"  Tier-3 records: {tier_counts.get('Tier-3', 0):,}")
    
    # -------------------------------------------------------------------------
    # COMPUTE METRICS PER TIER
    # -------------------------------------------------------------------------
    print("\n📊 Computing tier-level metrics...")
    
    tier_results = []
    
    for tier in ['Tier-1', 'Tier-2', 'Tier-3']:
        tier_enrol = df_enrol[df_enrol['tier'] == tier]
        
        if tier_enrol.empty:
            continue
        
        # Total enrolment volume by age group
        enrol_0_5 = tier_enrol['age_0_5'].sum()
        enrol_5_17 = tier_enrol['age_5_17'].sum()
        enrol_18_plus = tier_enrol['age_18_greater'].sum()
        total_enrol = enrol_0_5 + enrol_5_17 + enrol_18_plus
        
        # Effort units
        effort_units = (enrol_0_5 * EFFORT_WEIGHT_0_5 + 
                       enrol_5_17 * EFFORT_WEIGHT_5_17 + 
                       enrol_18_plus * EFFORT_WEIGHT_18_PLUS)
        
        # Number of unique pincodes (proxy for centers)
        num_pincodes = tier_enrol['pincode'].nunique()
        
        # Number of days in data
        num_days = tier_enrol['date'].nunique()
        
        # Average daily per center
        avg_daily_per_center = total_enrol / (num_days * num_pincodes) if num_days > 0 and num_pincodes > 0 else 0
        
        # Biometric metrics
        if not df_bio.empty:
            tier_bio = df_bio[df_bio['tier'] == tier]
            total_bio = tier_bio['bio_age_5_17'].sum() + tier_bio['bio_age_17_'].sum() if not tier_bio.empty else 0
        else:
            total_bio = 0
        
        # Bio-to-enrolment ratio (success proxy)
        bio_to_enrol_ratio = total_bio / total_enrol if total_enrol > 0 else 0
        
        # Cost per verification (effort per biometric)
        cost_per_verification = effort_units / total_bio if total_bio > 0 else float('inf')
        
        # Staff utilization proxy
        utilization = avg_daily_per_center / THEORETICAL_CAPACITY_PER_CENTER
        
        tier_results.append({
            'tier': tier,
            'total_enrolment': total_enrol,
            'enrol_0_5': enrol_0_5,
            'enrol_5_17': enrol_5_17,
            'enrol_18_plus': enrol_18_plus,
            'total_biometric': total_bio,
            'num_centers_proxy': num_pincodes,
            'num_days': num_days,
            'avg_daily_per_center': round(avg_daily_per_center, 2),
            'biometric_to_enrolment_ratio': round(bio_to_enrol_ratio, 4),
            'cost_per_verification': round(cost_per_verification, 4) if cost_per_verification != float('inf') else 'N/A',
            'utilization': round(utilization, 4),
            'theoretical_capacity': THEORETICAL_CAPACITY_PER_CENTER
        })
        
        print(f"\n  {tier}:")
        print(f"    Total enrolment: {total_enrol:,}")
        print(f"    Total biometric: {total_bio:,}")
        print(f"    Centers (pincodes): {num_pincodes}")
        print(f"    Avg daily/center: {avg_daily_per_center:.2f}")
        print(f"    Bio/Enrol ratio: {bio_to_enrol_ratio:.4f}")
        print(f"    Utilization: {utilization:.2%}")
    
    # Save results
    results_df = pd.DataFrame(tier_results)
    output_path = os.path.join(OUTPUT_DIR, "geographic_tier_efficiency.csv")
    results_df.to_csv(output_path, index=False)
    print(f"\n  💾 Saved: {output_path}")
    
    # Print key insight
    if len(tier_results) >= 2:
        print("\n  📌 KEY INSIGHT: Geographic Efficiency Paradox")
        tier_1 = next((t for t in tier_results if t['tier'] == 'Tier-1'), None)
        tier_2 = next((t for t in tier_results if t['tier'] == 'Tier-2'), None)
        if tier_1 and tier_2:
            print(f"     Tier-2 utilization: {tier_2['utilization']:.2%} vs Tier-1: {tier_1['utilization']:.2%}")


# ================================================================================
# PREDICTIVE INDICATORS: BACKLOG PREDICTION MODEL
# ================================================================================

def build_backlog_prediction_model(df_demo, df_bio, df_enrol):
    """
    Build a predictive model to forecast high backlog risk.
    Uses weekly aggregated data with Random Forest classifier.
    
    Args:
        df_demo: Cleaned demographic dataframe
        df_bio: Cleaned biometric dataframe
        df_enrol: Cleaned enrolment dataframe
    
    Saves:
        - backlog_prediction_features.csv
        - backlog_model_feature_importance.csv
    """
    print("\n" + "=" * 80)
    print("SECTION 5: PREDICTIVE MODEL - BACKLOG RISK PREDICTION")
    print("=" * 80)
    
    if df_demo.empty or df_bio.empty:
        print("  ⚠️ Cannot compute: Missing demographic or biometric data")
        return
    
    # -------------------------------------------------------------------------
    # PREPARE WEEKLY AGGREGATED DATA
    # -------------------------------------------------------------------------
    print("\n📊 Preparing weekly aggregated features...")
    
    df_demo = df_demo.copy()
    df_bio = df_bio.copy()
    df_enrol = df_enrol.copy()
    
    # Add totals
    df_demo['total_demo'] = df_demo['demo_age_5_17'] + df_demo['demo_age_17_']
    df_bio['total_bio'] = df_bio['bio_age_5_17'] + df_bio['bio_age_17_']
    
    if not df_enrol.empty:
        df_enrol['total_enrol'] = df_enrol['age_0_5'] + df_enrol['age_5_17'] + df_enrol['age_18_greater']
    
    # Add week column
    df_demo['week'] = df_demo['date'].dt.isocalendar().week
    df_demo['year'] = df_demo['date'].dt.year
    df_bio['week'] = df_bio['date'].dt.isocalendar().week
    df_bio['year'] = df_bio['date'].dt.year
    
    if not df_enrol.empty:
        df_enrol['week'] = df_enrol['date'].dt.isocalendar().week
        df_enrol['year'] = df_enrol['date'].dt.year
    
    # Aggregate by state and week
    demo_weekly = df_demo.groupby(['state', 'year', 'week']).agg({
        'total_demo': 'sum',
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    
    bio_weekly = df_bio.groupby(['state', 'year', 'week']).agg({
        'total_bio': 'sum',
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    
    # Merge demo and bio
    weekly = pd.merge(demo_weekly, bio_weekly, on=['state', 'year', 'week'], how='outer')
    weekly = weekly.fillna(0)
    
    # Merge enrolment if available
    if not df_enrol.empty:
        enrol_weekly = df_enrol.groupby(['state', 'year', 'week']).agg({
            'total_enrol': 'sum',
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum'
        }).reset_index()
        weekly = pd.merge(weekly, enrol_weekly, on=['state', 'year', 'week'], how='outer')
        weekly = weekly.fillna(0)
    else:
        weekly['total_enrol'] = 0
        weekly['age_0_5'] = 0
        weekly['age_5_17'] = 0
        weekly['age_18_greater'] = 0
    
    # Compute backlog
    weekly['backlog'] = weekly['total_demo'] - weekly['total_bio']
    weekly['backlog'] = weekly['backlog'].clip(lower=0)
    
    # Add tier based on state (simplified - assign based on major states)
    def get_state_tier(state):
        major_states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Gujarat']
        tier_2_states = ['Madhya Pradesh', 'Bihar', 'Jharkhand', 'Odisha', 'Kerala', 'Punjab', 'Haryana', 
                        'Uttarakhand', 'Chhattisgarh', 'Andhra Pradesh', 'Rajasthan']
        if state in major_states:
            return 1
        elif state in tier_2_states:
            return 2
        else:
            return 3
    
    weekly['tier'] = weekly['state'].apply(get_state_tier)
    
    # Age mix percentages
    total_age_cols = weekly['age_0_5'] + weekly['age_5_17'] + weekly['age_18_greater']
    weekly['pct_0_5'] = np.where(total_age_cols > 0, weekly['age_0_5'] / total_age_cols * 100, 0)
    weekly['pct_5_17'] = np.where(total_age_cols > 0, weekly['age_5_17'] / total_age_cols * 100, 0)
    weekly['pct_18_plus'] = np.where(total_age_cols > 0, weekly['age_18_greater'] / total_age_cols * 100, 0)
    
    # -------------------------------------------------------------------------
    # CREATE LAGGED FEATURES
    # -------------------------------------------------------------------------
    print("  Creating lagged features...")
    
    # Sort by state and week
    weekly = weekly.sort_values(['state', 'year', 'week'])
    
    # Create lag features for each state
    lagged_features = []
    
    for state in weekly['state'].unique():
        state_data = weekly[weekly['state'] == state].copy()
        state_data = state_data.sort_values(['year', 'week'])
        
        # 1-week lags
        state_data['demo_lag_1'] = state_data['total_demo'].shift(1)
        state_data['bio_lag_1'] = state_data['total_bio'].shift(1)
        state_data['backlog_lag_1'] = state_data['backlog'].shift(1)
        
        # 2-week lags
        state_data['demo_lag_2'] = state_data['total_demo'].shift(2)
        state_data['bio_lag_2'] = state_data['total_bio'].shift(2)
        
        lagged_features.append(state_data)
    
    weekly = pd.concat(lagged_features, ignore_index=True)
    weekly = weekly.dropna()  # Remove rows with NaN from lag
    
    # -------------------------------------------------------------------------
    # CREATE TARGET VARIABLE
    # -------------------------------------------------------------------------
    threshold = weekly['backlog'].quantile(HIGH_BACKLOG_PERCENTILE / 100)
    weekly['high_backlog'] = (weekly['backlog'] > threshold).astype(int)
    
    print(f"  High backlog threshold (P{HIGH_BACKLOG_PERCENTILE}): {threshold:,.0f}")
    print(f"  High backlog samples: {weekly['high_backlog'].sum()} / {len(weekly)}")
    
    # -------------------------------------------------------------------------
    # TRAIN MODEL
    # -------------------------------------------------------------------------
    print("\n📊 Training Random Forest model...")
    
    feature_cols = ['demo_lag_1', 'bio_lag_1', 'backlog_lag_1', 'demo_lag_2', 'bio_lag_2',
                   'tier', 'pct_0_5', 'pct_5_17', 'pct_18_plus']
    
    X = weekly[feature_cols]
    y = weekly['high_backlog']
    
    if len(X) < 10:
        print("  ⚠️ Insufficient data for model training")
        return
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if len(model.classes_) > 1 else y_pred
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    try:
        roc_auc = roc_auc_score(y_test, y_proba)
    except:
        roc_auc = 0.5  # Default if single class
    
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")
    
    # -------------------------------------------------------------------------
    # FEATURE IMPORTANCE
    # -------------------------------------------------------------------------
    print("\n📊 Feature Importance:")
    
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for _, row in importance_df.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # -------------------------------------------------------------------------
    # SAVE OUTPUTS
    # -------------------------------------------------------------------------
    
    # Save features
    features_output = weekly[['state', 'year', 'week', 'total_demo', 'total_bio', 'total_enrol',
                             'backlog', 'tier', 'pct_0_5', 'pct_5_17', 'pct_18_plus',
                             'demo_lag_1', 'bio_lag_1', 'backlog_lag_1', 'high_backlog']]
    features_path = os.path.join(OUTPUT_DIR, "backlog_prediction_features.csv")
    features_output.to_csv(features_path, index=False)
    print(f"\n  💾 Saved: {features_path}")
    
    # Save model summary
    model_summary = pd.DataFrame({
        'metric': ['accuracy', 'roc_auc', 'n_train', 'n_test', 'n_features', 'high_backlog_threshold'],
        'value': [accuracy, roc_auc, len(X_train), len(X_test), len(feature_cols), threshold]
    })
    
    importance_output = pd.concat([
        model_summary,
        importance_df.rename(columns={'feature': 'metric', 'importance': 'value'})
    ], ignore_index=True)
    
    importance_path = os.path.join(OUTPUT_DIR, "backlog_model_feature_importance.csv")
    importance_output.to_csv(importance_path, index=False)
    print(f"  💾 Saved: {importance_path}")


# ================================================================================
# MAIN EXECUTION
# ================================================================================

def main():
    """
    Main execution function - runs all analysis components.
    """
    print("\n" + "=" * 80)
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║       UIDAI DATA HACKATHON - COMPREHENSIVE ANALYSIS SOLUTION              ║")
    print("║                    BharatBytes Team Implementation                         ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print("=" * 80)
    
    start_time = datetime.now()
    print(f"\nExecution started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
    
    # -------------------------------------------------------------------------
    # STEP 1: Load and Clean Data
    # -------------------------------------------------------------------------
    df_demo, df_enrol, df_bio = load_and_clean_data()
    
    # -------------------------------------------------------------------------
    # STEP 2: Biometric Lag Analysis
    # -------------------------------------------------------------------------
    compute_biometric_lag(df_demo, df_bio)
    
    # -------------------------------------------------------------------------
    # STEP 3: Age Cohort Efficiency
    # -------------------------------------------------------------------------
    compute_age_cohort_efficiency(df_enrol)
    
    # -------------------------------------------------------------------------
    # STEP 4: Geographic Tier Efficiency
    # -------------------------------------------------------------------------
    compute_geographic_efficiency(df_demo, df_enrol, df_bio)
    
    # -------------------------------------------------------------------------
    # STEP 5: Predictive Model
    # -------------------------------------------------------------------------
    build_backlog_prediction_model(df_demo, df_bio, df_enrol)
    
    # -------------------------------------------------------------------------
    # COMPLETION SUMMARY
    # -------------------------------------------------------------------------
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                        ANALYSIS COMPLETE                                   ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print("=" * 80)
    
    print(f"\n⏱️  Total execution time: {duration:.2f} seconds")
    print(f"\n📁 Output files generated in '{OUTPUT_DIR}/':")
    
    expected_outputs = [
        "biometric_lag_national.csv",
        "biometric_lag_by_state.csv",
        "age_cohort_efficiency.csv",
        "geographic_tier_efficiency.csv",
        "backlog_prediction_features.csv",
        "backlog_model_feature_importance.csv",
        "biometric_lag_plot.png"
    ]
    
    for output_file in expected_outputs:
        filepath = os.path.join(OUTPUT_DIR, output_file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✅ {output_file} ({size:,} bytes)")
        else:
            print(f"  ⚠️ {output_file} (not generated)")
    
    print("\n🏆 Key Insights Generated:")
    print("  1. Biometric Deployment Asymmetry & Processing Backlog")
    print("  2. Age Cohort Misallocation Inefficiency (0-5 year olds)")
    print("  3. Geographic Efficiency Paradox (Tier-2 vs Tier-1)")
    print("  4. Predictive Risk Model for High Backlog States")
    
    print("\n" + "=" * 80)
    print("Analysis complete. Ready for hackathon submission! 🚀")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
