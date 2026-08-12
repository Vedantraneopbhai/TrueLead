# TrueLead / SachHai — Multi-Language Fake Job & Internship Scam Detector

**TrueLead (SachHai)** is an AI-powered multimodal system that detects fake job postings, internship scams, and fraudulent recruitment offers across India and globally.

---

## 🌟 Key Features

1. **Multi-Group ML Classifier (XGBoost)**:
   - Evaluates **22 structural, behavioral, consistency, and regional script features**.
   - Handles real/fake class imbalance (**14.98:1 ratio**) via weighted loss optimization.
   - Achieves **83.62% Recall** and **0.9850 ROC-AUC** under 5-Fold Stratified Cross-Validation.

2. **Explainable AI (SHAP & Category Flags)**:
   - Generates plain-English risk factors categorized into **Fee & Payment**, **Urgency**, **Contact Details**, **Domain Reputation**, and **Salary Mismatch**.
   - Exports SHAP summary feature importances.

3. **Domain & URL Reputation Checker**:
   - Queries domain WHOIS registration age (flags domains < 180 days old).
   - **Typosquatting Engine**: Identifies near-match domains (e.g. `internshaila-careers.com`) targeting top ~30 Indian job portals & recruiters (TCS, Infosys, Wipro, Internshala, Naukri, Amazon, etc.).

4. **Multi-Language & Regional Support**:
   - Detects English, Hindi (Devanagari script), and Hinglish (code-mixed Latin script).
   - Parallel Devanagari script regex flags for fee/urgency phrasing (`शुल्क`, `रजिस्ट्रेशन फीस`, `सुरक्षा राशि`).

5. **OCR Screenshot Analyzer**:
   - Image preprocessing using OpenCV (grayscale + Otsu thresholding) + `pytesseract` text extraction for WhatsApp/social media screenshots.

6. **Chrome Extension**:
   - Manifest V3 content script targeting **LinkedIn, Internshala, and Naukri** job detail pages with floating risk badges.

7. **Judge-Facing Web Interface**:
   - Single-Page Application with animated circular SVG risk meter (0-100%), tabbed inputs, confidence badges, and preset demo examples.

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run API Server & Web UI
```bash
python -m uvicorn api.main:app --port 8000
```
Open your browser at `http://localhost:8000/`.

---

## 📂 Repository Structure

```
├── api/
│   └── main.py              # FastAPI application server
├── src/
│   ├── clean.py             # Data preprocessing & text cleaning
│   ├── features.py          # Structural, behavioral, consistency & domain feature extraction
│   ├── domain_check.py      # WHOIS age & typosquatting checker
│   ├── lang_detector.py     # Language & Devanagari script detector
│   ├── ocr_processor.py     # OpenCV + Pytesseract image OCR processor
│   ├── explain.py           # Risk scoring, SHAP explainability & flag categorization
│   ├── train_baseline.py    # Stratified 5-Fold CV XGBoost training
│   ├── train_transformer.py # Multilingual transformer fine-tuning
│   └── evaluate.py          # Model comparison & SHAP summary plot generation
├── frontend/
│   └── index.html           # Pitch-ready Single Page App UI
├── extension/
│   ├── manifest.json        # Chrome Manifest V3 configuration
│   ├── content.js           # DOM text scraper & floating overlay badge
│   ├── popup.html           # Fallback popup scanner interface
│   └── styles.css           # Glassmorphic badge styling
├── requirements.txt         # Python dependencies
└── .gitignore               # Excludes large CSV datasets & local checkpoints
```

---

## 🔒 Privacy & Safety Notice
No private credentials, API keys, or raw user data are stored or exposed.
