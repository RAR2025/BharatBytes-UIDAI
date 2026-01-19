"""
================================================================================
DIGITAL INFRASTRUCTURE READINESS vs GROUND REALITY (PS-3)
================================================================================

Problem Statement 3: Analyzes the gap between reported digital infrastructure
capabilities and actual ground-level biometric transaction patterns.

This module computes three district-level indices:
1. Infrastructure Stress Index (ISI) - Measures volatility and capacity stress
2. Reporting Consistency Score (RCS) - Measures regularity of data reporting
3. Age Balance Score (ABS) - Measures equity across age demographics

Districts are classified into four typologies based on composite scores.

Author: Team Bharat Bytes
UIDAI Data Hackathon 2026
================================================================================
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

# ================================================================================
# CONFIGURATION
# ================================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILTERED_DATA_DIR = os.path.join(BASE_DIR, "filtered_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Input file
BIOMETRIC_FILE = os.path.join(FILTERED_DATA_DIR, "consolidated_biometric.csv")

# Output files
INDICES_OUTPUT = os.path.join(OUTPUT_DIR, "digital_infrastructure_indices.csv")
TYPOLOGY_OUTPUT = os.path.join(OUTPUT_DIR, "digital_infrastructure_typology.csv")


# ================================================================================
# DATA LOADING
# ================================================================================

def load_biometric_data():
    """
    Load the consolidated biometric dataset.
    
    Returns:
        pd.DataFrame: Biometric transactions data with date parsed
    """
    print(f"[INFO] Loading biometric data from: {BIOMETRIC_FILE}")
    
    if not os.path.exists(BIOMETRIC_FILE):
        raise FileNotFoundError(f"Biometric data file not found: {BIOMETRIC_FILE}")
    
    df = pd.read_csv(BIOMETRIC_FILE)
    
    # Parse date column (format: DD-MM-YYYY)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Calculate total biometric transactions per record
    # bio_age_5_17 = biometric transactions for age 5-17
    # bio_age_17_ = biometric transactions for age 17+
    df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    # Extract year-month for temporal aggregation
    df['year_month'] = df['date'].dt.to_period('M')
    
    print(f"[INFO] Loaded {len(df):,} records spanning {df['date'].min()} to {df['date'].max()}")
    
    return df


# ================================================================================
# INDEX CALCULATIONS
# ================================================================================

def compute_infrastructure_stress_index(df):
    """
    Compute Infrastructure Stress Index (ISI) for each district.
    
    Methodology:
    - Higher transaction volume indicates infrastructure load
    - Higher coefficient of variation (CV) indicates volatility/stress
    - Normalized to 0-1 scale where 1 = high stress
    
    Policy Relevance:
    - Districts with high ISI may need infrastructure capacity upgrades
    - Volatile patterns suggest unreliable service delivery
    
    Args:
        df: Biometric data with year_month column
        
    Returns:
        pd.DataFrame: District-level ISI scores
    """
    print("[INFO] Computing Infrastructure Stress Index (ISI)...")
    
    # Aggregate monthly totals by state, district
    monthly = df.groupby(['state', 'district', 'year_month'])['total_bio'].sum().reset_index()
    
    # Calculate statistics per district
    district_stats = monthly.groupby(['state', 'district']).agg(
        mean_volume=('total_bio', 'mean'),
        std_volume=('total_bio', 'std'),
        max_volume=('total_bio', 'max'),
        months_active=('year_month', 'count')
    ).reset_index()
    
    # Coefficient of Variation (CV) = std / mean
    # Higher CV indicates more volatility = more stress
    district_stats['cv'] = district_stats['std_volume'] / district_stats['mean_volume']
    district_stats['cv'] = district_stats['cv'].fillna(0)
    
    # Combine volume and volatility for stress score
    # High volume + high volatility = high stress
    # Normalize each component to 0-1
    max_volume = district_stats['mean_volume'].max()
    max_cv = district_stats['cv'].max()
    
    if max_volume > 0:
        district_stats['volume_normalized'] = district_stats['mean_volume'] / max_volume
    else:
        district_stats['volume_normalized'] = 0
    
    if max_cv > 0:
        district_stats['cv_normalized'] = district_stats['cv'] / max_cv
    else:
        district_stats['cv_normalized'] = 0
    
    # ISI = weighted combination (volume contributes to load, CV to stress)
    # 40% volume load + 60% volatility stress
    district_stats['ISI'] = (0.4 * district_stats['volume_normalized'] + 
                            0.6 * district_stats['cv_normalized'])
    
    # Normalize ISI to 0-1 scale
    isi_min = district_stats['ISI'].min()
    isi_max = district_stats['ISI'].max()
    if isi_max > isi_min:
        district_stats['ISI'] = (district_stats['ISI'] - isi_min) / (isi_max - isi_min)
    else:
        district_stats['ISI'] = 0
    
    print(f"[INFO] ISI computed for {len(district_stats)} districts")
    
    return district_stats[['state', 'district', 'ISI', 'mean_volume', 'cv', 'months_active']]


def compute_reporting_consistency_score(df):
    """
    Compute Reporting Consistency Score (RCS) for each district.
    
    Methodology:
    - Calculate percentage of months with non-zero biometric reporting
    - Districts should ideally report every month
    - Missing months indicate infrastructure gaps or data quality issues
    - Normalized to 0-1 scale where 1 = perfect consistency
    
    Policy Relevance:
    - Low RCS indicates unreliable ground infrastructure
    - Gaps in reporting may hide service delivery failures
    
    Args:
        df: Biometric data with year_month column
        
    Returns:
        pd.DataFrame: District-level RCS scores
    """
    print("[INFO] Computing Reporting Consistency Score (RCS)...")
    
    # Get all unique months in the dataset
    all_months = df['year_month'].unique()
    total_possible_months = len(all_months)
    
    print(f"[INFO] Total months in dataset: {total_possible_months}")
    
    # Count months with non-zero reporting per district
    monthly_reporting = df.groupby(['state', 'district', 'year_month'])['total_bio'].sum().reset_index()
    
    # Count months with actual transactions (non-zero)
    district_months = monthly_reporting[monthly_reporting['total_bio'] > 0].groupby(
        ['state', 'district']
    ).size().reset_index(name='months_with_data')
    
    # RCS = months_with_data / total_possible_months
    district_months['RCS'] = district_months['months_with_data'] / total_possible_months
    
    # Ensure RCS is in 0-1 range
    district_months['RCS'] = district_months['RCS'].clip(0, 1)
    
    print(f"[INFO] RCS computed for {len(district_months)} districts")
    
    return district_months[['state', 'district', 'RCS', 'months_with_data']]


def compute_age_balance_score(df):
    """
    Compute Age Balance Score (ABS) for each district.
    
    Methodology:
    - Measures how evenly distributed transactions are across age groups
    - Uses normalized entropy / Gini-like measure
    - Higher score = more balanced age distribution
    - Lower score = one age group dominates (potential bias)
    
    Policy Relevance:
    - Balanced usage indicates equitable service delivery
    - Dominance by single age group may indicate targeting gaps
    
    Args:
        df: Biometric data with age group columns
        
    Returns:
        pd.DataFrame: District-level ABS scores
    """
    print("[INFO] Computing Age Balance Score (ABS)...")
    
    # Aggregate total transactions per age group per district
    district_age = df.groupby(['state', 'district']).agg(
        total_5_17=('bio_age_5_17', 'sum'),
        total_17_plus=('bio_age_17_', 'sum')
    ).reset_index()
    
    # Total transactions
    district_age['total'] = district_age['total_5_17'] + district_age['total_17_plus']
    
    # Calculate proportions
    district_age['prop_5_17'] = district_age['total_5_17'] / district_age['total']
    district_age['prop_17_plus'] = district_age['total_17_plus'] / district_age['total']
    
    # Handle division by zero
    district_age['prop_5_17'] = district_age['prop_5_17'].fillna(0)
    district_age['prop_17_plus'] = district_age['prop_17_plus'].fillna(0)
    
    # Balance Score using entropy-based approach
    # For 2 categories, max entropy = log2(2) = 1 (when 50-50 split)
    # Entropy = -sum(p * log2(p)) for p > 0
    def calculate_entropy(row):
        props = [row['prop_5_17'], row['prop_17_plus']]
        entropy = 0
        for p in props:
            if p > 0:
                entropy -= p * np.log2(p)
        # Normalize by max entropy (log2(2) = 1)
        return entropy / 1.0  # Already normalized for 2 categories
    
    district_age['ABS'] = district_age.apply(calculate_entropy, axis=1)
    
    # Ensure ABS is in 0-1 range
    district_age['ABS'] = district_age['ABS'].clip(0, 1)
    
    print(f"[INFO] ABS computed for {len(district_age)} districts")
    
    return district_age[['state', 'district', 'ABS', 'prop_5_17', 'prop_17_plus']]


# ================================================================================
# TYPOLOGY CLASSIFICATION
# ================================================================================

def classify_districts(indices_df):
    """
    Classify districts into four typologies based on composite indices.
    
    Typologies:
    1. Digitally Strong & Balanced
       - Low stress (ISI < 0.5), High consistency (RCS > 0.5), High balance (ABS > 0.5)
       
    2. Digitally Strong but Overburdened
       - High stress (ISI >= 0.5), High consistency (RCS > 0.5)
       - Infrastructure exists but is under pressure
       
    3. Digitally Weak but Stable
       - Low stress (ISI < 0.5), Low consistency (RCS <= 0.5)
       - Limited activity but stable when operational
       
    4. Digitally Underserved
       - Low consistency (RCS <= 0.5), Low balance (ABS <= 0.5)
       - Poor infrastructure and inequitable service delivery
    
    Policy Relevance:
    - Strong & Balanced: Model districts for replication
    - Overburdened: Need capacity expansion
    - Weak but Stable: Need infrastructure investment
    - Underserved: Priority for comprehensive intervention
    
    Args:
        indices_df: DataFrame with ISI, RCS, ABS columns
        
    Returns:
        pd.DataFrame: District typology classifications
    """
    print("[INFO] Classifying districts into typologies...")
    
    df = indices_df.copy()
    
    def assign_typology(row):
        isi = row['ISI']
        rcs = row['RCS']
        abs_score = row['ABS']
        
        # Classification logic based on thresholds
        if rcs > 0.5 and isi < 0.5 and abs_score > 0.5:
            return "Digitally Strong & Balanced"
        elif rcs > 0.5 and isi >= 0.5:
            return "Digitally Strong but Overburdened"
        elif rcs <= 0.5 and isi < 0.5:
            return "Digitally Weak but Stable"
        else:
            return "Digitally Underserved"
    
    df['typology'] = df.apply(assign_typology, axis=1)
    
    # Count typologies
    typology_counts = df['typology'].value_counts()
    print("[INFO] Typology distribution:")
    for typology, count in typology_counts.items():
        print(f"       - {typology}: {count} districts")
    
    return df[['state', 'district', 'typology']]


# ================================================================================
# MAIN EXECUTION
# ================================================================================

def main():
    """
    Main execution function for PS-3 Digital Infrastructure Readiness analysis.
    
    Workflow:
    1. Load biometric transaction data
    2. Compute ISI, RCS, ABS indices
    3. Merge indices into composite dataset
    4. Classify districts into typologies
    5. Save outputs to CSV
    """
    print("=" * 80)
    print("DIGITAL INFRASTRUCTURE READINESS vs GROUND REALITY (PS-3)")
    print("UIDAI Data Hackathon 2026 | Team Bharat Bytes")
    print("=" * 80)
    print()
    
    start_time = datetime.now()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Load data
    print("[STEP 1/5] Loading biometric data...")
    df = load_biometric_data()
    print()
    
    # Step 2: Compute indices
    print("[STEP 2/5] Computing Infrastructure Stress Index (ISI)...")
    isi_df = compute_infrastructure_stress_index(df)
    print()
    
    print("[STEP 3/5] Computing Reporting Consistency Score (RCS)...")
    rcs_df = compute_reporting_consistency_score(df)
    print()
    
    print("[STEP 4/5] Computing Age Balance Score (ABS)...")
    abs_df = compute_age_balance_score(df)
    print()
    
    # Step 3: Merge all indices
    print("[STEP 5/5] Merging indices and classifying districts...")
    
    # Merge on state + district
    indices_df = isi_df.merge(rcs_df, on=['state', 'district'], how='outer')
    indices_df = indices_df.merge(abs_df, on=['state', 'district'], how='outer')
    
    # Fill any missing scores with 0
    indices_df['ISI'] = indices_df['ISI'].fillna(0)
    indices_df['RCS'] = indices_df['RCS'].fillna(0)
    indices_df['ABS'] = indices_df['ABS'].fillna(0)
    
    # Round indices to 4 decimal places for readability
    indices_df['ISI'] = indices_df['ISI'].round(4)
    indices_df['RCS'] = indices_df['RCS'].round(4)
    indices_df['ABS'] = indices_df['ABS'].round(4)
    
    # Step 4: Classify districts
    typology_df = classify_districts(indices_df)
    print()
    
    # Step 5: Save outputs
    print("[OUTPUT] Saving results...")
    
    # Select columns for indices output
    indices_output = indices_df[['state', 'district', 'ISI', 'RCS', 'ABS', 
                                  'mean_volume', 'cv', 'months_active', 
                                  'months_with_data', 'prop_5_17', 'prop_17_plus']]
    indices_output.to_csv(INDICES_OUTPUT, index=False)
    print(f"[SAVED] {INDICES_OUTPUT}")
    
    # Save typology output
    typology_df.to_csv(TYPOLOGY_OUTPUT, index=False)
    print(f"[SAVED] {TYPOLOGY_OUTPUT}")
    
    # Summary statistics
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Total districts analyzed: {len(indices_df)}")
    print(f"Output files saved to: {OUTPUT_DIR}")
    print()
    print("Index Summary:")
    print(f"  - ISI (Infrastructure Stress): min={indices_df['ISI'].min():.4f}, "
          f"max={indices_df['ISI'].max():.4f}, mean={indices_df['ISI'].mean():.4f}")
    print(f"  - RCS (Reporting Consistency): min={indices_df['RCS'].min():.4f}, "
          f"max={indices_df['RCS'].max():.4f}, mean={indices_df['RCS'].mean():.4f}")
    print(f"  - ABS (Age Balance): min={indices_df['ABS'].min():.4f}, "
          f"max={indices_df['ABS'].max():.4f}, mean={indices_df['ABS'].mean():.4f}")
    print()
    
    elapsed = datetime.now() - start_time
    print(f"Execution time: {elapsed.total_seconds():.2f} seconds")
    print("=" * 80)


if __name__ == "__main__":
    main()
