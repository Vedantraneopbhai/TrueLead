(function() {
    console.log("TrueLead AI Scam Detector extension loaded.");

    function extractPostingText() {
        let text = "";
        let company = "";
        let title = "";

        const host = window.location.hostname;

        if (host.includes("linkedin.com")) {
            // LinkedIn Selectors
            const titleEl = document.querySelector('.job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1');
            const compEl = document.querySelector('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name');
            const descEl = document.querySelector('#job-details, .jobs-description__content, .jobs-box__html-content');

            title = titleEl ? titleEl.innerText.strip() : "";
            company = compEl ? compEl.innerText.strip() : "";
            text = descEl ? descEl.innerText : document.body.innerText;

        } else if (host.includes("internshala.com")) {
            // Internshala Selectors
            const titleEl = document.querySelector('.heading_4_5, .profile_on_detail_page');
            const compEl = document.querySelector('.company_name');
            const descEl = document.querySelector('.internship_details, .detail_view');

            title = titleEl ? titleEl.innerText : "";
            company = compEl ? compEl.innerText : "";
            text = descEl ? descEl.innerText : document.body.innerText;

        } else if (host.includes("naukri.com")) {
            // Naukri Selectors
            const titleEl = document.querySelector('.jd-header-title, h1');
            const compEl = document.querySelector('.jd-header-comp-name, .comp-name');
            const descEl = document.querySelector('.job-desc, .dang-inner-html');

            title = titleEl ? titleEl.innerText : "";
            company = compEl ? compEl.innerText : "";
            text = descEl ? descEl.innerText : document.body.innerText;
        } else {
            text = document.body.innerText;
        }

        return { text: text.trim(), company: company.trim(), title: title.trim() };
    }

    async function analyzeCurrentPage() {
        const data = extractPostingText();
        if (!data.text || data.text.length < 30) return;

        try {
            const res = await fetch("http://localhost:8000/score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: data.text.substring(0, 4000),
                    company: data.company,
                    title: data.title
                })
            });

            if (!res.ok) return;
            const result = await res.json();
            injectScamBadge(result);
        } catch (e) {
            console.error("TrueLead API Error:", e);
        }
    }

    function injectScamBadge(result) {
        let badge = document.getElementById("truelead-scam-badge");
        if (!badge) {
            badge = document.createElement("div");
            badge.id = "truelead-scam-badge";
            document.body.appendChild(badge);
        }

        const score = result.score;
        let tagClass = "truelead-tag-low";
        let tagText = "LOW RISK";
        let color = "#10b981";

        if (score >= 70) {
            tagClass = "truelead-tag-high";
            tagText = "HIGH RISK SCAM";
            color = "#ef4444";
        } else if (score >= 30) {
            tagClass = "truelead-tag-med";
            tagText = "SUSPICIOUS";
            color = "#f59e0b";
        }

        const topFlags = (result.flags || []).slice(0, 3);
        const flagsHtml = topFlags.map(f => `<div class="truelead-flag-item">⚠️ ${f}</div>`).join("");

        badge.innerHTML = `
            <div class="truelead-header">
                <span>🛡️ TrueLead AI</span>
                <span class="truelead-score-tag ${tagClass}">${tagText}</span>
            </div>
            <div class="truelead-score-row">
                <span class="truelead-score-val" style="color: ${color}">${score}%</span>
                <span style="font-size: 11px; color: #94a3b8;">Scam Probability (${result.confidence})</span>
            </div>
            <div class="truelead-flags">
                ${flagsHtml}
            </div>
        `;
    }

    // Delay scan for dynamic page hydration
    setTimeout(analyzeCurrentPage, 1500);
})();
