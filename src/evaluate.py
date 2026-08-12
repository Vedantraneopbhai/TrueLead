import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import hstack
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
import shap

try:
    from src.features import ENGINEERED_FEATURE_NAMES
except ImportError:
    from features import ENGINEERED_FEATURE_NAMES

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    featured_path = os.path.join(data_dir, "featured.csv")
    if not os.path.exists(featured_path):
        raise FileNotFoundError(f"Featured dataset not found at {featured_path}. Run features.py first.")
        
    print(f"Loading dataset from {featured_path}...")
    df = pd.read_csv(featured_path)
    df['full_text'] = df['full_text'].fillna('')
    if 'raw_text' in df.columns:
        df['raw_text'] = df['raw_text'].fillna(df['full_text'])
    else:
        df['raw_text'] = df['full_text']
    
    y = df['fraudulent'].values
    n_genuine = np.sum(y == 0)
    n_fraud = np.sum(y == 1)
    imbalance_ratio = n_genuine / max(1, n_fraud)
    
    print("\n========================================================")
    print(" 1. COMPARING MODELS (5-FOLD STRATIFIED CROSS-VALIDATION)")
    print("========================================================")
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    metrics_text_only = []
    metrics_full_model = []
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(df, y), 1):
        train_df, test_df = df.iloc[train_idx], df.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # TF-IDF
        vec = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        X_tr_tfidf = vec.fit_transform(train_df['full_text'])
        X_te_tfidf = vec.transform(test_df['full_text'])
        
        # Model A: Text-Only
        model_text = XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.08,
            scale_pos_weight=imbalance_ratio, random_state=42, eval_metric='logloss'
        )
        model_text.fit(X_tr_tfidf, y_train)
        pred_t = model_text.predict(X_te_tfidf)
        prob_t = model_text.predict_proba(X_te_tfidf)[:, 1]
        
        metrics_text_only.append({
            'precision': precision_score(y_test, pred_t, zero_division=0),
            'recall': recall_score(y_test, pred_t, zero_division=0),
            'f1': f1_score(y_test, pred_t, zero_division=0),
            'auc': roc_auc_score(y_test, prob_t)
        })
        
        # Model B: Full Feature Model (Text + Structural + Behavioral + Consistency + Domain)
        X_tr_eng = train_df[ENGINEERED_FEATURE_NAMES].values
        X_te_eng = test_df[ENGINEERED_FEATURE_NAMES].values
        
        X_tr_full = hstack([X_tr_tfidf, X_tr_eng]).tocsr()
        X_te_full = hstack([X_te_tfidf, X_te_eng]).tocsr()
        
        model_full = XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.08,
            scale_pos_weight=imbalance_ratio, random_state=42, eval_metric='logloss'
        )
        model_full.fit(X_tr_full, y_train)
        pred_f = model_full.predict(X_te_full)
        prob_f = model_full.predict_proba(X_te_full)[:, 1]
        
        metrics_full_model.append({
            'precision': precision_score(y_test, pred_f, zero_division=0),
            'recall': recall_score(y_test, pred_f, zero_division=0),
            'f1': f1_score(y_test, pred_f, zero_division=0),
            'auc': roc_auc_score(y_test, prob_f)
        })

    def print_summary(name, metrics_list):
        p = np.mean([m['precision'] for m in metrics_list])
        r = np.mean([m['recall'] for m in metrics_list])
        f1 = np.mean([m['f1'] for m in metrics_list])
        auc = np.mean([m['auc'] for m in metrics_list])
        print(f"\n[{name}] Results over 5 Folds:")
        print(f"  Precision : {p:.4f}")
        print(f"  Recall    : {r:.4f}")
        print(f"  F1-Score  : {f1:.4f}")
        print(f"  ROC-AUC   : {auc:.4f}")
        return p, r, f1, auc

    print_summary("Model (A) Text-Only (TF-IDF)", metrics_text_only)
    p_f, r_f, f1_f, auc_f = print_summary("Model (B) Full Feature Model (Text + Structural + Behavioral + Consistency + Domain)", metrics_full_model)

    print("\n========================================================")
    print(" 2. SHAP & XGBOOST FEATURE IMPORTANCE ANALYSIS")
    print("========================================================")
    
    # Train full model on dataset sample for SHAP plot
    sample_df = df.sample(n=min(3000, len(df)), random_state=42).reset_index(drop=True)
    vec_full = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X_tfidf_sample = vec_full.fit_transform(sample_df['full_text'])
    X_eng_sample = sample_df[ENGINEERED_FEATURE_NAMES].values
    X_sample = hstack([X_tfidf_sample, X_eng_sample]).tocsr()
    
    xgb_full = XGBClassifier(
        n_estimators=150, max_depth=6, learning_rate=0.08,
        scale_pos_weight=imbalance_ratio, random_state=42, eval_metric='logloss'
    )
    xgb_full.fit(X_sample, sample_df['fraudulent'].values)
    
    feature_names = list(vec_full.get_feature_names_out()) + ENGINEERED_FEATURE_NAMES
    
    # SHAP summary plot
    print("Computing SHAP values...")
    explainer = shap.TreeExplainer(xgb_full)
    
    # Take a representative sub-sample for fast SHAP calculation
    shap_sample_X = X_sample[:500].toarray()
    shap_values = explainer.shap_values(shap_sample_X)
    
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, shap_sample_X, feature_names=feature_names, show=False, max_display=15)
    plt.title("SachHai / TrueLead - Top 15 Feature Importances (SHAP)", fontsize=14, pad=15)
    plt.tight_layout()
    shap_path = os.path.join(models_dir, "shap_summary.png")
    plt.savefig(shap_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"SHAP summary plot successfully saved to {shap_path}")
    
    # Engineered features specific importance ranking
    importances = xgb_full.feature_importances_
    eng_indices = [len(vec_full.get_feature_names_out()) + i for i in range(len(ENGINEERED_FEATURE_NAMES))]
    eng_importances = [(ENGINEERED_FEATURE_NAMES[i], importances[idx]) for i, idx in enumerate(eng_indices)]
    eng_importances.sort(key=lambda x: x[1], reverse=True)
    
    print("\nNon-Text Engineered Feature Importances (XGBoost Weight):")
    for feat, imp in eng_importances:
        print(f"  {feat:30s} : {imp:.6f}")

    print("\n========================================================")
    print(" 3. ERROR ANALYSIS (MISCLASSIFIED EXAMPLES)")
    print("========================================================")
    
    preds_sample = xgb_full.predict(X_sample)
    probs_sample = xgb_full.predict_proba(X_sample)[:, 1]
    targets = sample_df['fraudulent'].values
    
    false_negatives = sample_df[(targets == 1) & (preds_sample == 0)]
    false_positives = sample_df[(targets == 0) & (preds_sample == 1)]
    
    print(f"\nFalse Negatives (Scams missed by model): {len(false_negatives)}")
    if len(false_negatives) > 0:
        print("Sample False Negative Text Snippets:")
        for idx, row in false_negatives.head(3).iterrows():
            print(f" - [Title: {row.get('title', 'N/A')}] Snippet: {row['full_text'][:120]}...")
            
    print(f"\nFalse Positives (Genuine jobs flagged as scam): {len(false_positives)}")
    if len(false_positives) > 0:
        print("Sample False Positive Text Snippets:")
        for idx, row in false_positives.head(3).iterrows():
            print(f" - [Title: {row.get('title', 'N/A')}] Snippet: {row['full_text'][:120]}...")

    print("\n========================================================")
    print(" EVALUATION COMPLETE! Deliverables ready for pitch deck.")
    print("========================================================")

if __name__ == "__main__":
    main()
