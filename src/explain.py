import os
import joblib
import numpy as np
from scipy.sparse import hstack
import shap

try:
    from src.features import extract_features_from_text, ENGINEERED_FEATURE_NAMES
    from src.clean import clean_text
    from src.domain_check import analyze_domains
    from src.lang_detector import detect_language
except ImportError:
    from features import extract_features_from_text, ENGINEERED_FEATURE_NAMES
    from clean import clean_text
    from domain_check import analyze_domains
    from lang_detector import detect_language

def get_explainability_engine(models_dir=None):
    if models_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
    model_path = os.path.join(models_dir, "xgboost_model.joblib")
    vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
    rule_features_path = os.path.join(models_dir, "rule_features.joblib")
    
    if not (os.path.exists(model_path) and os.path.exists(vectorizer_path)):
        return None
        
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    rule_features = joblib.load(rule_features_path) if os.path.exists(rule_features_path) else ENGINEERED_FEATURE_NAMES
    
    explainer = None
    try:
        explainer = shap.TreeExplainer(model)
    except Exception:
        pass
        
    return {
        'model': model,
        'vectorizer': vectorizer,
        'rule_features': rule_features,
        'explainer': explainer
    }

def explain_prediction(text, company="", title="", engine=None):
    if engine is None:
        engine = get_explainability_engine()
        
    cleaned_input = clean_text(text)
    
    # 1. Language Detection (Phase D)
    lang_info = detect_language(text)
    
    # 2. Rule & Domain Checks (Phases A, B, D)
    rule_dict = extract_features_from_text(text, company=company, title=title)
    dom_res = analyze_domains(text, claimed_company=company)
    
    categorized_flags = {
        'fee': [],
        'urgency': [],
        'contact': [],
        'domain': dom_res['flags'],
        'salary': []
    }
    
    flags = []
    
    # Fee & Payment Flags
    if rule_dict['fee_mentioned'] or rule_dict['hindi_fee_mentioned']:
        msg = "Upfront registration, processing, or security deposit fee requested before joining."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
    if rule_dict['payment_before_joining']:
        msg = "Payment required prior to interview or work commencement."
        categorized_flags['fee'].append(msg)
        flags.append(msg)
        
    # Urgency Flags
    if rule_dict['urgency_language'] or rule_dict['hindi_urgency_language']:
        msg = "Artificial urgency language detected ('apply within X hours', 'limited slots', 'immediate joining')."
        categorized_flags['urgency'].append(msg)
        flags.append(msg)
    if rule_dict['no_interview_required']:
        msg = "Direct selection without standard interview or technical screening offered."
        categorized_flags['urgency'].append(msg)
        flags.append(msg)
        
    # Contact Flags
    if rule_dict['unofficial_contact'] or rule_dict['hindi_unofficial_contact']:
        msg = "Recruiter directs communication through personal webmail or messaging apps (WhatsApp/Telegram/Gmail)."
        categorized_flags['contact'].append(msg)
        flags.append(msg)
    if rule_dict['requests_personal_docs']:
        msg = "Upfront request for sensitive identity/financial documents (Aadhaar/PAN/Bank details)."
        categorized_flags['contact'].append(msg)
        flags.append(msg)
        
    # Salary & Consistency Flags
    if rule_dict['salary_seniority_mismatch']:
        msg = "Unrealistic high compensation promised for simple entry-level or typing tasks."
        categorized_flags['salary'].append(msg)
        flags.append(msg)
    if rule_dict['title_desc_mismatch']:
        msg = "Mismatch between claimed professional job title and actual low-skill task description."
        categorized_flags['salary'].append(msg)
        flags.append(msg)

    # Domain flags merge
    flags.extend(dom_res['flags'])

    # If engine not available, fallback to rule-based score
    if engine is None:
        risk_score = min(95, max(5, len(flags) * 25))
        confidence = "High Confidence" if risk_score > 60 or risk_score < 20 else "Needs Review"
        return {
            'score': risk_score,
            'confidence': confidence,
            'flags': flags if flags else ["No suspicious flags detected."],
            'categorized_flags': categorized_flags,
            'detected_language': lang_info['label'],
            'domain_info': dom_res,
            'shap_features': []
        }
        
    model = engine['model']
    vectorizer = engine['vectorizer']
    rule_features_keys = engine['rule_features']
    explainer = engine.get('explainer')
    
    # 3. Vectorize input text
    tfidf_vec = vectorizer.transform([cleaned_input])
    rule_vals = np.array([[rule_dict.get(k, 0) for k in rule_features_keys]])
    X_input = hstack([tfidf_vec, rule_vals]).tocsr()
    
    # Model prediction probability
    proba = float(model.predict_proba(X_input)[0, 1])
    risk_score = int(round(proba * 100))
    
    # Confidence calculation
    margin = abs(proba - 0.5)
    confidence = "High Confidence" if margin > 0.25 else "Needs Review"
    
    # 4. SHAP feature analysis
    shap_features = []
    if explainer is not None:
        try:
            shap_values = explainer.shap_values(X_input)
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0]
            else:
                shap_vals = shap_values[0]
                
            feature_names = list(vectorizer.get_feature_names_out()) + rule_features_keys
            top_indices = np.argsort(shap_vals)[::-1]
            
            for idx in top_indices[:7]:
                val = float(shap_vals[idx])
                fname = feature_names[idx]
                if val > 0.03:
                    shap_features.append({'feature': fname, 'importance': round(val, 4)})
                    if fname not in rule_features_keys:
                        flags.append(f"Text pattern indicator: '{fname}'")
        except Exception:
            pass
            
    if not flags:
        flags.append("Job posting appears genuine based on structural, behavioral, and text pattern analysis.")
        
    return {
        'score': risk_score,
        'confidence': confidence,
        'flags': flags,
        'categorized_flags': categorized_flags,
        'detected_language': lang_info['label'],
        'domain_info': dom_res,
        'shap_features': shap_features
    }
