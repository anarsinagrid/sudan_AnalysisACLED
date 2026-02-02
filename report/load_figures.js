/**
 * Plotly Figure Loader
 * Loads Plotly figures from JSON and renders them inline
 */

async function loadFigure(divId, jsonPath, customConfig = {}) {
    try {
        const res = await fetch(jsonPath);
        if (!res.ok) {
            throw new Error(`Failed to load ${jsonPath}: ${res.statusText}`);
        }
        const fig = await res.json();

        // Default config
        const defaultConfig = {
            responsive: true,
            displayModeBar: false
        };

        // Merge with custom config
        const config = { ...defaultConfig, ...customConfig };

        // Check if figure has animation frames
        if (fig.frames && fig.frames.length > 0) {
            // For animated figures, first create the plot, then add frames
            await Plotly.newPlot(divId, fig.data, fig.layout, config);
            await Plotly.addFrames(divId, fig.frames);
            console.log(`Loaded animated figure ${divId} with ${fig.frames.length} frames`);
        } else {
            Plotly.newPlot(divId, fig.data, fig.layout, config);
        }
    } catch (error) {
        console.error(`Error loading figure ${divId}:`, error);
        document.getElementById(divId).innerHTML =
            `<p style="color: red; padding: 20px;">Error loading figure: ${error.message}</p>`;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Load standard figures
    loadFigure('fig-f1-plot', 'interactive_figures/F1_fatalities_structural_break.json');
    loadFigure('fig-f2-plot', 'interactive_figures/F2_event_composition_full.json');
    loadFigure('fig-ax04-plot', 'interactive_figures/AX_04_actor_event_distribution.json');
    loadFigure('fig-ax06-plot', 'interactive_figures/AX_06_actor_timelines.json');
    loadFigure('fig-f9-plot', 'interactive_figures/F9_source_coverage_shift.json');

    loadFigure('fig-f6-plot', 'interactive_figures/F6_choropleth_with_hotspots.json', {
        scrollZoom: false
    });

    loadFigure('fig-f14-plot', 'interactive_figures/F14_event_timelapse_high_precision_decay.json', {
        scrollZoom: false
    });
});
