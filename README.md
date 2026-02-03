# What Changed in Sudan After April 2023?
### *A Visual Analysis of the Conflict's Structural Transformation*

This project analyzes the ACLED (Armed Conflict Location & Event Data) dataset to visualize how the conflict in Sudan fundamentally changed after the outbreak of war on April 15, 2023. It produces a data-driven narrative that moves beyond simple event counts to show shifts in lethality, actor behavior, and the collapse of civic space.

## 📂 Project Structure

The project follows a linear data pipeline from raw ingestion to final web report.

```
acledAnalysis/
├── data/
│   ├── raw/                  # Original CSV exports from ACLED
│   ├── cleaned_events.csv    # The master dataset used for all analysis (Generated)
│   └── sudan_admin1.geojson  # Geographic boundaries for maps
├── docs/                     # The final HTML report
│   ├── index.html            # Main narrative interface
│   ├── story.css             # Custom styling for the report
│   └── interactive_figures/  # JSON files for Plotly graphs (Generated)
├── final_figures/            # Static PNG versions of the figures (Generated)
├── data_cleaning.py          # Script: Standardizes and merges raw data
├── generate_final_figures.py # Script: Generates STATIC images (PNG)
└── generate_interactive_figures.py # Script: Generates INTERACTIVE graphs (JSON)
```

## 🚀 Setup & Installation

1. **Clone the repository** (or download the files).
2. **Install dependencies**. The project uses standard Python data science libraries.

```bash
pip install -r requirements.txt
```

*Key dependencies: `pandas`, `geopandas`, `plotly`, `matplotlib`, `seaborn`, `contextily`*

## 📊 Data Pipeline & Reproduction

To reproduce the analysis and report results, follow these steps in order:

### 1. Data Cleaning
Merges the pre-war and war-period datasets, standardizes column names, and adds necessary flags (e.g., `war_period` vs `pre_war`).

```bash
python data_cleaning.py
```
*Input: `data/raw/*.csv`*
*Output: `data/cleaned_events.csv`*

### 2. Generate Static Figures (Optional)
Creates high-resolution PNGs for use in slide decks or static documents.

```bash
python generate_final_figures.py
```
*Output: `final_figures/*.png`*

### 3. Generate Interactive Figures (Required for Web Report)
Creates the Plotly JSON files that power the `index.html` narrative. This step is **crucial** for the web interface to work.

```bash
python generate_interactive_figures.py
```
*Output: `docs/interactive_figures/*.json`*

### 4. View the Report
Open `docs/index.html` in your web browser. The report dynamically loads the generated JSON figures to tell the story of the conflict.

---

## 🛠 Analysis Decisions

- **Structural Break**: We use April 15, 2023, as the definitive split point to compare "Pre-War" (Oct 2021 - Apr 2023) vs "War Period".
- **Actor Normalization**: Various ACLED actor names (e.g., "Military Forces of Sudan (2019-)") are standardized to **SAF** (Sudanese Armed Forces) and **RSF** (Rapid Support Forces) for clarity.
- **Visual Style**: Figures use a custom color palette (SAF: Green, RSF: Gold/Orange) and minimalist styling to focus on the human impact of the data.

## 🔗 Data Sources
- **ACLED**: [Armed Conflict Location & Event Data Project](https://acleddata.com/)
- **Administrative Boundaries**: Sudan Admin Level 1 GeoJSON.
