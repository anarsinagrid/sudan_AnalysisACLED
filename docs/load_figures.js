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

        const defaultConfig = {
            responsive: true,
            displayModeBar: false
        };

        const config = { ...defaultConfig, ...customConfig };

        if (fig.frames && fig.frames.length > 0) {
            await Plotly.newPlot(divId, fig.data, fig.layout, config);
            await Plotly.addFrames(divId, fig.frames);
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

    /* -------- Load Figures -------- */

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

    /* -------- Act Background Transitions -------- */

    const actSections = document.querySelectorAll('.act');
    const timelineDots = document.querySelectorAll('.timeline__dot');
    const rootStyles = getComputedStyle(document.documentElement);
    const baseBg = rootStyles.getPropertyValue('--bg').trim();

    const updateTimelinePositions = () => {
        const doc = document.documentElement;
        const maxScroll = Math.max(1, doc.scrollHeight - doc.clientHeight);
        const actStart = document.querySelector('#act-rupture');
        const actEnd = document.querySelector('#act-aftermath');
        const actStartTop = actStart ? actStart.getBoundingClientRect().top + window.scrollY : null;
        const actEndTop = actEnd ? actEnd.getBoundingClientRect().top + window.scrollY : null;
        const hasActRange = actStartTop !== null && actEndTop !== null && actEndTop > actStartTop;
        const actStartRatio = hasActRange ? Math.min(1, Math.max(0, actStartTop / maxScroll)) : 0;
        const actEndRatio = hasActRange ? Math.min(1, Math.max(0, actEndTop / maxScroll)) : 1;

        timelineDots.forEach(dot => {
            const targetSelector = dot.getAttribute('href');
            if (!targetSelector || !targetSelector.startsWith('#')) return;
            const target = document.querySelector(targetSelector);
            if (!target) return;

            const targetTop = target.getBoundingClientRect().top + window.scrollY;
            let pos = Math.min(1, Math.max(0, targetTop / maxScroll));

            if (dot.classList.contains('timeline__dot--sub') && hasActRange) {
                const pad = 0.01;
                const minPos = actStartRatio + pad;
                const maxPos = actEndRatio - pad;
                pos = Math.min(maxPos, Math.max(minPos, pos));
            }

            dot.style.setProperty('--pos', pos.toFixed(4));
        });
    };

    const setActiveDot = (act) => {
        timelineDots.forEach(dot => {
            if (!dot.dataset.act) return;
            dot.classList.toggle('is-active', dot.dataset.act === act);
        });
    };

    if (baseBg) {
        document.body.style.backgroundColor = baseBg;
        document.documentElement.style.setProperty('--act-bg', baseBg);
    }

    const actObserver = new IntersectionObserver(
        (entries) => {
            // Use a center "band" rather than intersection ratio of the full act.
            // Acts can be taller than the viewport, so relying on ratio thresholds can fail.
            const active = entries
                .filter(e => e.isIntersecting)
                .sort((a, b) => b.intersectionRect.height - a.intersectionRect.height)[0];

            if (!active) return;

            const act = active.target.dataset.act;
            const color = rootStyles.getPropertyValue(`--bg-${act}`).trim();

            if (color) {
                document.body.style.backgroundColor = color;
                document.documentElement.style.setProperty('--act-bg', color);
                setActiveDot(act);
            }
        },
        {
            threshold: 0,
            rootMargin: '-45% 0px -45% 0px'
        }
    );

    actSections.forEach(section => actObserver.observe(section));

    /* -------- Scroll Progress -------- */

    let progressRaf = 0;
    const updateScrollProgress = () => {
        const doc = document.documentElement;
        const maxScroll = Math.max(1, doc.scrollHeight - doc.clientHeight);
        const progress = Math.min(1, Math.max(0, doc.scrollTop / maxScroll));
        doc.style.setProperty('--scroll-progress', progress.toFixed(4));
        progressRaf = 0;
    };

    const requestProgressUpdate = () => {
        if (progressRaf) return;
        progressRaf = requestAnimationFrame(updateScrollProgress);
    };

    updateScrollProgress();
    updateTimelinePositions();
    window.addEventListener('scroll', requestProgressUpdate, { passive: true });
    window.addEventListener('resize', () => {
        requestProgressUpdate();
        updateTimelinePositions();
    });

    if ('ResizeObserver' in window) {
        const resizeObserver = new ResizeObserver(() => {
            updateTimelinePositions();
        });
        resizeObserver.observe(document.body);
    } else {
        window.addEventListener('load', updateTimelinePositions);
    }

    /* -------- Figure Scroll Emphasis -------- */

    const figures = document.querySelectorAll('.figure.full');

    const figObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-active');
                }
            });
        },
        { threshold: 0.4 }
    );

    figures.forEach(fig => figObserver.observe(fig));
});
