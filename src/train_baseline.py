import os
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

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
        
    print(f"Loading featured dataset from {featured_path}...")
    df = pd.read_csv(featured_path)
    df['full_text'] = df['full_text'].fillna('')
    
    y = df['fraudulent'].values
    n_genuine = np.sum(y == 0)
    n_fraud = np.sum(y == 1)
    imbalance_ratio = n_genuine / max(1, n_fraud)
    
    print(f"\n--- DATASET CLASS IMBALANCE ---")
    print(f"Genuine (0): {n_genuine}")
    print(f"Fraudulent (1): {n_fraud}")
    print(f"Class Imbalance Ratio: {imbalance_ratio:.2f}:1")
    print(f"Setting XGBoost scale_pos_weight = {imbalance_ratio:.2f}\n")
    
    # 5-Fold Stratified Cross Validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    fold_metrics = []
    
    print("Performing 5-Fold Stratified Cross-Validation on Full Feature Model...")
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(df, y), 1):
        train_df, test_df = df.iloc[train_idx], df.iloc[test_idx]
        
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
        X_train_tfidf = vectorizer.fit_transform(train_df['full_text'])
        X_test_tfidf = vectorizer.transform(test_df['full_text'])
        
        X_train_eng = train_df[ENGINEERED_FEATURE_NAMES].values
        X_test_eng = test_df[ENGINEERED_FEATURE_NAMES].values
        
        X_train = hstack([X_train_tfidf, X_train_eng]).tocsr()
        X_test = hstack([X_test_tfidf, X_test_eng]).tocsr()
        
        y_train, y_test = y[train_idx], y[test_idx]
        
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.08,
            scale_pos_weight=imbalance_ratio,
            random_state=42,
            eval_metric='logloss',
            subsample=0.8,
            colsample_bytree=0.8
        )
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        p = precision_score(y_test, y_pred, zero_division=0)
        r = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        
        fold_metrics.append({'precision': p, 'recall': r, 'f1': f1, 'auc': auc})
        print(f"Fold {fold}: Precision={p:.4f}, Recall={r:.4f}, F1={f1:.4f}, ROC-AUC={auc:.4f}")
        
    avg_p = np.mean([m['precision'] for m in fold_metrics])
    avg_r = np.mean([m['recall'] for m in fold_metrics])
    avg_f1 = np.mean([m['f1'] for m in fold_metrics])
    avg_auc = np.mean([m['auc'] for m in fold_metrics])
    
    print("\n--- 5-FOLD CROSS-VALIDATION SUMMARY ---")
    print(f"Mean Precision: {avg_p:.4f}")
    print(f"Mean Recall:    {avg_r:.4f}")
    print(f"Mean F1-Score:  {avg_f1:.4f}")
    print(f"Mean ROC-AUC:   {avg_auc:.4f}\n")
    
    # Fit final model on 100% of data for production API use
    print("Training final model on 100% of dataset...")
    final_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X_tfidf_all = final_vectorizer.fit_transform(df['full_text'])
    X_eng_all = df[ENGINEERED_FEATURE_NAMES].values
    X_all = hstack([X_tfidf_all, X_eng_all]).tocsr()
    
    final_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.08,
        scale_pos_weight=imbalance_ratio,
        random_state=42,
        eval_metric='logloss',
        subsample=0.8,
        colsample_bytree=0.8
    )
    final_model.fit(X_all, y)
    
    # Save artifacts
    model_path = os.path.join(models_dir, "xgboost_model.joblib")
    vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
    features_path = os.path.join(models_dir, "rule_features.joblib")
    
    joblib.dump(final_model, model_path)
    joblib.dump(final_vectorizer, vectorizer_path)
    joblib.dump(ENGINEERED_FEATURE_NAMES, features_path)
    
    print(f"Model saved to {model_path}")
    print(f"Vectorizer saved to {vectorizer_path}")
    print(f"Engineered features list saved to {features_path}")

if __name__ == "__main__":
    main()
