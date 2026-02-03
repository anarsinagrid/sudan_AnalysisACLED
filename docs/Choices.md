# Storytelling & Design Decisions

This document explains the "why" behind the narrative structure, visual design, and data handling choices in the Sudan Conflict Analysis report. It is intended for designers, developers, and analysts who want to understand the editorial direction of the project.

## 1. Narrative Arc: The 5-Act Structure

Instead of a standard dashboard that presents all data at once, we chose a **linear, scrollytelling narrative**. This forces the reader to experience the conflict's evolution chronologically and thematically.

- **ACT I: Hope (Pre-War Context)**
  - *Goal*: Establish the baseline of civic engagement.
  - *Data*: Focus on protest events.
  - *Key Takeaway*: Sudan was not a vacuum; there was an active, organized civil society.

- **ACT II: Tension (The Build-up)**
  - *Goal*: Show the encroachment of violence upon civic space.
  - *Data*: Rise in armed actor presence vs. civilian demonstrations.
  - *Key Takeaway*: The war didn't just "happen"; it was a visible accumulation of power.

- **ACT III: Rupture (April 15, 2023)**
  - *Goal*: accurate visualization of the structural break.
  - *Data*: Fatalities spike (F1) and event composition shift (F2).
  - *Key Takeaway*: April 15 was a system shock that fundamentally altered the country's daily reality.

- **Event Composition (The "New Normal")**
  - *Goal*: Explain *how* the violence changed.
  - *Data*: Shift from "Protests" to "Battles" and "Violence Against Civilians".
  - *Key Takeaway*: Political expression was violently replaced by military logic.

- **ACT V: Aftermath**
  - *Goal*: Leave the reader with the lingering reality of the conflict.
  - *Data*: Persistence of violence despite "quiet" periods (stalemates).

## 2. Design Philosophy

### Minimalist Aesthetic
We stripped away standard chart clutter (grids, heavy borders, default titles) to focus on the data lines themselves. The heavy use of whitespace mirrors the "silence" often associated with unreported conflicts.

### Color Semantics
We eschewed standard categorical colors for a strictly semantic palette:
- **Forest Green (`#228B22`)**: **SAF** (Sudanese Armed Forces) - Represents the "official" military, grounded but rigid.
- **Goldenrod (`#DAA520`)**: **RSF** (Rapid Support Forces) - Represents the paramilitary nature, distinct from the state but highly visible.
- **Steel Blue (`#4682B4`)**: **Protesters** - Represents civic movement, distinct from the armed actors.
- **Grey**: Pre-war or neutral context.
- **Firebrick (`#B22222`)**: War-period intensity.

### Interactive "Scrollytelling"
The report uses `IntersectionOrder` in JavaScript to trigger animations only when the reader arrives at a specific section. This pacing ensures the reader processes one insight before moving to the next.

## 3. Data Decisions

### Structural Break Point: April 15, 2023
While tension existed before, statistical tests (Chow Test) confirmed Apr 15 as the structural break. We treat this date as a "hard border" in all visualizations.

### Actor Normalization
ACLED data contains many variations of actor names. We aggregated them into three primary buckets for clarity:
1. **SAF**: Includes "Military Forces of Sudan (2019-)", "Government of Sudan", etc.
2. **RSF**: Includes "Rapid Support Forces", "Military Forces of Sudan (2019-2023) Rapid Support Forces".
3. **Protesters**: Includes all civilian demonstration groups.

### Handling "Quiet" Periods
The analysis intentionally highlights the "stalemate" periods (e.g., early 2024). We annotated these in Figure 1 to prevent the misinterpretation that "fewer reported battles = peace." Instead, we labeled it "Shift to Silent War" to reflect the transition to siege warfare and starvation, which show up less in event data but are equally lethal.

## 4. The Editorial Layer: What We Explored But Chose Not to Show

The final report represents a curated selection from a much broader exploratory analysis. This section documents the visualizations and analyses that were tested but ultimately excluded—not due to lack of rigor, but because they either didn't serve the narrative or risked overwhelming the reader.

### Sexual Violence Analysis
**What we explored**: Event-level analysis of sexual violence incidents, including temporal patterns and geographic clustering.

**Why we excluded it**: 
- **Under-reporting bias**: Sexual violence is notoriously under-documented in conflict zones. Showing raw counts would misrepresent the true scale.
- **Ethical concerns**: Reducing sexual violence to "just another data point" without proper context felt reductive and potentially harmful.
- **Narrative fit**: The story focuses on structural shifts in violence, not specific atrocity types that require deeper qualitative context.

### Reporting Bias & Source Density
**What we explored**: Analysis of how media coverage shifted during the war, including source density maps and temporal reporting gaps.

**Why we simplified it**: 
- **Too meta**: A full reporting bias correction model would require explaining the methodology before the reader even sees the main story.
- **Audience accessibility**: The general audience doesn't need to know about ACLED's data collection process to understand the conflict's impact.
- **Compromise**: We kept a simplified version (Figure 9: Source Coverage Shift) that shows the change without diving into correction models.

### Complex Spatial Models
**What we explored**: DBSCAN clustering to identify "hotspot zones" and spatial autocorrelation tests (Moran's I) to detect conflict diffusion patterns.

**Why we used choropleths instead**: 
- **Interpretability**: Density-based clusters are hard to explain to non-technical audiences ("What does epsilon mean?").
- **Visual clarity**: Standard admin-level choropleths are immediately recognizable and don't require statistical training to interpret.
- **Actionability**: Policymakers and journalists are more familiar with state-level aggregations than algorithmically-defined zones.

### Actor Network Graphs
**What we explored**: Network visualizations showing interactions between 50+ armed groups, militias, and state actors.

**Why we focused on SAF vs RSF instead**: 
- **Visual overload**: Network graphs with dozens of nodes become unreadable "hairballs."
- **Narrative clarity**: The conflict is fundamentally a two-sided war. Showing every minor militia would obscure this core dynamic.
- **Behavioral DNA approach**: The diverging bar chart (AX_04) more clearly shows *how* SAF and RSF differ in their tactics than a network graph ever could.

### Temporal Aggregation Experiments
**What we explored**: Weekly, bi-weekly, and quarterly aggregations to test sensitivity to time windows.

**Why we standardized on monthly**: 
- **Noise reduction**: Weekly data was too volatile; quarterly data smoothed out important mid-term shifts.
- **Consistency**: Monthly aggregation is standard in conflict analysis literature, making our work comparable to other studies.
- **Visual rhythm**: Monthly bins create a readable timeline without excessive compression or expansion.

---

**Key Takeaway**: The final visualizations were not the first or only options explored. They were chosen because they best balanced **analytical rigor**, **narrative clarity**, and **audience accessibility**. Every exclusion was a deliberate editorial choice, not an oversight.
