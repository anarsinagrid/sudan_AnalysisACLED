import pandas as pd
import numpy as np
import os

# Configuration
FILES = {
    'pre_war': 'data/raw/beforeDDay.csv',
    'week_before': 'data/raw/weekBeforeDDay.csv',
    'war_period': 'data/raw/afterDDay.csv'
}
OUTPUT_FILE = 'data/cleaned_events.csv'

# STRICT Schema
KEEP_COLUMNS = [
    'event_id_cnty', 'event_date', 'year', 'time_precision', 'disorder_type',
    'event_type', 'sub_event_type', 'actor1', 'assoc_actor_1', 'inter1',
    'actor2', 'assoc_actor_2', 'inter2', 'interaction', 'civilian_targeting',
    'iso', 'region', 'country', 'admin1', 'admin2', 'admin3', 'location',
    'latitude', 'longitude', 'geo_precision', 'source', 'source_scale',
    'notes', 'fatalities', 'tags', 'timestamp'
]

def clean_data():
    """
    Loads, cleans, and combines ACLED datasets for different periods.
    
    Steps:
    1. Loads raw CSV files.
    2. Standardizes column names and types.
    3. Creates flag columns for precision and event types.
    4. Normalizes categorical fields.
    5. Merges into a single analysis-ready CSV.
    """
    print("--- STARTING DATA CLEANING ---")
    
    dfs = []
    
    # 1. Load Datasets
    print("\n--- Loading Datasets ---")
    for period, path in FILES.items():
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}")
            return
        
        df = pd.read_csv(path)
        
        # Filter columns to only those in the fixed schema
        missing_cols = set(KEEP_COLUMNS) - set(df.columns)
        if missing_cols:
            print(f"WARNING: {period} missing columns: {missing_cols}")
            df = df.reindex(columns=KEEP_COLUMNS)
        else:
            df = df[KEEP_COLUMNS].copy()
            
        df['period'] = period
        print(f"Loaded {period}: {len(df)} rows")
        dfs.append(df)
    
    processed_dfs = []
    for df in dfs:
        # 2. Standardize Dates & Core Types
        df['event_date'] = pd.to_datetime(df['event_date'])
        
        # Ensure numeric types
        df['fatalities'] = pd.to_numeric(df['fatalities'], errors='coerce').fillna(0)
        df['geo_precision'] = pd.to_numeric(df['geo_precision'], errors='coerce').fillna(-1).astype(int)
        df['time_precision'] = pd.to_numeric(df['time_precision'], errors='coerce').fillna(-1).astype(int)
        
        # 3. Create Precision & Validity Flags
        df['high_geo'] = df['geo_precision'] == 1
        df['low_geo'] = df['geo_precision'] >= 2
        df['exact_time'] = df['time_precision'] == 1
        df['estimated_time'] = df['time_precision'] > 1
        
        # 4. Normalize Key Categorical Fields
        cat_cols = ['event_type', 'sub_event_type', 'admin1', 'admin2', 'actor1', 'actor2']
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()
        
        # 5. Create Analysis-Ready Derived Fields
        df['month'] = df['event_date'].dt.to_period('M').astype(str) # YYYY-MM
        df['is_battle'] = df['event_type'] == "Battles"
        df['is_vac'] = df['event_type'] == "Violence Against Civilians" 
        
        processed_dfs.append(df)
        
    # 6. Combine Datasets
    print("\n--- Combining Datasets ---")
    combined_df = pd.concat(processed_dfs, ignore_index=True)
    
    # Output to CSV
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    combined_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved cleaned data to: {OUTPUT_FILE}")
    
    # Final Summary
    print("\n--- SUMMARY ---")
    print(f"Total rows: {len(combined_df)}")
    print("Rows per period:")
    print(combined_df['period'].value_counts())
    
    pct_high_geo = (combined_df['high_geo'].sum() / len(combined_df)) * 100
    pct_exact_time = (combined_df['exact_time'].sum() / len(combined_df)) * 100
    
    print(f"% high_geo: {pct_high_geo:.2f}%")
    print(f"% exact_time: {pct_exact_time:.2f}%")
    
    # Cleaning Completion Checklist
    print("\n--- CLEANING COMPLETION CHECKLIST ---")
    
    # Check if rows dropped
    total_input = sum(len(d) for d in dfs)
    rows_dropped = total_input != len(combined_df)
    print(f"Were any rows dropped? {'Yes' if rows_dropped else 'No'}")
    
    # Check derived columns
    derived_cols = ['period', 'high_geo', 'low_geo', 'exact_time', 'estimated_time', 'month', 'is_battle', 'is_vac']
    missing_derived = [c for c in derived_cols if c not in combined_df.columns]
    all_derived = len(missing_derived) == 0
    print(f"Are all derived columns present? {'Yes' if all_derived else 'No'}")
    
    # Readiness check
    ready = not rows_dropped and all_derived
    print(f"Is the dataset ready for aggregation? {'Yes' if ready else 'No'} (Standardized types, dates, flags created, no rows dropped)")

if __name__ == "__main__":
    clean_data()
