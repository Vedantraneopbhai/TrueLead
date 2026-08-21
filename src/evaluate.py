import os
import warnings

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from imblearn.over_sampling import SMOTE
from scipy.sparse import hstack, issparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.decomposition import TruncatedSVD
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier

try:
    from src.clean import main as clean_main
    from src.features import main as features_main, NUMERIC_FEATURE_NAMES, BINARY_FLAG_NAMES, ENGINEERED_FEATURE_NAMES
    from src.explain import explain_prediction, get_explainability_engine
except ImportError:
    from clean import main as clean_main
    from features import main as features_main, NUMERIC_FEATURE_NAMES, BINARY_FLAG_NAMES, ENGINEERED_FEATURE_NAMES
    from explain import explain_prediction, get_explainability_engine

warnings.filterwarnings('ignore')

RAW_DATASETS = [
    ('fake_job_postings.csv', 'fraudulent', ['title', 'company_profile', 'description', 'requirements']),
    ('indian_job_fraud.csv', 'label', ['title', 'company', 'description', 'requirements', 'contact'])
]


def _resolve_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _normalize_label_series(series):
    if series.dtype.kind in 'biufc':
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)
    normalized = series.astype(str).str.lower().str.strip()
    return normalized.map(lambda x: 1 if x in {'1', 'fake', 'fraud', 'fraudulent', 'scam', 'true'} else 0).astype(int)


def _combined_text(df, columns):
    existing = [column for column in columns if column in df.columns]
    if not existing:
        return pd.Series([''] * len(df), index=df.index)
    return df[existing].fillna('').astype(str).agg(' '.join, axis=1)


def print_data_audit(base_dir):
    print('\n============================================================')
    print('STEP 1 — DATA AUDIT')
    print('============================================================')
    for filename, label_column, text_columns in RAW_DATASETS:
        path = os.path.join(base_dir, 'data', filename) if filename in {'fake_job_postings.csv', 'indian_job_fraud.csv'} else None
        if path is None or not os.path.exists(path):
            path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            path = os.path.join(base_dir, 'fake job posting' if filename == 'fake_job_postings.csv' else 'fake indian job posting', filename)
        if not os.path.exists(path):
            continue

        df = pd.read_csv(path)
        print(f'\n[{filename}] shape={df.shape}')
        if label_column in df.columns:
            labels = _normalize_label_series(df[label_column])
            real_count = int((labels == 0).sum())
            fake_count = int((labels == 1).sum())
            ratio = real_count / max(1, fake_count)
            print(f'class balance: real={real_count}, fake={fake_count}, ratio={ratio:.2f}:1')
        else:
            print(f'class balance: label column {label_column} not found')
        print('missing values per column:')
        print(df.isna().sum().to_string())
        text_series = _combined_text(df, text_columns)
        word_counts = text_series.str.split().str.len()
        print(f'avg words per posting: {word_counts.mean():.2f}')
        if label_column in df.columns:
            labels = _normalize_label_series(df[label_column])
            for value in [0, 1]:
                subset = word_counts[labels == value]
                print(f'avg words for {"real" if value == 0 else "fake"}: {subset.mean():.2f} (n={len(subset)})')


def rebuild_featured_dataset(base_dir):
    print('\nRefreshing cleaned and featured datasets from scratch...')
    clean_main()
    features_main()
    featured_path = os.path.join(base_dir, 'data', 'featured.csv')
    if not os.path.exists(featured_path):
        raise FileNotFoundError(f'Featured dataset not found at {featured_path}.')
    df = pd.read_csv(featured_path)
    if 'full_text' not in df.columns:
        df['full_text'] = ''
    df['full_text'] = df['full_text'].fillna('')
    if 'source' not in df.columns:
        df['source'] = 'dataset'
    for column in NUMERIC_FEATURE_NAMES:
        if column not in df.columns:
            df[column] = -1.0 if 'missing' in column or 'age' in column else 0.0
    for column in BINARY_FLAG_NAMES:
        if column not in df.columns:
            df[column] = 0
    df[NUMERIC_FEATURE_NAMES] = df[NUMERIC_FEATURE_NAMES].apply(pd.to_numeric, errors='coerce').fillna(-1.0)
    df[BINARY_FLAG_NAMES] = df[BINARY_FLAG_NAMES].fillna(0).astype(int)
    # Ensure all engineered features exist
    for column in ENGINEERED_FEATURE_NAMES:
        if column not in df.columns:
            df[column] = 0
    return df


def make_xgb(random_state=42, n_estimators=220, max_depth=6, learning_rate=0.06):
    return XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.0,
        reg_lambda=1.0,
        min_child_weight=1,
        objective='binary:logistic',
        eval_metric='logloss',
        tree_method='hist',
        n_jobs=-1,
        random_state=random_state
    )


def make_text_embeddings(train_texts, test_texts, n_components=256, random_state=42):
    vectorizer = TfidfVectorizer(max_features=12000, stop_words='english', ngram_range=(1, 2), min_df=2)
    X_train_tfidf = vectorizer.fit_transform(train_texts)
    X_test_tfidf = vectorizer.transform(test_texts)

    max_components = max(2, min(n_components, X_train_tfidf.shape[1] - 1, max(1, X_train_tfidf.shape[0] - 1)))
    if max_components < 2:
        X_train_dense = X_train_tfidf.toarray()
        X_test_dense = X_test_tfidf.toarray()
        return vectorizer, None, X_train_dense, X_test_dense

    svd = TruncatedSVD(n_components=max_components, random_state=random_state)
    X_train_dense = svd.fit_transform(X_train_tfidf)
    X_test_dense = svd.transform(X_test_tfidf)
    return vectorizer, svd, X_train_dense, X_test_dense


def smote_and_weight(X, y, use_smote, random_state=42):
    y = np.asarray(y).astype(int)
    classes = np.unique(y)
    class_weights = compute_class_weight(class_weight='balanced', classes=classes, y=y)
    weight_map = {int(cls): float(weight) for cls, weight in zip(classes, class_weights)}

    if use_smote:
        counts = np.bincount(y)
        minority_count = int(counts[counts > 0].min()) if len(counts[counts > 0]) else 0
        if minority_count >= 2:
            smote = SMOTE(random_state=random_state, k_neighbors=min(5, minority_count - 1))
            try:
                X_res, y_res = smote.fit_resample(X, y)
                sample_weight = np.array([weight_map[int(label)] for label in y_res], dtype=float)
                return X_res, y_res, sample_weight
            except Exception as exc:
                print(f'SMOTE warning: {exc}. Continuing with class weighting only for this split.')

    sample_weight = np.array([weight_map[int(label)] for label in y], dtype=float)
    return X, y, sample_weight


def evaluate_predictions(y_true, y_pred, y_proba):
    return {
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'auc': roc_auc_score(y_true, y_proba) if len(np.unique(y_true)) > 1 else 0.0
    }


def safe_hard_f1(y_true, y_pred, hard_mask):
    if hard_mask.sum() == 0:
        return f1_score(y_true, y_pred, zero_division=0)
    return f1_score(y_true[hard_mask], y_pred[hard_mask], zero_division=0)


def main():
    base_dir = _resolve_base_dir()
    data_dir = os.path.join(base_dir, 'data')
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print_data_audit(base_dir)

    df = rebuild_featured_dataset(base_dir)
    y = pd.to_numeric(df['fraudulent'], errors='coerce').fillna(0).astype(int).values
    full_text = df['full_text'].fillna('').astype(str).values
    hard_mask_global = (df['source'].astype(str) == 'hard_examples').values

    n_real = int((y == 0).sum())
    n_fake = int((y == 1).sum())
    imbalance_ratio = n_real / max(1, n_fake)
    use_smote = imbalance_ratio > 4.0

    print('\n============================================================')
    print('STEP 4 — LATE-FUSION TRAINING')
    print('============================================================')
    print(f'Featured rows: {len(df)}')
    print(f'Class balance after merge: real={n_real}, fake={n_fake}, ratio={imbalance_ratio:.2f}:1')
    print(f'Imbalance mitigation enabled: {use_smote}')

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    metrics_a = {'precision': [], 'recall': [], 'f1': [], 'auc': [], 'hard_f1': []}
    metrics_b = {'precision': [], 'recall': [], 'f1': [], 'auc': [], 'hard_f1': []}
    metrics_c = {'precision': [], 'recall': [], 'f1': [], 'auc': [], 'hard_f1': []}

    for fold, (train_idx, test_idx) in enumerate(skf.split(df, y), 1):
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]
        hard_in_test = hard_mask_global[test_idx]

        vectorizer, svd, X_train_tfidf, X_test_tfidf = make_text_embeddings(
            train_df['full_text'].fillna('').astype(str),
            test_df['full_text'].fillna('').astype(str)
        )

        X_train_num = train_df[ENGINEERED_FEATURE_NAMES].fillna(0).astype(float).values
        X_test_num = test_df[ENGINEERED_FEATURE_NAMES].fillna(0).astype(float).values
        X_train_comb = np.hstack([X_train_tfidf, X_train_num])
        X_test_comb = np.hstack([X_test_tfidf, X_test_num])

        X_train_num_res, y_train_num_res, sw_num = smote_and_weight(X_train_num, y_train, use_smote)
        X_train_tfidf_res, y_train_tfidf_res, sw_text = smote_and_weight(X_train_tfidf, y_train, use_smote)
        X_train_comb_res, y_train_comb_res, sw_comb = smote_and_weight(X_train_comb, y_train, use_smote)

        model_a = make_xgb(n_estimators=180, max_depth=4, learning_rate=0.08)
        model_b = make_xgb(n_estimators=180, max_depth=5, learning_rate=0.07)
        model_c = make_xgb(n_estimators=260, max_depth=6, learning_rate=0.06)

        model_a.fit(X_train_num_res, y_train_num_res, sample_weight=sw_num)
        model_b.fit(X_train_tfidf_res, y_train_tfidf_res, sample_weight=sw_text)
        model_c.fit(X_train_comb_res, y_train_comb_res, sample_weight=sw_comb)

        y_pred_a = model_a.predict(X_test_num)
        y_proba_a = model_a.predict_proba(X_test_num)[:, 1]
        y_pred_b = model_b.predict(X_test_tfidf)
        y_proba_b = model_b.predict_proba(X_test_tfidf)[:, 1]
        y_pred_c = model_c.predict(X_test_comb)
        y_proba_c = model_c.predict_proba(X_test_comb)[:, 1]

        fold_metrics = {
            'A': evaluate_predictions(y_test, y_pred_a, y_proba_a),
            'B': evaluate_predictions(y_test, y_pred_b, y_proba_b),
            'C': evaluate_predictions(y_test, y_pred_c, y_proba_c),
        }

        for key, y_pred in [('A', y_pred_a), ('B', y_pred_b), ('C', y_pred_c)]:
            hard_score = safe_hard_f1(y_test, y_pred, hard_in_test)
            fold_metrics[key]['hard_f1'] = hard_score

        for key, metrics in [('A', metrics_a), ('B', metrics_b), ('C', metrics_c)]:
            metrics['precision'].append(fold_metrics[key]['precision'])
            metrics['recall'].append(fold_metrics[key]['recall'])
            metrics['f1'].append(fold_metrics[key]['f1'])
            metrics['auc'].append(fold_metrics[key]['auc'])
            metrics['hard_f1'].append(fold_metrics[key]['hard_f1'])

        print(
            f'Fold {fold}: '
            f"A F1={fold_metrics['A']['f1']:.4f}, "
            f"B F1={fold_metrics['B']['f1']:.4f}, "
            f"C F1={fold_metrics['C']['f1']:.4f}"
        )

    print('\n============================================================')
    print('STEP 5 — ABLATION EVALUATION')
    print('============================================================')
    for label, metrics in [
        ('Model A (Structured only)', metrics_a),
        ('Model B (Text only)', metrics_b),
        ('Model C (Combined)', metrics_c),
    ]:
        print(
            f"{label:28s} | "
            f"Precision={np.mean(metrics['precision']):.4f} | "
            f"Recall={np.mean(metrics['recall']):.4f} | "
            f"F1={np.mean(metrics['f1']):.4f} | "
            f"Hard F1={np.mean(metrics['hard_f1']):.4f} | "
            f"AUC={np.mean(metrics['auc']):.4f}"
        )

    plt.figure(figsize=(10, 5), dpi=300)
    labels = ['Structured', 'Text', 'Combined']
    overall = [np.mean(metrics_a['f1']), np.mean(metrics_b['f1']), np.mean(metrics_c['f1'])]
    hard = [np.mean(metrics_a['hard_f1']), np.mean(metrics_b['hard_f1']), np.mean(metrics_c['hard_f1'])]
    x = np.arange(len(labels))
    width = 0.34
    plt.bar(x - width / 2, overall, width, label='Overall F1', color='#0f766e')
    plt.bar(x + width / 2, hard, width, label='Hard examples F1', color='#f97316')
    plt.ylabel('F1 score')
    plt.title('TrueLead Ablation Study')
    plt.xticks(x, labels)
    plt.ylim(0, 1.05)
    plt.grid(axis='y', linestyle='--', alpha=0.25)
    plt.legend()
    plt.tight_layout()
    ablation_path = os.path.join(reports_dir, 'ablation_chart.png')
    plt.savefig(ablation_path)
    plt.close()
    print(f'\nAblation chart saved to {ablation_path}')

    print('\n============================================================')
    print('STEP 6 — CALIBRATION AND THRESHOLD TUNING')
    print('============================================================')
    final_vectorizer = TfidfVectorizer(max_features=12000, stop_words='english', ngram_range=(1, 2), min_df=2)
    X_tfidf_all = final_vectorizer.fit_transform(full_text)
    final_svd = TruncatedSVD(n_components=max(2, min(256, X_tfidf_all.shape[1] - 1, max(1, X_tfidf_all.shape[0] - 1))), random_state=42)
    X_text_all = final_svd.fit_transform(X_tfidf_all)
    X_num_all = df[ENGINEERED_FEATURE_NAMES].fillna(0).astype(float).values
    X_comb_all = np.hstack([X_text_all, X_num_all])

    X_num_res, y_num_res, sw_num = smote_and_weight(X_num_all, y, use_smote)
    X_text_res, y_text_res, sw_text = smote_and_weight(X_text_all, y, use_smote)
    X_comb_res, y_comb_res, sw_comb = smote_and_weight(X_comb_all, y, use_smote)

    final_model_a = make_xgb(n_estimators=200, max_depth=4, learning_rate=0.08)
    final_model_b = make_xgb(n_estimators=200, max_depth=5, learning_rate=0.07)
    base_model_c = make_xgb(n_estimators=300, max_depth=6, learning_rate=0.06)

    final_model_a.fit(X_num_res, y_num_res, sample_weight=sw_num)
    final_model_b.fit(X_text_res, y_text_res, sample_weight=sw_text)
    base_model_c.fit(X_comb_res, y_comb_res, sample_weight=sw_comb)

    calibrated_model_c = CalibratedClassifierCV(base_model_c, method='sigmoid', cv='prefit')
    calibrated_model_c.fit(X_comb_all, y)

    probs = calibrated_model_c.predict_proba(X_comb_all)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y, probs)
    if len(thresholds) == 0:
        optimal_threshold = 0.5
    else:
        costs = []
        for threshold in thresholds:
            preds = (probs >= threshold).astype(int)
            false_negatives = int(np.sum((y == 1) & (preds == 0)))
            false_positives = int(np.sum((y == 0) & (preds == 1)))
            costs.append((4 * false_negatives) + false_positives)
        optimal_threshold = float(thresholds[int(np.argmin(costs))])

    final_preds = (probs >= optimal_threshold).astype(int)
    tuned_precision = precision_score(y, final_preds, zero_division=0)
    tuned_recall = recall_score(y, final_preds, zero_division=0)
    tuned_f1 = f1_score(y, final_preds, zero_division=0)
    tuned_auc = roc_auc_score(y, probs)

    print(f'Optimal threshold: {optimal_threshold:.4f}')
    print(
        f'Tuned Model C metrics: Precision={tuned_precision:.4f}, '
        f'Recall={tuned_recall:.4f}, F1={tuned_f1:.4f}, AUC={tuned_auc:.4f}'
    )

    print('\nGenerating SHAP summary plot for Model C...')
    try:
        sample_size = min(250, X_comb_all.shape[0])
        sample_indices = np.random.default_rng(42).choice(X_comb_all.shape[0], size=sample_size, replace=False)
        X_sample_dense = np.asarray(X_comb_all[sample_indices])
        feature_names = [f'text_svd_{i}' for i in range(X_text_all.shape[1])] + ENGINEERED_FEATURE_NAMES
        explainer = shap.TreeExplainer(base_model_c)
        shap_values = explainer.shap_values(X_sample_dense)
        plt.figure(figsize=(11, 7), dpi=300)
        shap.summary_plot(shap_values, X_sample_dense, feature_names=feature_names, show=False, max_display=15)
        shap_path = os.path.join(reports_dir, 'shap_summary.png')
        plt.tight_layout()
        plt.savefig(shap_path, bbox_inches='tight')
        plt.close()
        print(f'SHAP summary plot saved to {shap_path}')
    except Exception as exc:
        print(f'SHAP plot generation warning: {exc}')

    print('\n============================================================')
    print('STEP 7 — SAVING MODEL ARTIFACTS')
    print('============================================================')
    feature_pipeline = {
        'vectorizer': final_vectorizer,
        'svd': final_svd,
        'numeric_features': ENGINEERED_FEATURE_NAMES,
        'binary_features': BINARY_FLAG_NAMES,
        'engineered_features': ENGINEERED_FEATURE_NAMES,
        'text_column': 'full_text',
        'version': 2,
    }

    joblib.dump(final_model_a, os.path.join(models_dir, 'model_a_structured.joblib'))
    joblib.dump(final_model_b, os.path.join(models_dir, 'model_b_text.joblib'))
    joblib.dump(base_model_c, os.path.join(models_dir, 'model_c_base.joblib'))
    joblib.dump(calibrated_model_c, os.path.join(models_dir, 'model_c_calibrated.joblib'))
    joblib.dump(calibrated_model_c, os.path.join(models_dir, 'xgboost_model.joblib'))
    joblib.dump(final_vectorizer, os.path.join(models_dir, 'tfidf_vectorizer.joblib'))
    joblib.dump(final_svd, os.path.join(models_dir, 'text_svd.joblib'))
    joblib.dump(feature_pipeline, os.path.join(models_dir, 'feature_pipeline.joblib'))
    joblib.dump(ENGINEERED_FEATURE_NAMES, os.path.join(models_dir, 'numeric_features.joblib'))
    joblib.dump(BINARY_FLAG_NAMES, os.path.join(models_dir, 'binary_flags.joblib'))
    joblib.dump(BINARY_FLAG_NAMES, os.path.join(models_dir, 'rule_features.joblib'))
    joblib.dump({
        'threshold': optimal_threshold,
        'false_negative_cost': 4,
        'false_positive_cost': 1,
        'precision': tuned_precision,
        'recall': tuned_recall,
        'f1': tuned_f1,
        'auc': tuned_auc,
    }, os.path.join(models_dir, 'threshold_config.joblib'))

    print(f'Artifacts successfully saved to {models_dir}')

    print('\n============================================================')
    print('API SMOKE TEST')
    print('============================================================')
    try:
        engine = get_explainability_engine(models_dir=models_dir)
        sample_row = df[df['fraudulent'] == 1].head(1)
        if sample_row.empty:
            sample_row = df.head(1)
        sample_text = sample_row.iloc[0]['full_text']
        sample_company = str(sample_row.iloc[0].get('company_profile', '')) if 'company_profile' in sample_row.columns else ''
        sample_title = str(sample_row.iloc[0].get('title', '')) if 'title' in sample_row.columns else ''
        sample_result = explain_prediction(sample_text, company=sample_company, title=sample_title, engine=engine)
        print({'score': sample_result.get('score'), 'flags': sample_result.get('flags')})
    except Exception as exc:
        print(f'API smoke test warning: {exc}')


if __name__ == '__main__':
    main()
