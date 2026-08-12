# TrueLead — Fake Job & Internship Scam Detector MVP

TrueLead is an AI-powered fake job and internship scam detector designed to evaluate job posting descriptions, recruitment emails, and messaging offers for fraudulent indicators and scam patterns.

## Tech Stack
- **Backend Framework**: Python 3.11, FastAPI, Uvicorn
- **Machine Learning & NLP**: Scikit-Learn, XGBoost, HuggingFace Transformers (DistilBERT)
- **Explainability**: SHAP (SHapley Additive exPlanations) + Rule-based heuristic red flags
- **Frontend**: Plain HTML5, Vanilla JavaScript, Modern Glassmorphism CSS

## Project Directory Structure
```
sachhai/
├── data/                    # Raw datasets & processed dataset CSVs
│   ├── fake_job_postings.csv (EMSCAD main dataset)
│   ├── indian_job_fraud.csv  (Synthetic Indian context dataset)
│   ├── cleaned.csv
│   └── featured.csv
├── src/
│   ├── clean.py             # Schema mapping, text cleaning & merging
│   ├── features.py          # Rule-based red flag feature extraction
│   ├── train_baseline.py    # TF-IDF + XGBoost model training & joblib export
│   ├── train_transformer.py # DistilBERT sequence classification fine-tuning
│   └── explain.py           # SHAP explainability engine & risk flag generator
├── api/
│   └── main.py              # FastAPI app with POST /score & static web server
├── frontend/
│   └── index.html           # Interactive risk meter & web user interface
├── models/                  # Saved .joblib and transformer model weights
├── requirements.txt         # Project dependencies
└── README.md
```

## Quick Start Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Data Pipeline & Train Baseline Model
Execute the data processing and model training pipeline sequentially:

```bash
# Step 1: Clean and merge datasets
python -m sachhai.src.clean

# Step 2: Extract red-flag heuristic features
python -m sachhai.src.features

# Step 3: Train XGBoost baseline model
python -m sachhai.src.train_baseline
```

*(Optional Step 4: Fine-tune DistilBERT Transformer)*
```bash
python -m sachhai.src.train_transformer
```

### 3. Launch FastAPI Server & Web App
```bash
python -m uvicorn sachhai.api.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000` to interact with the scam detection UI!

## Scam Red-Flag Heuristics Included
- **Fee Mentioned**: Detects upfront registration fees, security deposits, and processing payments.
- **Artificial Urgency**: Highlights phrases such as "limited slots", "apply within 24 hours", and "immediate spot offer".
- **Personal Webmail Contact**: Identifies recruiters using `@gmail.com`, `@yahoo.com`, or `@hotmail.com` instead of enterprise domains.
- **Salary Mismatch**: Detects unrealistic high daily or monthly payouts promised for entry-level / intern roles.
