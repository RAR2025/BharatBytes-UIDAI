import pandas as pd
import sys
import os

if len(sys.argv) != 2:
    print("api_data_aadhar_biometric\api_data_aadhar_biometric_0_500000.csv")
    sys.exit(1)

input_file = sys.argv[1]

# Read CSV
df = pd.read_csv(input_file)

# Check if pincode column exists
if "pincode" not in df.columns:
    print("Error: CSV must contain a column named 'pincode'")
    sys.exit(1)

# Convert pincode to numeric for proper sorting (handles strings like "380001")
df["pincode"] = pd.to_numeric(df["pincode"], errors="coerce")

# Sort by pincode
df_sorted = df.sort_values(by="pincode", ascending=True)

# Create output filename
base, ext = os.path.splitext(input_file)
output_file = f"{base}_ascending.csv"

# Save sorted CSV
df_sorted.to_csv(output_file, index=False)

print(f"Sorted file saved as: {output_file}")
