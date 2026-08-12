import os
import re
import pandas as pd
import numpy as np

try:
    from src.domain_check import analyze_domains
except ImportError:
    from domain_check import analyze_domains

FEE_REGEX = re.compile(
    r'\b(registration fee|security deposit|training fee|processing fee|gate fee|refundable deposit|pay inr|pay rs|payment required|enrollment fee|charges apply|deposit amount|pay before|fees apply|laptop deposit|id card fee|badge fee)\b',
    re.IGNORECASE
)

NO_INTERVIEW_REGEX = re.compile(
    r'\b(no interview|direct selection|direct joining|spot offer|guaranteed selection|immediate selection|no test required|selection on spot|direct placement|without interview|no exam)\b',
    re.IGNORECASE
)

PAYMENT_BEFORE_JOINING_REGEX = re.compile(
    r'\b(pay before|fee before|payment required before|deposit before|pay first|transfer money before|pay prior|pay before interview)\b',
    re.IGNORECASE
)

URGENCY_REGEX = re.compile(
    r'\b(limited slots|limited seats|apply within \d+ (hours|days)|immediate joining|urgently required|urgent hiring|hiring immediately|spot offer|guaranteed selection|act fast|last chance|urgent vacancy|apply today)\b',
    re.IGNORECASE
)

PERSONAL_DOCS_REGEX = re.compile(
    r'\b(aadhaar|pan card|bank account details|cancelled cheque|passbook|bank passbook|passport copy|share bank details|send aadhaar)\b',
    re.IGNORECASE
)

UNOFFICIAL_CONTACT_REGEX = re.compile(
    r'\b(whatsapp|telegram|gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|rediffmail\.com|yandex\.com|mail\.com|\+91\d{10}|\b\d{10}\b)\b',
    re.IGNORECASE
)

SPECIFIC_SALARY_REGEX = re.compile(
    r'(\u20b9|\$|rs\.?|inr)\s*\d+[\d,]*\s*(-|to)\s*(\u20b9|\$|rs\.?|inr)?\s*\d+[\d,]*|\b\d{2,3}k\s*(-|to)\s*\d{2,3}k\b|\b\d+[\d,]*\s*(per|/)\s*(month|annum|year|pm|lpa)\b',
    re.IGNORECASE
)

VAGUE_SALARY_REGEX = re.compile(
    r'\b(attractive salary|best in industry|handsome salary|competitive salary|negotiable|as per market standards|good pay)\b',
    re.IGNORECASE
)

SALARY_MISMATCH_REGEX = re.compile(
    r'\b(\d{4,6}\s*(per|/)\s*(day|hour|week)|50000\s*(per|/)\s*month for intern|100000\s*(per|/)\s*month for typing|data entry.*(?:10000|20000|50000|100000)|earn \d{4,6} (daily|weekly)|no experience.*(?:50000|100000|200000)|typing job.*(?:30000|50000|80000))\b',
    re.IGNORECASE
)

TITLE_DESC_MISMATCH_REGEX = re.compile(
    r'\b(manager|developer|architect|engineer|data scientist|consultant|lead)\b.*\b(data entry|typing|form filling|ad posting|copy paste|sms sending|captcha)\b',
    re.IGNORECASE
)

# Regional / Devanagari Hindi Script Regexes
HINDI_FEE_REGEX = re.compile(
    r'(शुल्क|रजिस्ट्रेशन|डिपॉजिट|फीस|पैसे जमा|पेमेंट|सुरक्षा राशि)',
    re.IGNORECASE
)

HINDI_URGENCY_REGEX = re.compile(
    r'(सीमित सीटें|तुरंत जॉइनिंग|अति आवश्यक|जल्दी करें|आज ही|तत्काल भर्ती)',
    re.IGNORECASE
)

HINDI_UNOFFICIAL_CONTACT_REGEX = re.compile(
    r'(व्हाट्सएप|टेलीग्राम|जीमेल|पर्सनल नंबर|कॉल करें)',
    re.IGNORECASE
)

ENGINEERED_FEATURE_NAMES = [
    'posting_length',
    'word_count',
    'exclamation_ratio',
    'caps_ratio',
    'has_company_profile',
    'requirements_count',
    'has_specific_salary',
    'fee_mentioned',
    'no_interview_required',
    'payment_before_joining',
    'urgency_language',
    'requests_personal_docs',
    'unofficial_contact',
    'salary_seniority_mismatch',
    'company_domain_mismatch',
    'title_desc_mismatch',
    'hindi_fee_mentioned',
    'hindi_urgency_language',
    'hindi_unofficial_contact',
    'domain_has_recent',
    'domain_has_typosquat',
    'domain_has_free_email'
]

def extract_features_from_text(text, company="", title="", company_profile=""):
    if not isinstance(text, str):
        text = ""
        
    text_len = len(text)
    words = text.split()
    word_cnt = len(words)
    
    # Structural features
    exclamation_cnt = text.count('!')
    exclamation_ratio = exclamation_cnt / max(1, word_cnt)
    
    caps_cnt = sum(1 for c in text if c.isupper())
    caps_ratio = caps_cnt / max(1, text_len)
    
    has_comp_prof = 1 if (isinstance(company_profile, str) and len(company_profile.strip()) > 15) or "about company" in text.lower() else 0
    
    req_bullets = text.count('•') + text.count('- ') + text.count('* ')
    req_keywords = len(re.findall(r'\b(requirement|qualification|skill|must have|eligibility|responsibility)\b', text, re.IGNORECASE))
    requirements_count = req_bullets + req_keywords
    
    has_spec_sal = 1 if SPECIFIC_SALARY_REGEX.search(text) else 0
    
    # Behavioral features
    fee_val = 1 if FEE_REGEX.search(text) else 0
    no_interview_val = 1 if NO_INTERVIEW_REGEX.search(text) else 0
    pay_before_val = 1 if PAYMENT_BEFORE_JOINING_REGEX.search(text) else 0
    urgency_val = 1 if URGENCY_REGEX.search(text) else 0
    personal_docs_val = 1 if PERSONAL_DOCS_REGEX.search(text) else 0
    unofficial_contact_val = 1 if UNOFFICIAL_CONTACT_REGEX.search(text) else 0
    
    # Consistency features
    salary_mismatch_val = 1 if SALARY_MISMATCH_REGEX.search(text) else 0
    full_combo = (title + " " + text).lower()
    title_desc_mismatch_val = 1 if TITLE_DESC_MISMATCH_REGEX.search(full_combo) else 0
    
    # Hindi features
    hindi_fee_val = 1 if HINDI_FEE_REGEX.search(text) else 0
    hindi_urgency_val = 1 if HINDI_URGENCY_REGEX.search(text) else 0
    hindi_unofficial_val = 1 if HINDI_UNOFFICIAL_CONTACT_REGEX.search(text) else 0
    
    # Domain / Reputation features
    dom_res = analyze_domains(text, claimed_company=company)
    dom_recent = dom_res['has_recent_domain']
    dom_typosquat = dom_res['has_typosquat']
    dom_free_email = dom_res['has_free_email']
    comp_domain_mismatch = dom_res['company_domain_mismatch']
    
    return {
        'posting_length': text_len,
        'word_count': word_cnt,
        'exclamation_ratio': exclamation_ratio,
        'caps_ratio': caps_ratio,
        'has_company_profile': has_comp_prof,
        'requirements_count': requirements_count,
        'has_specific_salary': has_spec_sal,
        'fee_mentioned': fee_val,
        'no_interview_required': no_interview_val,
        'payment_before_joining': pay_before_val,
        'urgency_language': urgency_val,
        'requests_personal_docs': personal_docs_val,
        'unofficial_contact': unofficial_contact_val,
        'salary_seniority_mismatch': salary_mismatch_val,
        'company_domain_mismatch': comp_domain_mismatch,
        'title_desc_mismatch': title_desc_mismatch_val,
        'hindi_fee_mentioned': hindi_fee_val,
        'hindi_urgency_language': hindi_urgency_val,
        'hindi_unofficial_contact': hindi_unofficial_val,
        'domain_has_recent': dom_recent,
        'domain_has_typosquat': dom_typosquat,
        'domain_has_free_email': dom_free_email
    }

def process_features(df):
    print("Extracting multi-group engineered features (structural, behavioral, consistency, regional, domain)...")
    
    def _row_extract(row):
        txt = str(row.get('raw_text', row.get('full_text', '')))
        comp = str(row.get('company_profile', ''))
        ttl = str(row.get('title', ''))
        return extract_features_from_text(txt, company=comp, title=ttl, company_profile=comp)
        
    features_list = df.apply(_row_extract, axis=1).tolist()
    features_df = pd.DataFrame(features_list)
    
    # Fill NAs
    features_df = features_df.fillna(0)
    
    return pd.concat([df, features_df], axis=1)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    cleaned_path = os.path.join(data_dir, "cleaned.csv")
    
    if not os.path.exists(cleaned_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_path}. Run clean.py first.")
        
    print(f"Loading cleaned dataset from {cleaned_path}...")
    df = pd.read_csv(cleaned_path)
    
    df_featured = process_features(df)
    
    output_path = os.path.join(data_dir, "featured.csv")
    df_featured.to_csv(output_path, index=False)
    print(f"Saved featured dataset to {output_path} with shape {df_featured.shape}.")
    print("\nFeature Summary (Means across dataset):")
    print(df_featured[ENGINEERED_FEATURE_NAMES].mean())

if __name__ == "__main__":
    main()
