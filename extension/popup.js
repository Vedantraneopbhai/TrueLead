document.getElementById('pop-btn').addEventListener('click', async () => {
    const text = document.getElementById('pop-text').value.trim();
    if (!text) return;

    const btn = document.getElementById('pop-btn');
    btn.disabled = true;
    btn.textContent = 'Scanning...';

    try {
        const res = await fetch("http://localhost:8000/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!res.ok) throw new Error("API Offline");
        const data = await res.json();

        const resDiv = document.getElementById('pop-result');
        const scoreVal = document.getElementById('pop-score-val');
        const flagsDiv = document.getElementById('pop-flags');

        resDiv.style.display = 'block';
        scoreVal.textContent = data.score + "%";
        scoreVal.style.color = data.score > 60 ? "#ef4444" : (data.score > 30 ? "#f59e0b" : "#10b981");

        flagsDiv.innerHTML = (data.flags || []).map(f => `<div>• ${f}</div>`).join('');
    } catch (e) {
        alert("Make sure TrueLead API is running at http://localhost:8000");
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan Job Offer';
    }
});
