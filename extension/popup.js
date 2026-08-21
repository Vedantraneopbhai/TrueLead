const API_BASE_URL = "http://localhost:8000";

document.addEventListener('DOMContentLoaded', async () => {
    // Detect current tab platform
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || !tabs[0]) return;
        const currentTab = tabs[0];
        const statusBadge = document.getElementById('page-status');
        const extractBtn = document.getElementById('extract-btn');

        const url = currentTab.url || '';
        if (url.includes("internshala.com")) {
            statusBadge.textContent = "Internshala Active";
            statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
            statusBadge.style.color = "#34d399";
            extractBtn.style.display = 'block';
        } else if (url.includes("naukri.com")) {
            statusBadge.textContent = "Naukri Active";
            statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
            statusBadge.style.color = "#34d399";
            extractBtn.style.display = 'block';
        } else if (url.includes("linkedin.com")) {
            statusBadge.textContent = "LinkedIn Active";
            statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
            statusBadge.style.color = "#34d399";
            extractBtn.style.display = 'block';
        } else if (url.includes("indeed.com")) {
            statusBadge.textContent = "Indeed Active";
            statusBadge.style.background = "rgba(16, 185, 129, 0.15)";
            statusBadge.style.color = "#34d399";
            extractBtn.style.display = 'block';
        }
    });
});

// Extract from active page
document.getElementById('extract-btn').addEventListener('click', async () => {
    const btn = document.getElementById('extract-btn');
    btn.disabled = true;
    btn.textContent = 'Extracting...';

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                // Try to extract job posting text from the page
                const selectors = [
                    '.internship_details', '.detail_view', '.text-container', '.job-description',
                    '.job-desc', '.dang-inner-html', '.jd-desc',
                    '.jobs-description__content', '.jobs-box__html-content',
                    '#jobDescriptionText', '.jobsearch-jobDescriptionText'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el && el.innerText.trim().length > 30) return el.innerText.trim();
                }
                return document.body.innerText.substring(0, 5000);
            }
        });

        if (results && results[0] && results[0].result) {
            document.getElementById('pop-text').value = results[0].result.substring(0, 4000);
            btn.textContent = 'Extracted ✓';
            setTimeout(() => { btn.textContent = 'Extract from Page'; btn.disabled = false; }, 1500);
        }
    } catch (e) {
        btn.textContent = 'Extract Failed';
        setTimeout(() => { btn.textContent = 'Extract from Page'; btn.disabled = false; }, 1500);
    }
});

// Analyze button
document.getElementById('pop-btn').addEventListener('click', async () => {
    const text = document.getElementById('pop-text').value.trim();
    const btn = document.getElementById('pop-btn');
    const resDiv = document.getElementById('pop-result');
    const flagsDiv = document.getElementById('pop-flags');

    if (!text) {
        alert("Please paste job posting text to analyze.");
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    resDiv.style.display = 'none';

    try {
        const res = await fetch(`${API_BASE_URL}/score`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!res.ok) throw new Error(`Backend Error (${res.status})`);
        const data = await res.json();

        const scoreVal = document.getElementById('pop-score-val');
        const popTag = document.getElementById('pop-tag');
        const popConf = document.getElementById('pop-confidence');

        resDiv.style.display = 'block';
        scoreVal.textContent = data.score + "%";
        popConf.textContent = ` (${data.confidence || 'Evaluated'})`;

        if (data.score >= 70) {
            scoreVal.style.color = "#f87171";
            popTag.textContent = "HIGH RISK";
            popTag.className = "pop-tag pop-tag-high";
        } else if (data.score >= 30) {
            scoreVal.style.color = "#fbbf24";
            popTag.textContent = "SUSPICIOUS";
            popTag.className = "pop-tag pop-tag-med";
        } else {
            scoreVal.style.color = "#34d399";
            popTag.textContent = "LOW RISK";
            popTag.className = "pop-tag pop-tag-low";
        }

        // Flags
        const flags = data.flags || [];
        if (flags.length > 0) {
            flagsDiv.innerHTML = flags.slice(0, 4).map(f => `<div class="pop-flag-item">⚠️ ${f}</div>`).join('');
        } else {
            flagsDiv.innerHTML = '<div class="pop-flag-item">✅ No suspicious scam indicators found.</div>';
        }

        // Report section
        const reportDiv = document.getElementById('pop-report');
        const report = data.report;
        if (report) {
            reportDiv.style.display = 'block';
            document.getElementById('pop-verdict').textContent = report.verdict || '';
            const recsEl = document.getElementById('pop-recs');
            recsEl.innerHTML = '';
            (report.recommendations || []).slice(0, 3).forEach(rec => {
                const div = document.createElement('div');
                div.className = 'pop-rec-item';
                div.textContent = `→ ${rec}`;
                recsEl.appendChild(div);
            });
        } else {
            reportDiv.style.display = 'none';
        }

    } catch (e) {
        resDiv.style.display = 'block';
        document.getElementById('pop-score-val').textContent = "Err";
        document.getElementById('pop-score-val').style.color = "#94a3b8";
        document.getElementById('pop-tag').textContent = "OFFLINE";
        document.getElementById('pop-tag').className = "pop-tag";
        flagsDiv.innerHTML = '⚠️ Unable to reach TrueLead — check backend at http://localhost:8000';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Check Scam Risk';
    }
});
