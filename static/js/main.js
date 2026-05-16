/**
 * CardioSense v2 — Main JavaScript
 * Form handling, API calls, and UI interactions
 */

async function runPrediction() {
    const btn = document.getElementById('predict-btn');
    const originalText = btn.textContent;
    btn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
    btn.disabled = true;

    const fieldIds = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
        'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ];

    const payload = {
        patient_name: document.getElementById('patient_name').value,
        model_name: document.getElementById('model_name').value
    };

    // Validate and collect
    for (const id of fieldIds) {
        const el = document.getElementById(id);
        const val = el ? el.value : '';
        if (val === '' || val === null || val === undefined) {
            showToast(`Please fill in the "${el?.previousElementSibling?.textContent || id}" field`, 'warning');
            btn.textContent = originalText;
            btn.disabled = false;
            return;
        }
        payload[id] = parseFloat(val);
    }

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = `/result/${result.data.record_id}`;
        } else {
            showToast('Prediction failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Network error: ' + error.message, 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Toast notification
function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; bottom: 2rem; right: 2rem; z-index: 9999;
        padding: 0.85rem 1.5rem; border-radius: 10px; font-size: 0.875rem;
        font-weight: 500; font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); animation: slideUp 0.3s ease;
        max-width: 400px;
    `;
    if (type === 'error') {
        toast.style.background = '#fee2e2'; toast.style.color = '#991b1b';
    } else if (type === 'warning') {
        toast.style.background = '#fef3c7'; toast.style.color = '#92400e';
    } else if (type === 'success') {
        toast.style.background = '#dcfce7'; toast.style.color = '#166534';
    } else {
        toast.style.background = '#dbeafe'; toast.style.color = '#1e40af';
    }
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 3500);
    setTimeout(() => toast.remove(), 4000);
}

// Batch upload
async function handleBatchUpload(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const statusEl = document.getElementById('batch-status');
    const resultsEl = document.getElementById('batch-results');

    if (statusEl) {
        statusEl.innerHTML = '<span class="loading-spinner" style="border-color:rgba(30,64,175,0.2);border-top-color:var(--primary)"></span> Processing...';
        statusEl.style.display = 'block';
    }

    try {
        const response = await fetch('/api/batch-predict', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            if (statusEl) statusEl.style.display = 'none';
            renderBatchResults(data, resultsEl);
        } else {
            if (statusEl) statusEl.innerHTML = `<span style="color:var(--danger)">Error: ${data.error}</span>`;
        }
    } catch (err) {
        if (statusEl) statusEl.innerHTML = `<span style="color:var(--danger)">Upload failed: ${err.message}</span>`;
    }
}

function renderBatchResults(data, container) {
    if (!container) return;

    const high = data.results.filter(r => r.risk_level === 'High').length;
    const moderate = data.results.filter(r => r.risk_level === 'Moderate').length;
    const low = data.results.filter(r => r.risk_level === 'Low').length;

    let html = `
        <div class="fade-in">
            <h3 style="margin-bottom:1rem;font-size:1rem;font-weight:700;">Batch Results — ${data.count} patients</h3>
            <div class="batch-summary">
                <div class="batch-stat" style="border-color:#bbf7d0">
                    <div class="batch-stat-number" style="color:var(--success)">${low}</div>
                    <div class="batch-stat-label">Low Risk</div>
                </div>
                <div class="batch-stat" style="border-color:#fde68a">
                    <div class="batch-stat-number" style="color:var(--warning)">${moderate}</div>
                    <div class="batch-stat-label">Moderate Risk</div>
                </div>
                <div class="batch-stat" style="border-color:#fecaca">
                    <div class="batch-stat-number" style="color:var(--danger)">${high}</div>
                    <div class="batch-stat-label">High Risk</div>
                </div>
            </div>
            <div class="card" style="padding:0;overflow:hidden">
                <table class="data-table">
                    <thead><tr>
                        <th>#</th><th>Age</th><th>Probability</th><th>Risk Level</th>
                    </tr></thead>
                    <tbody>
    `;

    data.results.forEach((r, i) => {
        const badgeClass = r.risk_level === 'High' ? 'risk-high' : r.risk_level === 'Moderate' ? 'risk-moderate' : 'risk-low';
        html += `<tr>
            <td>${i + 1}</td>
            <td>${r.age || '-'}</td>
            <td>${r.probability}%</td>
            <td><span class="risk-badge ${badgeClass}">${r.risk_level}</span></td>
        </tr>`;
    });

    html += '</tbody></table></div></div>';
    container.innerHTML = html;
}
