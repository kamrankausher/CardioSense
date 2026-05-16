/**
 * CardioSense v2 — Risk Meter & SHAP Bar Animations
 */

function animateRiskMeter(probability) {
    const needle = document.getElementById('risk-needle');
    if (!needle) return;
    setTimeout(() => {
        needle.style.left = `${probability}%`;
    }, 300);
}

function renderShapBars(shapData, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !shapData || shapData.length === 0) return;

    const maxAbsShap = Math.max(...shapData.map(s => Math.abs(s.shap_value)), 0.001);

    let html = '';
    shapData.forEach((item, idx) => {
        const isPositive = item.shap_value > 0;
        const barWidth = Math.min((Math.abs(item.shap_value) / maxAbsShap) * 100, 100);
        const barClass = isPositive ? 'shap-bar-positive' : 'shap-bar-negative';
        const valClass = isPositive ? 'shap-positive-val' : 'shap-negative-val';
        const sign = isPositive ? '+' : '';

        html += `
        <div class="shap-feature-row fade-in" style="animation-delay: ${idx * 0.08}s">
            <div class="shap-feature-label" title="${item.feature}">${item.feature}</div>
            <div class="shap-bar-track">
                <div class="shap-bar-fill ${barClass}" style="width: 0%" data-width="${barWidth}"></div>
            </div>
            <div class="shap-bar-value ${valClass}">${sign}${item.shap_value.toFixed(3)}</div>
        </div>`;
    });

    container.innerHTML = html;

    // Animate bars
    setTimeout(() => {
        container.querySelectorAll('.shap-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width + '%';
        });
    }, 100);
}

// Animate numbers counting up
function animateCounter(elementId, targetValue, duration = 1000) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const currentVal = start + (targetValue - start) * eased;

        if (targetValue % 1 !== 0) {
            el.textContent = currentVal.toFixed(1) + '%';
        } else {
            el.textContent = Math.round(currentVal);
        }

        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// Initialize result page animations
function initResultAnimations(probability, shapData) {
    animateRiskMeter(probability);
    renderShapBars(shapData, 'shap-container');
    animateCounter('probability-value', probability, 1200);
}
