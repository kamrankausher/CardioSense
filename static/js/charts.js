/**
 * CardioSense v2 — Chart.js Visualizations
 */

const CHART_COLORS = {
    primary: '#1e40af',
    primaryLight: '#93c5fd',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    muted: '#94a3b8',
    grid: '#f1f5f9'
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            labels: {
                font: { family: "'Inter', sans-serif", size: 12, weight: '500' },
                usePointStyle: true,
                padding: 16
            }
        }
    }
};

function createRiskDoughnut(canvasId, riskData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Moderate Risk', 'High Risk'],
            datasets: [{
                data: [riskData.Low || 0, riskData.Moderate || 0, riskData.High || 0],
                backgroundColor: [CHART_COLORS.success, CHART_COLORS.warning, CHART_COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            cutout: '65%',
            plugins: {
                ...CHART_DEFAULTS.plugins,
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.label}: ${ctx.raw} patients`
                    }
                }
            }
        }
    });
}

function createAgeScatter(canvasId, ageData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const datasets = {
        'Low': { data: [], color: CHART_COLORS.success },
        'Moderate': { data: [], color: CHART_COLORS.warning },
        'High': { data: [], color: CHART_COLORS.danger }
    };

    ageData.forEach(d => {
        if (datasets[d.risk]) {
            datasets[d.risk].data.push({ x: d.age, y: d.prob });
        }
    });

    return new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: Object.entries(datasets).map(([label, d]) => ({
                label: `${label} Risk`,
                data: d.data,
                backgroundColor: d.color + '99',
                borderColor: d.color,
                borderWidth: 1.5,
                pointRadius: 5,
                pointHoverRadius: 7
            }))
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                x: {
                    title: { display: true, text: 'Age', font: { family: "'Inter'", weight: '600' } },
                    grid: { color: CHART_COLORS.grid }
                },
                y: {
                    title: { display: true, text: 'Probability (%)', font: { family: "'Inter'", weight: '600' } },
                    grid: { color: CHART_COLORS.grid },
                    min: 0, max: 100
                }
            }
        }
    });
}

function createModelBar(canvasId, metricsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const models = Object.keys(metricsData);
    const labels = models.map(m => m.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Accuracy',
                    data: models.map(m => metricsData[m].accuracy),
                    backgroundColor: CHART_COLORS.primary + 'cc',
                    borderRadius: 4
                },
                {
                    label: 'Precision',
                    data: models.map(m => metricsData[m].precision),
                    backgroundColor: CHART_COLORS.success + 'cc',
                    borderRadius: 4
                },
                {
                    label: 'Recall',
                    data: models.map(m => metricsData[m].recall),
                    backgroundColor: CHART_COLORS.warning + 'cc',
                    borderRadius: 4
                }
            ]
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 60,
                    max: 100,
                    grid: { color: CHART_COLORS.grid }
                },
                x: { grid: { display: false } }
            },
            plugins: {
                ...CHART_DEFAULTS.plugins,
                tooltip: {
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}

function createModelUsagePie(canvasId, modelUsage) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = Object.keys(modelUsage).map(m =>
        m.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    );

    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: Object.values(modelUsage),
                backgroundColor: [CHART_COLORS.primary, CHART_COLORS.success, CHART_COLORS.warning],
                borderWidth: 0
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                tooltip: {
                    callbacks: { label: ctx => `${ctx.label}: ${ctx.raw} predictions` }
                }
            }
        }
    });
}
