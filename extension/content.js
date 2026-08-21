(function() {
    console.log("TrueLead AI Scam Detector v2.0 initialized.");

    const API_BASE_URL = "http://localhost:8000";
    const MAX_RETRIES = 3;
    const RETRY_DELAY_MS = 2000;

    // Platform-specific selectors for extracting job posting content
    const PLATFORM_SELECTORS = {
        internshala: {
            detect: () => location.hostname.includes('internshala.com'),
            title: '.heading_4_5, .profile, .profile_on_detail_page, h1',
            company: '.company_name, .link_display_like_text',
            description: '.internship_details, .detail_view, .text-container, .job-description',
        },
        naukri: {
            detect: () => location.hostname.includes('naukri.com'),
            title: '.jd-header-title, .job-title, h1.jd-header-title',
            company: '.jd-header-comp-name, .company-name, .jd-comp-name a',
            description: '.job-desc, .dang-inner-html, .jd-desc, .job-description-container',
        },
        linkedin: {
            detect: () => location.hostname.includes('linkedin.com'),
            title: '.job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1',
            company: '.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name',
            description: '.jobs-description__content, .jobs-box__html-content, .job-details-jobs-unified-description__content',
        },
        indeed: {
            detect: () => location.hostname.includes('indeed.com'),
            title: '.jobsearch-JobInfoHeader-title, h1[data-testid="jobsearch-JobInfoHeader-title"]',
            company: '.jobsearch-InlineCompanyRating-companyHeader, [data-testid="inlineHeader-companyName"]',
            description: '#jobDescriptionText, .jobsearch-jobDescriptionText',
        }
    };

    function detectPlatform() {
        for (const [name, config] of Object.entries(PLATFORM_SELECTORS)) {
            if (config.detect()) return { name, ...config };
        }
        return null;
    }

    function extractPostingText() {
        const platform = detectPlatform();
        let text = "", company = "", title = "";

        if (platform) {
            const titleEl = document.querySelector(platform.title);
            const compEl = document.querySelector(platform.company);
            const descEl = document.querySelector(platform.description);

            title = titleEl ? titleEl.innerText.trim() : "";
            company = compEl ? compEl.innerText.trim() : "";
            text = descEl ? descEl.innerText.trim() : "";
        }

        // Fallback: use full body text if no platform-specific content found
        if (!text || text.length < 30) {
            text = document.body.innerText.trim();
        }

        return { text, company, title };
    }

    async function analyzeWithRetry(data, retries = 0) {
        try {
            const res = await fetch(`${API_BASE_URL}/score`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: data.text.substring(0, 5000),
                    company: data.company,
                    title: data.title
                })
            });

            if (!res.ok) {
                throw new Error(`Backend error (${res.status})`);
            }
            return await res.json();
        } catch (e) {
            if (retries < MAX_RETRIES) {
                console.log(`TrueLead: Retry ${retries + 1}/${MAX_RETRIES} in ${RETRY_DELAY_MS}ms...`);
                await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
                return analyzeWithRetry(data, retries + 1);
            }
            throw e;
        }
    }

    async function analyzeCurrentPage() {
        const data = extractPostingText();
        
        if (!data.text || data.text.length < 30) {
            console.log("TrueLead: Insufficient posting text detected on page.");
            return;
        }

        try {
            const result = await analyzeWithRetry(data);
            injectScamBadge(result, null);
        } catch (e) {
            console.error("TrueLead API Error:", e);
            injectScamBadge(null, "Unable to reach TrueLead backend");
        }
    }

    function injectScamBadge(result, errorMsg) {
        let badge = document.getElementById("truelead-scam-badge");
        if (!badge) {
            badge = document.createElement("div");
            badge.id = "truelead-scam-badge";
            document.body.appendChild(badge);
        }

        if (errorMsg) {
            badge.innerHTML = `
                <div class="truelead-header">
                    <div class="truelead-header-left">🛡️ TrueLead AI</div>
                    <span class="truelead-dismiss" title="Dismiss">✕</span>
                </div>
                <div class="truelead-score-row">
                    <span class="truelead-score-val" style="color: #cbd5e1; font-size: 18px;">Offline</span>
                    <span class="truelead-score-tag truelead-tag-err">ERROR</span>
                </div>
                <div class="truelead-flags" style="color: #f87171;">
                    ⚠️ ${errorMsg}
                </div>
            `;
            badge.querySelector(".truelead-dismiss").addEventListener("click", () => badge.remove());
            return;
        }

        const score = result.score;
        let tagClass = "truelead-tag-low";
        let tagText = "LOW RISK";
        let color = "#34d399";

        if (score >= 70) {
            tagClass = "truelead-tag-high";
            tagText = "HIGH RISK SCAM";
            color = "#f87171";
        } else if (score >= 30) {
            tagClass = "truelead-tag-med";
            tagText = "SUSPICIOUS";
            color = "#fbbf24";
        }

        const topFlags = (result.flags || []).slice(0, 3);
        const flagsHtml = topFlags.length > 0
            ? topFlags.map(f => `<div class="truelead-flag-item"><span>⚠️</span> <span>${f}</span></div>`).join("")
            : `<div class="truelead-flag-item"><span>✅</span> <span>No immediate red flags detected.</span></div>`;

        // Report verdict and recommendations
        const report = result.report || {};
        const verdict = report.verdict || '';
        const recs = (report.recommendations || []).slice(0, 2);
        const recsHtml = recs.map(r => `<div class="truelead-rec-item">→ ${r}</div>`).join('');

        const hasDetails = (result.flags || []).length > 3 || verdict || recs.length > 0;

        badge.innerHTML = `
            <div class="truelead-header">
                <div class="truelead-header-left">🛡️ TrueLead AI</div>
                <span class="truelead-dismiss" title="Dismiss">✕</span>
            </div>
            <div class="truelead-score-row">
                <div>
                    <span class="truelead-score-val" style="color: ${color}">${score}%</span>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Risk Level (${result.confidence})</div>
                </div>
                <span class="truelead-score-tag ${tagClass}">${tagText}</span>
            </div>
            <div class="truelead-flags">
                ${flagsHtml}
            </div>
            ${hasDetails ? `
                <button class="truelead-toggle-btn" id="truelead-toggle">View full report ▾</button>
                <div class="truelead-details" id="truelead-details-panel">
                    ${verdict ? `<div class="truelead-verdict">${verdict}</div>` : ''}
                    ${recsHtml ? `<div class="truelead-recs-section">${recsHtml}</div>` : ''}
                    ${(result.flags || []).slice(3).map(f => `<div style="margin-bottom:4px;">• ${f}</div>`).join('')}
                    ${result.detected_language ? `<div style="margin-top:4px; font-size: 10px;">Lang: ${result.detected_language}</div>` : ''}
                </div>
            ` : ''}
        `;

        badge.querySelector(".truelead-dismiss").addEventListener("click", () => badge.remove());

        const toggleBtn = badge.querySelector("#truelead-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                const panel = badge.querySelector("#truelead-details-panel");
                if (panel.classList.contains("expanded")) {
                    panel.classList.remove("expanded");
                    toggleBtn.textContent = "View full report ▾";
                } else {
                    panel.classList.add("expanded");
                    toggleBtn.textContent = "Hide details ▴";
                }
            });
        }
    }

    // Delay scan for dynamic SPA hydration — longer for LinkedIn/Naukri
    const platform = detectPlatform();
    const delay = (platform && (platform.name === 'linkedin' || platform.name === 'naukri')) ? 2500 : 1200;
    setTimeout(analyzeCurrentPage, delay);

    // Also re-scan on URL changes (SPA navigation)
    let lastUrl = location.href;
    const observer = new MutationObserver(() => {
        if (location.href !== lastUrl) {
            lastUrl = location.href;
            // Remove old badge
            const oldBadge = document.getElementById("truelead-scam-badge");
            if (oldBadge) oldBadge.remove();
            setTimeout(analyzeCurrentPage, delay);
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
