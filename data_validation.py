import pandas as pd
import numpy as np
import sys

# Configuration
FILES = {
    'pre-war': 'data/raw/beforeDDay.csv',
    'week-before': 'data/raw/weekBeforeDDay.csv',
    'war-period': 'data/raw/afterDDay.csv'
}

def load_and_check_integrity(name, file_path):
    """Load dataset and perform basic integrity checks (completeness, duplication)."""
    print(f"--- Load & Integrity Check [{name}] ---")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None
    
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    
    if 'event_date' in df.columns:
        print(f"Min event_date: {df['event_date'].min()}")
        print(f"Max event_date: {df['event_date'].max()}")
    
    dup_ids = df['event_id_cnty'].duplicated().sum()
    print(f"Duplicate event_id_cnty: {dup_ids}")
    
    missing_counts = df.isnull().sum()
    missing_cols = missing_counts[missing_counts > 0]
    if not missing_cols.empty:
        print("Missing values per column (only > 0 shown):")
        print(missing_cols)
    else:
        print("No missing values found.")
    print("-" * 30)
    return df

def check_schema_consistency(dfs):
    """Verify that all datasets have consistent columns and data types."""
    print("\n--- Schema Consistency Check ---")
    
    reference_name = list(dfs.keys())[0]
    reference_df = dfs[reference_name]
    ref_cols = list(reference_df.columns)
    ref_dtypes = reference_df.dtypes
    
    all_consistent = True
    
    for name, df in dfs.items():
        if name == reference_name:
            continue
            
        print(f"Comparing {name} vs {reference_name}:")
        
        # Column names consistency
        curr_cols = list(df.columns)
        if curr_cols != ref_cols:
            all_consistent = False
            print("  ! Column list NOT identical")
            missing = set(ref_cols) - set(curr_cols)
            if missing:
                print(f"  ! Missing in {name}: {missing}")
            extra = set(curr_cols) - set(ref_cols)
            if extra:
                print(f"  ! Extra in {name}: {extra}")
        else:
            print("  - Column names/order: OK")
            
        # Dtype consistency
        common_cols = set(ref_cols).intersection(set(curr_cols))
        for col in common_cols:
            if df[col].dtype != ref_dtypes[col]:
                print(f"  ! Dtype mismatch in '{col}': {reference_name}={ref_dtypes[col]} vs {name}={df[col].dtype}")
    
    if all_consistent:
        print("Schema appears consistent across verified files.")

def check_temporal_sanity(dfs):
    """Verify event dates fall within expected analysis windows."""
    print("\n--- Temporal Sanity Checks ---")
    
    for name, df in dfs.items():
        print(f"Checking {name}...")
        try:
            dates = pd.to_datetime(df['event_date'])
        except Exception as e:
            print(f"  ! Could not parse dates: {e}")
            continue
            
        d_min, d_max = dates.min(), dates.max()
        print(f"  Range: {d_min.date()} to {d_max.date()}")
        
        # Window anomaly checks
        if name == 'pre-war':
             if d_max > pd.Timestamp('2023-04-10'): 
                 print(f"  ! Date outside expected pre-war window (ends 2023-04-10)")
        elif name == 'week-before':
             if d_min < pd.Timestamp('2023-04-11') or d_max > pd.Timestamp('2023-04-14'): 
                 print(f"  ! Date outside expected week-before window (11-14 Apr 2023)")
        elif name == 'war-period':
             if d_min < pd.Timestamp('2023-04-15'): 
                 print(f"  ! Date outside expected war-period window (starts 2023-04-15)")

        # Year consistency
        if 'year' in df.columns:
            date_years = dates.dt.year
            mismatches = df[df['year'] != date_years]
            if not mismatches.empty:
                print(f"  ! {len(mismatches)} rows have 'year' column mismatching 'event_date'")
        
        # Time precision distribution
        if 'time_precision' in df.columns:
            print("  Time Precision Distribution:")
            print(df['time_precision'].value_counts().sort_index())
        else:
            print("  ! 'time_precision' column missing")

def check_spatial_precision(dfs):
    """Analyze the usage of geo_precision codes to assess spatial reliability."""
    print("\n--- Spatial Precision Diagnostics ---")
    for name, df in dfs.items():
        if 'geo_precision' not in df.columns:
            print(f"{name}: 'geo_precision' missing")
            continue
            
        counts = df['geo_precision'].value_counts().sort_index()
        total = len(df)
        print(f"Dataset: {name}")
        for prec in [1, 2, 3]:
            c = counts.get(prec, 0)
            pct = (c / total) * 100 if total > 0 else 0
            print(f"  geo_precision={prec}: {c} ({pct:.1f}%)")

def check_fatalities_volume(dfs):
    """Check total events and fatality counts for baseline metrics."""
    print("\n--- Fatalities & Event Volume Baseline ---")
    for name, df in dfs.items():
        print(f"Dataset: {name}")
        n_events = len(df)
        print(f"  Total events: {n_events}")
        
        if 'fatalities' in df.columns:
            total_fatal = df['fatalities'].sum()
            median_fatal = df['fatalities'].median()
            zero_fatal_pct = (len(df[df['fatalities'] == 0]) / n_events) * 100 if n_events > 0 else 0
            
            print(f"  Total fatalities: {total_fatal}")
            print(f"  Median fatalities: {median_fatal}")
            print(f"  Events with 0 fatalities: {zero_fatal_pct:.1f}%")
        else:
            print("  ! 'fatalities' column missing")

def print_summary():
    """Output key questions for downstream analysis based on validation results."""
    print("\n--- DATA READINESS SUMMARY ---")
    print("Is the data usable for spatial analysis? (See Spatial Precision output)")
    print("Is the data comparable across the three periods? (See Schema Consistency output)")
    
    print("Issues to Address in Cleaning:")
    print("1. Assess dominance of low-precision geo codes (geo_precision > 1).")
    print("2. Verify time_precision consistency across periods.")
    print("3. Validate fatality outliers and zero-fatality reporting rates.")

def main():
    loaded_dfs = {}
    for name, path in FILES.items():
        df = load_and_check_integrity(name, path)
        if df is not None:
            loaded_dfs[name] = df
            
    if len(loaded_dfs) > 0:
        check_schema_consistency(loaded_dfs)
        check_temporal_sanity(loaded_dfs)
        check_spatial_precision(loaded_dfs)
        check_fatalities_volume(loaded_dfs)
        print_summary()
    else:
        print("No data loaded.")

if __name__ == "__main__":
    main()
