"""
Consolidate and Normalize Aadhaar Datasets
Combines all CSV files for biometric, demographic, and enrolment data
Applies state name normalization to all records
Creates filtered_data folder with 3 consolidated CSV files
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# STATE NORMALIZATION MAPPING AND OFFICIAL STATES
# ============================================================================

OFFICIAL_STATES = {
    'Andhra Pradesh',
    'Arunachal Pradesh',
    'Assam',
    'Bihar',
    'Chhattisgarh',
    'Goa',
    'Gujarat',
    'Haryana',
    'Himachal Pradesh',
    'Jharkhand',
    'Karnataka',
    'Kerala',
    'Madhya Pradesh',
    'Maharashtra',
    'Manipur',
    'Meghalaya',
    'Mizoram',
    'Nagaland',
    'Odisha',
    'Punjab',
    'Rajasthan',
    'Sikkim',
    'Tamil Nadu',
    'Telangana',
    'Tripura',
    'Uttar Pradesh',
    'Uttarakhand',
    'West Bengal',
    'Andaman & Nicobar Islands',
    'Chandigarh',
    'Dadra & Nagar Haveli and Daman & Diu',
    'Lakshadweep',
    'Delhi',
    'Puducherry',
    'Ladakh',
    'Jammu & Kashmir'
}

GEOGRAPHIC_NAME_MAPPING = {
    # Puducherry variations
    'pondicherry': 'Puducherry',
    'pondi': 'Puducherry',
    'puduchery': 'Puducherry',
    'pondy': 'Puducherry',
    
    # Jammu & Kashmir variations
    'j&k': 'Jammu & Kashmir',
    'jk': 'Jammu & Kashmir',
    'j & k': 'Jammu & Kashmir',
    'jammu kashmir': 'Jammu & Kashmir',
    'jammu and kashmir': 'Jammu & Kashmir',
    
    # Andaman & Nicobar variations
    'a & n islands': 'Andaman & Nicobar Islands',
    'a&n': 'Andaman & Nicobar Islands',
    'andaman & nicobar': 'Andaman & Nicobar Islands',
    'andaman nicobar': 'Andaman & Nicobar Islands',
    'a and n islands': 'Andaman & Nicobar Islands',
    'andaman and nicobar': 'Andaman & Nicobar Islands',
    'andaman and nicobar islands': 'Andaman & Nicobar Islands',
    
    # West Bengal variations
    'west bangal': 'West Bengal',
    'westbengal': 'West Bengal',
    'west bengli': 'West Bengal',
    'west bengal': 'West Bengal',
    'westbengali': 'West Bengal',
    
    # Historical names
    'orissa': 'Odisha',
    'uttaranchal': 'Uttarakhand',
    'uttaranchl': 'Uttarakhand',
    
    # Dadra & Nagar Haveli and Daman & Diu
    'dadra and nagar haveli and daman and diu': 'Dadra & Nagar Haveli and Daman & Diu',
    'dadra & nagar haveli and daman & diu': 'Dadra & Nagar Haveli and Daman & Diu',
    'dadra nagar haveli daman diu': 'Dadra & Nagar Haveli and Daman & Diu',
    'dnhdd': 'Dadra & Nagar Haveli and Daman & Diu',
    
    # Other variations with & symbol
    'himachal pradesh': 'Himachal Pradesh',
    'madhya pradesh': 'Madhya Pradesh',
    'andhra pradesh': 'Andhra Pradesh',
    'arunachal pradesh': 'Arunachal Pradesh',
    
    # Duplicate state names
    'tamilnadu': 'Tamil Nadu',
    'chhatisgarh': 'Chhattisgarh',
}

# Invalid state entries (districts, cities, or junk data mistakenly marked as states)
INVALID_STATES = {
    '100000',  # Pincode
    'Balanagar',  # District in Telangana
    'Darbhanga',  # District in Bihar
    'Jaipur',  # District in Rajasthan (capital city)
    'Madanapalle',  # Town in Andhra Pradesh
    'Nagpur',  # District in Maharashtra
    'Puttenahalli',  # Locality in Bangalore
    'Raja Annamalai Puram',  # Locality in Chennai
}

# ============================================================================
# NORMALIZATION FUNCTIONS
# ============================================================================

def normalize_geographic_text(text):
    """
    Normalize geographic text by applying comprehensive text processing
    """
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text).strip()
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Replace common symbols
    text_lower = text_lower.replace('&', 'and')
    text_lower = text_lower.replace('-', ' ')
    
    # Remove extra whitespace
    text_lower = ' '.join(text_lower.split())
    
    # Check direct mapping
    if text_lower in GEOGRAPHIC_NAME_MAPPING:
        return GEOGRAPHIC_NAME_MAPPING[text_lower]
    
    # Try partial matches
    for key, value in GEOGRAPHIC_NAME_MAPPING.items():
        if key in text_lower or text_lower in key:
            return value
    
    # Return title case if no mapping found
    return text.title()

def validate_and_correct_state(state_name):
    """
    Validate state name and return corrected version
    Filters out invalid entries (districts, pincodes, etc.)
    """
    if pd.isna(state_name) or state_name == '':
        return ''
    
    state_name = str(state_name).strip()
    
    # Check if it's a known invalid entry (district, city, or junk data)
    if state_name in INVALID_STATES:
        return ''  # Return empty string to filter out
    
    # Check if it's a numeric value (likely a pincode)
    if state_name.isdigit():
        return ''
    
    normalized = normalize_geographic_text(state_name)
    
    # Check if normalized state is in official states
    if normalized in OFFICIAL_STATES:
        return normalized
    
    # If not in official states, check if it's an invalid entry
    if normalized in INVALID_STATES:
        return ''
    
    # Return title case version as fallback
    return normalized.title()

# ============================================================================
# DATA CONSOLIDATION AND NORMALIZATION
# ============================================================================

def load_and_consolidate_dataset(folder_path, file_pattern, dataset_name):
    """
    Load all CSV files matching pattern, consolidate, and normalize
    """
    print(f"\n{'='*70}")
    print(f"Processing {dataset_name} Dataset")
    print(f"{'='*70}")
    
    # Get all CSV files matching pattern
    csv_files = list(Path(folder_path).glob(f"*.csv"))
    csv_files = [f for f in csv_files if file_pattern in f.name]
    csv_files = sorted(csv_files)
    
    if not csv_files:
        print(f"❌ No CSV files found matching pattern: {file_pattern}")
        return None
    
    print(f"Found {len(csv_files)} files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Load and consolidate all CSV files
    dfs = []
    total_rows = 0
    
    for file_path in csv_files:
        try:
            print(f"\n📂 Loading: {file_path.name}...", end='')
            df = pd.read_csv(file_path, low_memory=False)
            print(f" ✓ ({len(df):,} rows)")
            dfs.append(df)
            total_rows += len(df)
        except Exception as e:
            print(f" ❌ Error: {e}")
            continue
    
    if not dfs:
        print(f"❌ No data loaded successfully")
        return None
    
    # Concatenate all dataframes
    print(f"\n📊 Consolidating {len(dfs)} files...")
    consolidated_df = pd.concat(dfs, ignore_index=True)
    print(f"   Total rows: {len(consolidated_df):,}")
    print(f"   Total columns: {len(consolidated_df.columns)}")
    
    # Identify state column
    state_column = None
    possible_names = ['state', 'State', 'STATE', 'state_name', 'State_Name']
    
    for col in possible_names:
        if col in consolidated_df.columns:
            state_column = col
            break
    
    if state_column is None:
        # Try fuzzy match
        for col in consolidated_df.columns:
            if 'state' in col.lower():
                state_column = col
                break
    
    if state_column:
        print(f"\n🔍 Found state column: '{state_column}'")
        print(f"   Unique states before normalization: {consolidated_df[state_column].nunique()}")
        
        # Apply normalization
        print(f"   Normalizing state names...", end='')
        consolidated_df[state_column] = consolidated_df[state_column].apply(
            validate_and_correct_state
        )
        
        # Remove rows with empty state names (invalid entries)
        rows_before = len(consolidated_df)
        consolidated_df = consolidated_df[consolidated_df[state_column] != '']
        rows_after = len(consolidated_df)
        rows_removed = rows_before - rows_after
        
        unique_states_after = consolidated_df[state_column].nunique()
        print(f" ✓")
        print(f"   Unique states after normalization: {unique_states_after}")
        print(f"   Rows removed (invalid states): {rows_removed:,}")
        
        # Show state distribution
        print(f"\n   State Distribution:")
        state_counts = consolidated_df[state_column].value_counts().head(10)
        for state, count in state_counts.items():
            print(f"      {state}: {count:,}")
    else:
        print(f"⚠️  Warning: Could not identify state column")
    
    return consolidated_df

def main():
    """
    Main execution function
    """
    print("\n" + "="*70)
    print("AADHAAR DATA CONSOLIDATION AND NORMALIZATION")
    print("="*70)
    
    # Setup paths
    base_path = Path("c:\\Users\\RUTURAJ\\D_Drive\\Desktop\\Coding\\AAdhar hackathon\\BharatBytes-UIDAI")
    
    biometric_folder = base_path / "api_data_aadhar_biometric"
    demographic_folder = base_path / "api_data_aadhar_demographic"
    enrolment_folder = base_path / "api_data_aadhar_enrolment"
    output_folder = base_path / "filtered_data"
    
    # Create output folder
    output_folder.mkdir(exist_ok=True)
    print(f"\n📁 Output folder: {output_folder}")
    
    # Process each dataset type
    datasets = [
        (biometric_folder, "api_data_aadhar_biometric", "Biometric", "consolidated_biometric.csv"),
        (demographic_folder, "api_data_aadhar_demographic", "Demographic", "consolidated_demographic.csv"),
        (enrolment_folder, "api_data_aadhar_enrolment", "Enrolment", "consolidated_enrolment.csv"),
    ]
    
    output_files = []
    
    for folder, pattern, dataset_name, output_filename in datasets:
        if not folder.exists():
            print(f"\n❌ Folder not found: {folder}")
            continue
        
        # Load and consolidate
        df = load_and_consolidate_dataset(folder, pattern, dataset_name)
        
        if df is not None and len(df) > 0:
            # Save consolidated file
            output_path = output_folder / output_filename
            print(f"\n💾 Saving to: {output_filename}...", end='')
            df.to_csv(output_path, index=False)
            print(f" ✓")
            output_files.append((dataset_name, output_filename, len(df)))
            print(f"   Size: {output_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Summary report
    print(f"\n{'='*70}")
    print("CONSOLIDATION SUMMARY")
    print(f"{'='*70}")
    
    if output_files:
        print(f"\n✓ Successfully created {len(output_files)} consolidated files:\n")
        for dataset_name, filename, row_count in output_files:
            filepath = output_folder / filename
            size_mb = filepath.stat().st_size / (1024*1024)
            print(f"   📄 {filename}")
            print(f"      Type: {dataset_name}")
            print(f"      Rows: {row_count:,}")
            print(f"      Size: {size_mb:.2f} MB")
            print()
        
        print(f"✅ All files saved to: {output_folder}")
    else:
        print(f"❌ No files were successfully processed")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
