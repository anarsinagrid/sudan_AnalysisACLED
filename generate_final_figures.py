"""
generate_final_figures.py

Generates static PNG figures for the Sudan Conflict Report.
Figures included:
1. F1: Fatalities Structural Break
2. F2: Event Composition Shift
3. F6: Conflict Distribution Map (Choropleth + Hotspots)
4. F9: Source Reporting Scale
5. AX_06: Actor Activity Timelines
6. AX_04: Behavioral DNA (Actor Event Distribution)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import contextily as cx
import os

INPUT_FILE = 'data/cleaned_events.csv'
ADMIN1_SHP = 'data/sudan_admin1.geojson'
OUTPUT_DIR = 'final_figures'

def main():
    """Main execution function to generate all static figures."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Creating output directory: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)

    sns.set_theme(style="white")
    
    print("--- 1. Data Loading & Preprocessing ---")
    df = pd.read_csv(INPUT_FILE)
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    period_map = {
        'pre_war': 'before_war',
        'week_before': 'before_war',
        'war_period': 'war_period'
    }
    df['period_group'] = df['period'].map(period_map).fillna(df['period'])
    print(f"Periods after merge: {df['period_group'].value_counts()}")

    actor_map_fixed = {
        'Military Forces Of Sudan (2019-)': 'SAF',
        'Government Of Sudan (2019-)': 'SAF',
        'Rapid Support Forces': 'RSF',
        'Military Forces Of Sudan (2019-2023) Rapid Support Forces': 'RSF',
        'Military Forces of Sudan (2019-)': 'SAF',
        'Government of Sudan (2019-)': 'SAF'
    }
    df['actor1_norm'] = df['actor1'].replace(actor_map_fixed)
    
    color_map = {
        'SAF': 'forestgreen',
        'RSF': 'goldenrod', 
        'Protesters (Sudan)': 'steelblue',
        'before_war': 'gray',
        'war_period': 'firebrick'
    }

    print("\n--- Generating F1: Fatalities Structural Break ---")
    df['month'] = df['event_date'].dt.to_period('M').dt.to_timestamp()
    
    f1_df = df.groupby(['month', 'period_group'])['fatalities'].sum().reset_index()
    f1_df = f1_df.sort_values('month')
    
    plt.figure(figsize=(12, 6))
    
    for period in ['before_war', 'war_period']:
        subset = f1_df[f1_df['period_group'] == period]
        if not subset.empty:
            subset_rolled = subset.set_index('month')['fatalities'].rolling(window=2, min_periods=1).mean()
            plt.plot(subset_rolled.index, subset_rolled.values, 
                     label=period.replace('_', ' ').title(), 
                     color=color_map.get(period, 'black'), linewidth=2.5)
            
            if period == 'war_period':
                try:
                    s2024 = subset_rolled['2024']
                    if not s2024.empty:
                        early_2024 = s2024[s2024.index.month <= 6]
                        if not early_2024.empty:
                            min_date = early_2024.idxmin()
                            min_val = early_2024.min()
                            anno_date = min_date - pd.DateOffset(months=3)
                            plt.axvline(anno_date, color='grey', linestyle=':', linewidth=1.5)
                            plt.text(anno_date, min_val - 100, f"Shift to Silent War", 
                                     ha='center', va='bottom', fontsize=10, color='grey')

                        late_2024 = s2024[s2024.index.month > 6]
                        if not late_2024.empty:
                            max_date = late_2024.idxmax()
                            max_val = late_2024.max()
                            anno_date = max_date - pd.DateOffset(months=2)
                            plt.axvline(anno_date, color='grey', linestyle=':', linewidth=1.5)
                            plt.text(anno_date, max_val + 50, f"The Battle for El Fasher", 
                                     ha='center', va='bottom', fontsize=10, color='grey')
                except Exception as e:
                    print(f"Could not annotate 2024 points: {e}")
    
    plt.axvline(pd.Timestamp("2023-04-15"), color='black', linestyle='--', linewidth=1.5)
    plt.text(pd.Timestamp("2023-04-15"), plt.ylim()[1]*0.9, ' War Starts (Apr 15)', ha='left', va='top')
    
    plt.title('F1: Fatalities Structural Break (Pre-War vs War)')
    plt.ylabel('Monthly Fatalities')
    plt.xlabel('Date')
    plt.legend()
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'F1_fatalities_structural_break.png'), dpi=300)
    plt.close()

    print("\n--- Generating F2: Event Composition (Stacked Area) ---")
    
    if 'month' not in df.columns:
        df['month'] = df['event_date'].dt.to_period('M').dt.to_timestamp()

    type_time = df.groupby(['month', 'event_type']).size().unstack(fill_value=0)
    type_time_pct = type_time.div(type_time.sum(axis=1), axis=0) * 100
    type_time_pct_smooth = type_time_pct.rolling(window=5, min_periods=1, center=True).mean()
    
    plt.figure(figsize=(12, 6))
    colors = sns.color_palette("tab10", n_colors=len(type_time_pct_smooth.columns))
    plt.stackplot(type_time_pct_smooth.index, type_time_pct_smooth.T, labels=type_time_pct_smooth.columns, colors=colors)
    
    plt.axvline(pd.Timestamp("2023-04-15"), color='black', linestyle='--', linewidth=1.5)
    plt.text(pd.Timestamp("2023-04-15"), 102, ' War Starts', ha='center', va='bottom')
    
    plt.title('F2: Shift in Event Composition')
    plt.ylabel('Percentage of Events')
    plt.xlabel('Date')
    plt.xlim(type_time_pct_smooth.index.min(), type_time_pct_smooth.index.max())
    plt.ylim(0, 100)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Event Type')
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'F2_event_composition_full.png'), dpi=300, bbox_inches='tight')
    plt.close()

    print("\n--- Generating F6: Choropleth + Hotspots ---")
    try:
        gdf_admin1 = gpd.read_file(ADMIN1_SHP)
        
        name_col = 'shapeName'
        if name_col not in gdf_admin1.columns:
            possible_cols = ['shapeName', 'ADM1_EN', 'admin1Name', 'Name', 'NAME_1', 'admin1']
            for col in possible_cols:
                if col in gdf_admin1.columns:
                    name_col = col
                    break
        
        print(f"Using Admin1 Name Column: {name_col}")
        
        corrections = {
            'Al Jazirah': 'Gezira',
            'Al Qadarif': 'Gedaref'
        }
        df['admin1_mapped'] = df['admin1'].replace(corrections)
        
        event_counts = df.groupby('admin1_mapped').size().rename('event_count')
        gdf_merged = gdf_admin1.merge(event_counts, left_on=name_col, right_index=True, how='left').fillna(0)
        
        hotspots = df[(df['geo_precision'] == 1)].sort_values('fatalities', ascending=False).head(50)
        
        gdf_web = gdf_merged.to_crs(epsg=3857)
        hotspots_gdf = gpd.GeoDataFrame(hotspots, geometry=gpd.points_from_xy(hotspots.longitude, hotspots.latitude), crs="EPSG:4326")
        hotspots_web = hotspots_gdf.to_crs(epsg=3857)
        
        plt.figure(figsize=(10, 10))
        ax = plt.gca()
        
        gdf_web.plot(column='event_count', ax=ax, cmap='OrRd', edgecolor='black', linewidth=0.5, alpha=0.7, legend=True,
                     legend_kwds={'label': "Total Events", 'shrink': 0.6})
        
        try:
            cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
        except Exception as e:
            print(f"Basemap error: {e}")
            
        sizes = np.sqrt(hotspots_web['fatalities']) * 2
        ax.scatter(hotspots_web.geometry.x, hotspots_web.geometry.y, s=sizes, color='black', alpha=0.8, label='Top Fatality Events', edgecolors='white', linewidth=0.5)
        
        ax.set_axis_off()
        plt.title('F6: Conflict Distribution & High-Fatality Hotspots')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'F6_choropleth_with_hotspots.png'), dpi=300)
        plt.close()
        
    except Exception as e:
        print(f"Skipping F6 Map: {e}")

    print("\n--- Generating F9: Source Coverage Shift ---")
    f9_ct = pd.crosstab(df['period_group'], df['source_scale'], normalize='index') * 100
    if 'before_war' in f9_ct.index and 'war_period' in f9_ct.index:
        f9_ct = f9_ct.reindex(['before_war', 'war_period'])
        
    top_scales = df['source_scale'].value_counts().head(5).index
    f9_ct = f9_ct[top_scales] 
    
    f9_ct.plot(kind='bar', figsize=(10, 6), width=0.8)
    plt.title('F9: Shift in Source Reporting Scale (Top 5)')
    plt.ylabel('% of Period Reports')
    plt.xlabel('Period')
    plt.xticks(rotation=0)
    plt.legend(title='Source Scale')
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'F9_source_coverage_shift.png'), dpi=300)
    plt.close()

    print("\n--- Generating AX_06: Actor Timelines ---")
    target_actors = ['SAF', 'RSF', 'Protesters (Sudan)']
    ax06_df = df[df['actor1_norm'].isin(target_actors)].copy()
    
    month_counts = ax06_df.groupby(['month', 'actor1_norm']).size().reset_index(name='count')
    
    plt.figure(figsize=(12, 6))
    for actor in target_actors:
        subset = month_counts[month_counts['actor1_norm'] == actor]
        if not subset.empty:
            full_idx = pd.period_range(subset['month'].min(), subset['month'].max(), freq='M').to_timestamp()
            subset_reindexed = subset.set_index('month')['count'].reindex(full_idx, fill_value=0).reset_index()
            subset_reindexed.columns = ['month', 'count']
            
            subset_reindexed['count_smooth'] = subset_reindexed['count'].rolling(window=2, min_periods=1).mean()
            plt.plot(subset_reindexed['month'], subset_reindexed['count_smooth'], label=actor, color=color_map.get(actor), linewidth=2.5)
            
    plt.axvline(pd.Timestamp("2023-04-15"), color='black', linestyle='--', linewidth=1.5)
    plt.text(pd.Timestamp("2023-04-15"), plt.ylim()[1]*0.95, ' War Starts', ha='left')
    
    plt.title('AX_06: Actor Activity Timelines ')
    plt.ylabel('Monthly Events')
    plt.xlabel('Date')
    plt.legend()
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'AX_06_actor_timelines.png'), dpi=300)
    plt.close()

    print("\n--- Generating AX_04: Behavioral DNA (Replacement) ---")
    ax04_df = df[df['actor1_norm'].isin(['SAF', 'RSF'])].copy()
    ax04_counts = ax04_df.groupby(['actor1_norm', 'event_type']).size().reset_index(name='count')
    
    ax04_pivot = ax04_counts.pivot(index='event_type', columns='actor1_norm', values='count').fillna(0)
    ax04_pivot['SAF'] = ax04_pivot['SAF'] / ax04_pivot['SAF'].sum() * 100
    ax04_pivot['RSF'] = (ax04_pivot['RSF'] / ax04_pivot['RSF'].sum() * 100) * -1
    
    ax04_pivot = ax04_pivot.sort_values('SAF')
    
    plt.figure(figsize=(10, 8))
    plt.barh(ax04_pivot.index, ax04_pivot['RSF'], color=color_map.get('RSF', 'goldenrod'), label='RSF')
    plt.barh(ax04_pivot.index, ax04_pivot['SAF'], color=color_map.get('SAF', 'forestgreen'), label='SAF')
    
    plt.axvline(0, color='black', linewidth=1)
    
    plt.xlabel('Activity Share (%)')
    plt.title('AX_04: Behavioral DNA (War-Fighting Signatures)')
    plt.legend()
    sns.despine(left=True, bottom=True)
    
    ticks = plt.xticks()[0]
    plt.xticks(ticks, [str(abs(int(t))) for t in ticks])
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'AX_04_actor_event_distribution.png'), dpi=300)
    plt.close()

    print("\n--- All Figures Generated Successfully (PNGs) ---")

if __name__ == "__main__":
    main()
