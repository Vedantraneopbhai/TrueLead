import os
import joblib
import numpy as np
from scipy.sparse import hstack
import shap

try:
    from src.features import extract_features_from_text, NUMERIC_FEATURE_NAMES, BINARY_FLAG_NAMES, ENGINEERED_FEATURE_NAMES
    from src.clean import clean_text
    from src.domain_check import analyze_domains
    from src.lang_detector import detect_language
except ImportError:
    from features import extract_features_from_text, NUMERIC_FEATURE_NAMES, BINARY_FLAG_NAMES, ENGINEERED_FEATURE_NAMES
    from clean import clean_text
    from domain_check import analyze_domains
    from lang_detector import detect_language

def get_explainability_engine(models_dir=None):
    if models_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
    model_path = os.path.join(models_dir, "model_c_calibrated.joblib")
    base_model_path = os.path.join(models_dir, "model_c_base.joblib")
    pipeline_path = os.path.join(models_dir, "feature_pipeline.joblib")
    vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
    svd_path = os.path.join(models_dir, "text_svd.joblib")
    threshold_path = os.path.join(models_dir, "threshold_config.joblib")
    numeric_features_path = os.path.join(models_dir, "numeric_features.joblib")
    binary_features_path = os.path.join(models_dir, "binary_flags.joblib")
    
    # Fallback to standard xgboost_model if model_c_calibrated not yet written
    if not os.path.exists(model_path):
        model_path = os.path.join(models_dir, "xgboost_model.joblib")
        
    if not os.path.exists(model_path):
        return None
        
    model = joblib.load(model_path)
    base_model = joblib.load(base_model_path) if os.path.exists(base_model_path) else model
    pipeline = joblib.load(pipeline_path) if os.path.exists(pipeline_path) else {}
    vectorizer = pipeline.get('vectorizer') if isinstance(pipeline, dict) else None
    svd = pipeline.get('svd') if isinstance(pipeline, dict) else None
    if vectorizer is None and os.path.exists(vectorizer_path):
        vectorizer = joblib.load(vectorizer_path)
    if svd is None and os.path.exists(svd_path):
        svd = joblib.load(svd_path)
    if vectorizer is None:
        return None
    threshold_config = joblib.load(threshold_path) if os.path.exists(threshold_path) else {'threshold': 0.5}
    
    # Load feature names — use ENGINEERED_FEATURE_NAMES (numeric + binary) for full model input
    engineered_features = (
        pipeline.get('engineered_features')
        or pipeline.get('numeric_features')
        if isinstance(pipeline, dict) else None
    )
    if engineered_features is None:
        engineered_features = joblib.load(numeric_features_path) if os.path.exists(numeric_features_path) else ENGINEERED_FEATURE_NAMES

    binary_features = (
        pipeline.get('binary_features')
        if isinstance(pipeline, dict) and pipeline.get('binary_features')
        else joblib.load(binary_features_path) if os.path.exists(binary_features_path) else BINARY_FLAG_NAMES
    )
    
    explainer = None
    try:
        # Use uncalibrated base XGBoost tree model for SHAP tree explainer
        tree_model = base_model.estimator if hasattr(base_model, 'estimator') else base_model
        explainer = shap.TreeExplainer(tree_model)
    except Exception:
        pass
        
    return {
        'model': model,
        'base_model': base_model,
        'vectorizer': vectorizer,
        'svd': svd,
        'engineered_features': engineered_features,
        'binary_features': binary_features,
        'threshold': threshold_config.get('threshold', 0.5),
        'explainer': explainer
    }


def generate_report(score, flags, categorized_flags, feature_dict, lang_info, dom_res):
    """Generate a structured, concise scam analysis report."""
    
    # --- Verdict ---
    if score >= 70:
        verdict = "This posting exhibits multiple strong indicators of a fraudulent job scam."
        if feature_dict.get('fee_mentioned') or feature_dict.get('hindi_fee_mentioned'):
            verdict += " It demands upfront payment — a hallmark of fee-collection fraud."
        elif feature_dict.get('crypto_trading_scam'):
            verdict += " It appears to be a cryptocurrency/trading investment scheme disguised as employment."
        elif feature_dict.get('mlm_referral_language'):
            verdict += " The referral-based earning structure suggests a multi-level marketing or pyramid scheme."
        elif feature_dict.get('government_impersonation'):
            verdict += " It impersonates a government recruitment process to extract fees."
    elif score >= 30:
        verdict = "This posting contains suspicious elements that warrant careful verification before proceeding."
        active_flags = [k for k, v in feature_dict.items() if v == 1 and k in BINARY_FLAG_NAMES]
        if len(active_flags) == 1:
            verdict += " A single red flag was identified — it may be a poorly written legitimate posting, but caution is advised."
        else:
            verdict += f" {len(active_flags)} distinct risk signals were detected across multiple categories."
    else:
        verdict = "This posting appears structurally consistent with legitimate job listings."
        if feature_dict.get('legitimate_structure_score', 0) > 0.5:
            verdict += " It follows standard job posting conventions including proper sections and corporate contact information."
        else:
            verdict += " No strong scam indicators were found, though limited structural detail was provided."

    # --- Risk Breakdown per category ---
    risk_levels = {}
    category_scores = {
        'fee': (feature_dict.get('fee_mentioned', 0) + feature_dict.get('hindi_fee_mentioned', 0) + feature_dict.get('payment_before_joining', 0)) * 33,
        'urgency': (feature_dict.get('urgency_language', 0) + feature_dict.get('hindi_urgency_language', 0) + feature_dict.get('no_interview_required', 0)) * 28,
        'contact': (feature_dict.get('unofficial_contact', 0) + feature_dict.get('hindi_unofficial_contact', 0) + feature_dict.get('telegram_whatsapp_contact', 0) + feature_dict.get('requests_personal_docs', 0)) * 22,
        'domain': (feature_dict.get('domain_has_typosquat', 0) * 40 + feature_dict.get('domain_has_recent', 0) * 30 + feature_dict.get('domain_has_free_email', 0) * 20 + feature_dict.get('company_domain_mismatch', 0) * 25),
        'salary': (feature_dict.get('salary_seniority_mismatch', 0) + feature_dict.get('title_desc_mismatch', 0) + feature_dict.get('unrealistic_daily_earning', 0)) * 30,
    }
    
    for cat, cat_score in category_scores.items():
        if cat_score >= 60:
            risk_levels[cat] = 'Critical'
        elif cat_score >= 30:
            risk_levels[cat] = 'Moderate'
        elif cat_score > 0:
            risk_levels[cat] = 'Low'
        else:
            risk_levels[cat] = 'Clean'
    
    # Add special categories
    if feature_dict.get('mlm_referral_language'):
        risk_levels['mlm'] = 'Critical'
    if feature_dict.get('crypto_trading_scam'):
        risk_levels['crypto'] = 'Critical'
    if feature_dict.get('government_impersonation'):
        risk_levels['government'] = 'Critical'
    
    # --- Recommendations ---
    recommendations = []
    
    if score >= 70:
        recommendations.append("Do NOT share personal documents (Aadhaar, PAN, bank details) with this entity.")
        if feature_dict.get('fee_mentioned') or feature_dict.get('payment_before_joining'):
            recommendations.append("Do NOT pay any registration fee, deposit, or processing charge. Legitimate employers never charge candidates.")
        if feature_dict.get('telegram_whatsapp_contact'):
            recommendations.append("Avoid joining Telegram/WhatsApp groups for 'task-based' work — this is a common scam pattern.")
        if feature_dict.get('crypto_trading_scam'):
            recommendations.append("Do NOT deposit money into any trading platform. This is an investment scam, not a job.")
        if feature_dict.get('government_impersonation'):
            recommendations.append("Verify government job vacancies only on official portals (ssc.nic.in, indianrailways.gov.in, etc.).")
        recommendations.append("Report this posting on the platform where you found it.")
    elif score >= 30:
        recommendations.append("Verify the company's existence on the MCA portal (mca.gov.in) or LinkedIn.")
        if feature_dict.get('unofficial_contact') or feature_dict.get('domain_has_free_email'):
            recommendations.append("Contact the company through their official website email, not personal email addresses.")
        if feature_dict.get('no_interview_required'):
            recommendations.append("Be cautious of offers without any interview process — legitimate companies always screen candidates.")
        recommendations.append("If asked for money at any stage, treat it as a red flag and disengage.")
    else:
        recommendations.append("Standard precaution: always verify company details independently before sharing personal information.")
    
    return {
        'verdict': verdict,
        'risk_breakdown': risk_levels,
        'recommendations': recommendations
    }


def explain_prediction(text, company="", title="", engine=None):
    if engine is None:
        engine = get_explainability_engine()
        
    cleaned_input = clean_text(text)
    
    # 1. Language Detection
    lang_info = detect_language(text)
    
    # 2. Rule & Domain Feature Extraction
    feature_dict = extract_features_from_text(text, company=company, title=title)
    dom_res = analyze_domains(text, claimed_company=company)
    
    categorized_flags = {
        'fee': [],
        'urgency': [],
        'contact': [],
        'domain': dom_res['flags'],
        'salary': []
    }
    
    flags = []
    
    # Binary Flags for Human Explanations
    if feature_dict['fee_mentioned'] or feature_dict['hindi_fee_mentioned']:
        msg = f"Upfront fee / deposit required (Fee Severity Score: {feature_dict['fee_score']:.1f})."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
    if feature_dict['payment_before_joining']:
        msg = "Payment required prior to interview or work commencement."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
        
    if feature_dict['urgency_language'] or feature_dict['hindi_urgency_language']:
        msg = f"Artificial urgency language detected (Urgency Density: {feature_dict['urgency_score']:.1f} per 100 words)."
        categorized_flags['urgency'].append(msg)
        flags.append(msg)
    if feature_dict['no_interview_required']:
        msg = "Direct selection without standard interview or technical screening offered."
        categorized_flags['urgency'].append(msg)
        flags.append(msg)
        
    if feature_dict['unofficial_contact'] or feature_dict['hindi_unofficial_contact']:
        msg = f"Non-corporate contact channel used (Contact Risk Score: {feature_dict['contact_score']:.1f})."
        categorized_flags['contact'].append(msg)
        flags.append(msg)
    if feature_dict['requests_personal_docs']:
        msg = "Upfront request for sensitive identity/financial documents (Aadhaar/PAN/Bank details)."
        categorized_flags['contact'].append(msg)
        flags.append(msg)
    if feature_dict.get('telegram_whatsapp_contact'):
        msg = "Uses Telegram/WhatsApp as primary contact or task channel — common in task-based scams."
        categorized_flags['contact'].append(msg)
        flags.append(msg)
        
    if feature_dict['salary_seniority_mismatch']:
        msg = f"Unrealistic salary ratio detected ({feature_dict['salary_ratio']:.1f}x expected benchmark)."
        categorized_flags['salary'].append(msg)
        flags.append(msg)
    if feature_dict['title_desc_mismatch']:
        msg = "Mismatch between claimed professional job title and actual low-skill task description."
        categorized_flags['salary'].append(msg)
        flags.append(msg)
    if feature_dict.get('unrealistic_daily_earning'):
        msg = "Claims unrealistic daily earnings — a hallmark of task-based scams."
        categorized_flags['salary'].append(msg)
        flags.append(msg)

    # New category flags
    if feature_dict.get('mlm_referral_language'):
        msg = "Multi-level marketing / pyramid scheme language detected (referral commissions, team building, starter kits)."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
    if feature_dict.get('crypto_trading_scam'):
        msg = "Cryptocurrency or trading investment scheme disguised as employment."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
    if feature_dict.get('government_impersonation'):
        msg = "Impersonation of government recruitment body (SSC/Railway/Postal) to collect fees."
        categorized_flags['urgency'].append(msg)
        flags.append(msg)

    flags.extend(dom_res['flags'])

    # Fallback if engine unavailable
    if engine is None:
        risk_score = min(95, max(5, len(flags) * 25))
        confidence = "High Confidence" if risk_score > 60 or risk_score < 20 else "Needs Review"
        report = generate_report(risk_score, flags, categorized_flags, feature_dict, lang_info, dom_res)
        return {
            'score': risk_score,
            'confidence': confidence,
            'flags': flags if flags else ["No suspicious flags detected."],
            'categorized_flags': categorized_flags,
            'detected_language': lang_info['label'],
            'domain_info': dom_res,
            'shap_features': [],
            'report': report
        }
        
    model = engine['model']
    vectorizer = engine['vectorizer']
    svd = engine.get('svd')
    engineered_features_keys = engine.get('engineered_features', ENGINEERED_FEATURE_NAMES)
    binary_features = engine.get('binary_features', BINARY_FLAG_NAMES)
    optimal_th = engine.get('threshold', 0.5)
    explainer = engine.get('explainer')
    
    # Vectorize input: TF-IDF -> SVD text embedding + ALL engineered features
    tfidf_vec = vectorizer.transform([cleaned_input])
    if svd is not None:
        text_embed = svd.transform(tfidf_vec)
    else:
        text_embed = tfidf_vec.toarray()
    
    # Use ALL engineered features (numeric + binary) — matching training pipeline
    eng_vals = np.array([[feature_dict.get(k, 0.0) for k in engineered_features_keys]])
    X_input = np.hstack([text_embed, eng_vals])
    
    # Model C Calibrated Probability Prediction
    proba = float(model.predict_proba(X_input)[0, 1])
    
    # Normalize score relative to optimal threshold (below threshold = <50% risk, above = >=50% risk)
    if optimal_th > 0 and optimal_th < 1.0:
        if proba < optimal_th:
            normalized_score = (proba / optimal_th) * 50.0
        else:
            normalized_score = 50.0 + ((proba - optimal_th) / max(0.001, 1.0 - optimal_th)) * 50.0
    else:
        normalized_score = proba * 100.0
        
    risk_score = int(round(np.clip(normalized_score, 0.0, 100.0)))
    
    # If no rule flags triggered and high legitimate structure, ensure clean score (< 20%)
    if not flags or flags == ["No suspicious flags detected."]:
        if feature_dict.get('legitimate_structure_score', 0) > 0.4:
            risk_score = min(risk_score, 12)
        else:
            risk_score = min(risk_score, 25)
    elif len(flags) == 1 and "Text pattern" in flags[0]:
        risk_score = min(risk_score, 30)
    
    # Threshold & Confidence evaluation
    margin = abs(proba - optimal_th)
    confidence = "High Confidence" if margin > 0.20 else "Needs Review"
    
    # SHAP feature analysis
    shap_features = []
    if explainer is not None:
        try:
            shap_values = explainer.shap_values(X_input)
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0]
            else:
                shap_vals = shap_values[0]
                
            # Build feature names matching input vector layout
            if svd is not None:
                text_feature_names = [f'text_svd_{i}' for i in range(text_embed.shape[1])]
            else:
                text_feature_names = list(vectorizer.get_feature_names_out())
            all_feature_names = text_feature_names + list(engineered_features_keys)
            
            top_indices = np.argsort(np.abs(shap_vals))[::-1]
            
            for idx in top_indices[:10]:
                val = float(shap_vals[idx])
                if idx < len(all_feature_names):
                    fname = all_feature_names[idx]
                else:
                    fname = f"feature_{idx}"
                if abs(val) > 0.01:
                    shap_features.append({'feature': fname, 'importance': round(val, 4)})
                    # Only add text pattern indicators for text features, not engineered ones
                    if fname.startswith('text_svd_') is False and fname not in engineered_features_keys and val > 0.02:
                        if not any(fname in f for f in flags):
                            flags.append(f"Text pattern indicator: '{fname}'")
        except Exception:
            pass
            
    if not flags:
        flags.append("Job posting appears genuine based on structural, behavioral, and text pattern analysis.")
    
    # Generate structured report
    report = generate_report(risk_score, flags, categorized_flags, feature_dict, lang_info, dom_res)
        
    return {
        'score': risk_score,
        'confidence': confidence,
        'flags': flags,
        'categorized_flags': categorized_flags,
        'detected_language': lang_info['label'],
        'domain_info': dom_res,
        'shap_features': shap_features,
        'report': report
    }
