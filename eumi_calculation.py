# EUMI Calculation and Visualization

import pandas as pd
import numpy as np
import plotly.express as px

# Function to compute EUMI

def compute_eumi(df_enrollment, df_biometric):
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
    
    return merged_df

# Function to plot EUMI scatter plot

def plot_eumi_scatter(df):
    fig = px.scatter(df, x='enroll_share', y='usage_share', color='category',
                     title='EUMI Scatter Plot',
                     labels={'enroll_share': 'Enrollment Share', 'usage_share': 'Usage Share'})
    return fig
