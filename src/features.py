import os
import re
import pandas as pd
import numpy as np

try:
    from src.domain_check import analyze_domains
except ImportError:
    from domain_check import analyze_domains

# ----------------- REGEX PATTERNS -----------------

FEE_KEYWORD_REGEX = re.compile(
    r'\b(registration fee|security deposit|training fee|processing fee|gate fee|refundable deposit|pay inr|pay rs|payment required|enrollment fee|charges apply|deposit amount|pay before|fees apply|laptop deposit|id card fee|badge fee|fee deposit|admin fee|seat booking|training charges|verification charges|शुल्क|रजिस्ट्रेशन|डिपॉजिट|फीस|पैसे जमा|पेमेंट|सुरक्षा राशि)\b',
    re.IGNORECASE
)

PAYMENT_METHOD_REGEX = re.compile(
    r'\b(upi|gpay|google pay|phonepe|paytm|account number|account no|bank transfer|qr code|remit|deposit to|transfer money|wallet|net banking|scan and pay)\b',
    re.IGNORECASE
)

PAYMENT_INSTRUCTION_REGEX = re.compile(
    r'\b(pay to|transfer to|deposit to|send to|remit to|credited to|account holder|upi id|google pay|phonepe|paytm|qr code|bank transfer|advance payment)\b',
    re.IGNORECASE
)

URGENCY_KEYWORD_REGEX = re.compile(
    r'\b(limited slots|limited seats|apply within \d+ (hours|days)|immediate joining|urgently required|urgent hiring|hiring immediately|spot offer|guaranteed selection|act fast|last chance|urgent vacancy|apply today|same day selection|open until filled|सीमित सीटें|तुरंत जॉइनिंग|अति आवश्यक|जल्दी करें|आज ही|तत्काल भर्ती)\b',
    re.IGNORECASE
)

NO_INTERVIEW_REGEX = re.compile(
    r'\b(no interview|direct selection|direct joining|spot offer|guaranteed selection|immediate selection|no test required|selection on spot|direct placement|without interview|no exam)\b',
    re.IGNORECASE
)

PERSONAL_DOCS_REGEX = re.compile(
    r'\b(aadhaar|pan card|bank account details|cancelled cheque|passbook|bank passbook|passport copy|share bank details|send aadhaar)\b',
    re.IGNORECASE
)

SPECIFIC_SALARY_REGEX = re.compile(
    r'(\u20b9|\$|rs\.?|inr)\s*\d+[\d,]*\s*(-|to)\s*(\u20b9|\$|rs\.?|inr)?\s*\d+[\d,]*|\b\d{2,3}k\s*(-|to)\s*\d{2,3}k\b|\b\d+[\d,]*\s*(per|/)\s*(month|annum|year|pm|lpa)\b',
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

# ---------- NEW DETECTION PATTERNS ----------

TELEGRAM_WHATSAPP_REGEX = re.compile(
    r'(telegram|@\w+tasks?|@\w+jobs?|@\w+earn|wa\.me|t\.me|join\s+(our|the)\s+(telegram|whatsapp)\s+(channel|group)|whatsapp\s+(group|channel|pe\s+contact|pe\s+join)|contact\s+(on|via)\s+(telegram|whatsapp)|व्हाट्सएप|टेलीग्राम)',
    re.IGNORECASE
)

MLM_REFERRAL_REGEX = re.compile(
    r'\b(refer\s+\d+\s+people|referral\s+(bonus|commission|income)|earn\s+(per|from)\s+referral|build\s+your\s+(own\s+)?team|multi.?tier|network\s+marketing|passive\s+income|team\s+building\s+bonus|recruitment\s+commission|downline|upline|per\s+referral|unlimited\s+referral|affiliate\s+network|starter\s+kit|activation\s+fee)\b',
    re.IGNORECASE
)

CRYPTO_TRADING_REGEX = re.compile(
    r'\b(crypto|bitcoin|forex|trading\s+(analyst|platform|capital|signals?)|guaranteed\s+returns?|daily\s+returns?|invest(ment)?\s+(of|minimum|required)|trading\s+bot|trading\s+account|monthly\s+returns?\s+of\s+\d+%|minimum\s+investment|place\s+trades?)\b',
    re.IGNORECASE
)

GOVERNMENT_IMPERSONATION_REGEX = re.compile(
    r'\b(ssc\s+recruitment|railway\s+(recruitment|clerk)|government\s+(job|vacancy|recruitment)|sarkari\s+naukri|direct\s+appointment|special\s+(discretionary\s+)?quota|(?:7th|6th)\s+cpc|pay\s+scale|pension\s+benefit|permanent\s+government|indian\s+railway|staff\s+selection|postal\s+department|डाक\s+विभाग|भारतीय\s+डाक|सरकारी\s+नौकरी|सीधी\s+भर्ती|सीधी\s+नियुक्ति)\b',
    re.IGNORECASE
)

UNREALISTIC_DAILY_EARNING_REGEX = re.compile(
    r'(earn\s+rs\.?\s*\d{3,6}\s*(per|/)\s*day|daily\s+(income|earning|payment)\s+rs\.?\s*\d{3,6}|rs\.?\s*\d{3,6}\s*(daily|per\s+day)|kamao.*\d{4,6}|\d{3,6}\s*रोज़|रोज़.*\d{3,6}|per\s+day\s+guaranteed|daily\s+guaranteed)',
    re.IGNORECASE
)

EXPECTED_SALARY_BENCHMARKS = {
    'intern': 15000,
    'data entry': 18000,
    'typing': 15000,
    'fresher': 25000,
    'executive': 30000,
    'developer': 50000,
    'engineer': 50000,
    'manager': 80000,
    'lead': 90000,
}

NUMERIC_FEATURE_NAMES = [
    'fee_score',
    'urgency_score',
    'salary_ratio',
    'contact_score',
    'domain_age_days',
    'domain_age_missing',
    'has_domain_info',
    'structure_score',
    'exclamation_ratio',
    'caps_ratio',
    'posting_length',
    'word_count',
    'requirements_density',
    'communication_quality_score',
    'legitimate_structure_score',
    'red_flag_density'
]

BINARY_FLAG_NAMES = [
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
    'domain_has_free_email',
    'telegram_whatsapp_contact',
    'mlm_referral_language',
    'crypto_trading_scam',
    'government_impersonation',
    'unrealistic_daily_earning'
]

ENGINEERED_FEATURE_NAMES = NUMERIC_FEATURE_NAMES + BINARY_FLAG_NAMES
ALL_ENGINEERED_FEATURES = ENGINEERED_FEATURE_NAMES

def _safe_text(value):
    return value if isinstance(value, str) else ""

def _extract_salary_amounts(text):
    text = _safe_text(text)
    candidates = []

    for match in re.finditer(r'(?:rs\.?|inr|\u20b9|\$)\s*(\d[\d,]*(?:\.\d+)?)\s*(lpa|lakhs?|k|per month|pm|month|per annum|annum|year|per day|day|per hour|hour)?', text, re.IGNORECASE):
        amount = float(match.group(1).replace(',', ''))
        unit = (match.group(2) or '').lower()
        candidates.append((amount, unit))

    for match in re.finditer(r'(\d[\d,]*(?:\.\d+)?)\s*(lpa|lakhs?|k|per month|pm|month|per annum|annum|year|per day|day|per hour|hour)', text, re.IGNORECASE):
        amount = float(match.group(1).replace(',', ''))
        unit = (match.group(2) or '').lower()
        candidates.append((amount, unit))

    converted = []
    for amount, unit in candidates:
        if 'lpa' in unit or 'lakh' in unit:
            monthly = (amount * 100000.0) / 12.0
        elif unit == 'k':
            monthly = amount * 1000.0
        elif 'per annum' in unit or unit == 'annum' or unit == 'year':
            monthly = amount / 12.0
        elif 'per day' in unit or unit == 'day':
            monthly = amount * 26.0
        elif 'per hour' in unit or unit == 'hour':
            monthly = amount * 160.0
        else:
            monthly = amount
        converted.append(monthly)

    return converted

def calculate_fee_score(text):
    text = _safe_text(text)
    fee_matches = list(FEE_KEYWORD_REGEX.finditer(text))
    if not fee_matches:
        return 0.0
    base_score = 0.0
    lower_text = text.lower()
    for match in fee_matches:
        base_score += 1.0
        window_start = max(0, match.start() - 90)
        window_end = min(len(lower_text), match.end() + 90)
        window = lower_text[window_start:window_end]
        if PAYMENT_METHOD_REGEX.search(window):
            base_score += 1.5
        if PAYMENT_INSTRUCTION_REGEX.search(window):
            base_score += 1.0
    base_score += min(2.0, len(PAYMENT_METHOD_REGEX.findall(text)) * 0.4)
    return float(np.clip(base_score, 0.0, 10.0))

def calculate_urgency_score(text, word_cnt):
    text = _safe_text(text)
    urgency_matches = URGENCY_KEYWORD_REGEX.findall(text)
    match_cnt = len(urgency_matches)
    if word_cnt == 0 or match_cnt == 0:
        return 0.0
    density = (match_cnt / max(1.0, word_cnt / 100.0))
    return float(np.clip(density, 0.0, 10.0))

def calculate_salary_ratio(text, title=""):
    text = _safe_text(text)
    combined_text = (title + " " + text).lower()
    expected = 30000
    for role, bench in EXPECTED_SALARY_BENCHMARKS.items():
        if role in combined_text:
            expected = bench
            break

    candidates = _extract_salary_amounts(text)
    if not candidates:
        return -1.0

    extracted_val = max(candidates)
    ratio = extracted_val / float(expected)
    return float(np.clip(ratio, 0.0, 10.0))

def calculate_contact_score(text, company=""):
    text_lower = _safe_text(text).lower()
    email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text_lower)
    free_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com", "protonmail.com", "icloud.com", "mail.com"}
    has_free_email = any(domain in free_domains for domain in email_matches)
    has_corp_email = bool(email_matches) and not has_free_email
    has_phone = bool(re.search(r'(\+?91[\s-]?)?[6-9]\d{9}', text_lower))
    has_whatsapp = 'whatsapp' in text_lower or 'wa.me' in text_lower

    if has_corp_email:
        return 0.0
    if has_free_email:
        return 0.5
    if has_phone or has_whatsapp:
        return 1.0
    return 0.2

def calculate_domain_signal(text, claimed_company=""):
    dom_res = analyze_domains(text, claimed_company=claimed_company)
    domain_age_days = dom_res.get('domain_age_days', -1.0)
    domain_age_missing = dom_res.get('domain_age_missing', 1)
    has_domain_info = 1.0 if dom_res.get('domain_count', 0) > 0 else 0.0
    return dom_res, float(domain_age_days if domain_age_days is not None else -1.0), float(domain_age_missing), float(has_domain_info)

def calculate_structure_score(text, title="", company_profile=""):
    text = _safe_text(text)
    title = _safe_text(title)
    company_profile = _safe_text(company_profile)
    word_cnt = len(text.split())
    length_component = np.clip(word_cnt / 220.0, 0.0, 1.0)
    has_reqs = 1.0 if re.search(r'\b(requirement|requirements|qualification|qualifications|skill|skills|eligibility|responsibility|responsibilities)\b', text, re.IGNORECASE) else 0.0
    has_detail_section = 1.0 if re.search(r'(^|\n)\s*[-*•]\s+', text) else 0.0
    title_words = {w for w in re.findall(r'[a-zA-Z]+', title.lower()) if len(w) > 2}
    text_words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    duty_words = set(re.findall(r'(developer|engineer|manager|analyst|writer|support|sales|design|designer|tester|qa|hr|finance|accountant|operations|marketing|coordinator|assistant|executive|specialist)', text.lower()))
    title_match = (len(title_words.intersection(text_words.union(duty_words))) / max(1, len(title_words))) if title_words else 0.3
    company_detail = 1.0 if len(company_profile.strip()) > 20 else 0.0
    requirement_density = len(re.findall(r'\b(requirement|qualification|skill|eligibility|responsibility)\b', text, re.IGNORECASE)) / max(1.0, word_cnt / 100.0)
    detail_component = np.clip((requirement_density / 4.0) + (has_detail_section * 0.3), 0.0, 1.0)
    composite = (length_component * 0.25) + (has_reqs * 0.25) + (detail_component * 0.25) + (title_match * 0.15) + (company_detail * 0.10)
    return float(composite)

def calculate_communication_quality(text):
    """Score communication quality — lower = worse writing = more suspicious."""
    text = _safe_text(text)
    if not text:
        return 0.5
    words = text.split()
    word_cnt = len(words)
    if word_cnt == 0:
        return 0.5
    
    # Excessive caps ratio (scams tend to shout)
    caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
    caps_word_ratio = caps_words / max(1, word_cnt)
    
    # Excessive exclamation/question marks
    excl_cnt = text.count('!') + text.count('!!') + text.count('???')
    excl_ratio = excl_cnt / max(1, word_cnt)
    
    # Repeated punctuation (e.g., "!!!!!", "????")
    repeated_punct = len(re.findall(r'[!?]{2,}', text))
    
    # Very short sentences (fragmented writing)
    sentences = re.split(r'[.!?]+', text)
    short_sentences = sum(1 for s in sentences if 0 < len(s.split()) < 4)
    short_ratio = short_sentences / max(1, len(sentences))
    
    # Emoji/special char density (scam postings use more)
    special_chars = len(re.findall(r'[★☆✓✔✗✘⚡🔥💰🎯💼]', text))
    
    quality = 1.0
    quality -= min(0.3, caps_word_ratio * 2)
    quality -= min(0.2, excl_ratio * 3)
    quality -= min(0.15, repeated_punct * 0.05)
    quality -= min(0.15, short_ratio * 0.5)
    quality -= min(0.1, special_chars * 0.02)
    
    return float(np.clip(quality, 0.0, 1.0))


def calculate_legitimate_structure(text, title="", company_profile=""):
    """Score how well the posting follows legitimate job posting structure."""
    text = _safe_text(text)
    title = _safe_text(title)
    company_profile = _safe_text(company_profile)
    lower = text.lower()
    
    signals = 0.0
    max_signals = 10.0
    
    # Has proper section headings
    if re.search(r'(about\s+(us|the\s+company)|company\s+(overview|profile|description))', lower):
        signals += 1.0
    if re.search(r'(job\s+description|role\s+description|key\s+responsibilities|responsibilities)', lower):
        signals += 1.0
    if re.search(r'(requirements?|qualifications?|what\s+we.*(look|need)|eligibility)', lower):
        signals += 1.0
    if re.search(r'(benefits?|perks?|what\s+we\s+offer|compensation)', lower):
        signals += 1.0
    if re.search(r'(how\s+to\s+apply|application\s+process|apply\s+(at|on|via|through))', lower):
        signals += 1.0
    
    # Has bullet points or structured lists
    if re.search(r'(^|\n)\s*[-*•●▸]\s+', text):
        signals += 1.0
    
    # Mentions specific technologies, tools, or skills (not vague)
    tech_mentions = len(re.findall(r'\b(python|java|sql|excel|react|angular|aws|gcp|azure|kubernetes|docker|jira|salesforce|sap|tableau|power bi|figma|photoshop)\b', lower))
    if tech_mentions >= 2:
        signals += 1.0
    
    # Has a proper company profile/description
    if len(company_profile.strip()) > 40:
        signals += 1.0
    
    # No fee/deposit mentioned anywhere
    if not FEE_KEYWORD_REGEX.search(text):
        signals += 0.5
    
    # Uses corporate email domain (not gmail/yahoo)
    corp_emails = re.findall(r'[a-zA-Z0-9._%+-]+@(?!gmail|yahoo|hotmail|outlook|rediffmail)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', lower)
    if corp_emails:
        signals += 0.5
    
    return float(np.clip(signals / max_signals, 0.0, 1.0))


def calculate_red_flag_density(binary_flags_dict):
    """Calculate how concentrated the red flags are — more flags = exponentially more suspicious."""
    flag_count = sum(1 for v in binary_flags_dict.values() if v == 1)
    total_flags = max(1, len(binary_flags_dict))
    # Non-linear scaling: 1 flag is mildly suspicious, 5+ is extremely suspicious
    raw_density = flag_count / total_flags
    amplified = raw_density * (1 + flag_count * 0.15)
    return float(np.clip(amplified, 0.0, 1.0))


def extract_features_from_text(text, company="", title="", company_profile=""):
    text = _safe_text(text)
    company = _safe_text(company)
    title = _safe_text(title)
    company_profile = _safe_text(company_profile)

    text_len = len(text)
    words = text.split()
    word_cnt = len(words)
    
    exclamation_cnt = text.count('!')
    exclamation_ratio = exclamation_cnt / max(1, word_cnt)
    caps_cnt = sum(1 for c in text if c.isupper())
    caps_ratio = caps_cnt / max(1, text_len)
    
    fee_score = calculate_fee_score(text)
    urgency_score = calculate_urgency_score(text, word_cnt)
    salary_ratio = calculate_salary_ratio(text, title=title)
    contact_score = calculate_contact_score(text, company=company)
    structure_score = calculate_structure_score(text, title=title, company_profile=company_profile)
    
    dom_res, domain_age, domain_age_missing, has_dom_info = calculate_domain_signal(text, claimed_company=company)

    req_bullets = text.count('•') + text.count('- ') + text.count('* ')
    req_keywords = len(re.findall(r'\b(requirement|qualification|skill|eligibility|responsibility)\b', text, re.IGNORECASE))
    req_density = (req_bullets + req_keywords) / max(1.0, word_cnt / 100.0)

    binary_flags = {
        'fee_mentioned': 1 if fee_score > 0 else 0,
        'no_interview_required': 1 if NO_INTERVIEW_REGEX.search(text) else 0,
        'payment_before_joining': 1 if re.search(r'\b(pay before|fee before|deposit before|pay (to|via)|transfer.*(fee|deposit|charge)|deposit.*before|advance payment)\b', text, re.IGNORECASE) else 0,
        'urgency_language': 1 if urgency_score > 0 else 0,
        'requests_personal_docs': 1 if PERSONAL_DOCS_REGEX.search(text) else 0,
        'unofficial_contact': 1 if contact_score >= 0.5 else 0,
        'salary_seniority_mismatch': 1 if SALARY_MISMATCH_REGEX.search(text) or (salary_ratio > 3.0) else 0,
        'company_domain_mismatch': 1 if dom_res.get('company_domain_mismatch', 0) else 0,
        'title_desc_mismatch': 1 if TITLE_DESC_MISMATCH_REGEX.search((title + " " + text).lower()) else 0,
        'hindi_fee_mentioned': 1 if re.search(r'(शुल्क|रजिस्ट्रेशन|डिपॉजिट|फीस|पैसे जमा|सुरक्षा राशि)', text) else 0,
        'hindi_urgency_language': 1 if re.search(r'(सीमित सीटें|तुरंत जॉइनिंग|अति आवश्यक|तत्काल भर्ती)', text) else 0,
        'hindi_unofficial_contact': 1 if re.search(r'(व्हाट्सएप|टेलीग्राम|जीमेल)', text) else 0,
        'domain_has_recent': 1 if dom_res.get('has_recent_domain', 0) else 0,
        'domain_has_typosquat': 1 if dom_res.get('has_typosquat', 0) else 0,
        'domain_has_free_email': 1 if dom_res.get('has_free_email', 0) else 0,
        'telegram_whatsapp_contact': 1 if TELEGRAM_WHATSAPP_REGEX.search(text) else 0,
        'mlm_referral_language': 1 if MLM_REFERRAL_REGEX.search(text) else 0,
        'crypto_trading_scam': 1 if CRYPTO_TRADING_REGEX.search(text) else 0,
        'government_impersonation': 1 if (GOVERNMENT_IMPERSONATION_REGEX.search(text) and (fee_score > 0 or contact_score >= 0.5)) else 0,
        'unrealistic_daily_earning': 1 if UNREALISTIC_DAILY_EARNING_REGEX.search(text) else 0
    }

    # New numeric features
    comm_quality = calculate_communication_quality(text)
    legit_structure = calculate_legitimate_structure(text, title=title, company_profile=company_profile)
    red_flag_dens = calculate_red_flag_density(binary_flags)

    numeric_features = {
        'fee_score': fee_score,
        'urgency_score': urgency_score,
        'salary_ratio': salary_ratio,
        'contact_score': contact_score,
        'domain_age_days': domain_age,
        'domain_age_missing': domain_age_missing,
        'has_domain_info': has_dom_info,
        'structure_score': structure_score,
        'exclamation_ratio': exclamation_ratio,
        'caps_ratio': caps_ratio,
        'posting_length': text_len,
        'word_count': word_cnt,
        'requirements_density': req_density,
        'communication_quality_score': comm_quality,
        'legitimate_structure_score': legit_structure,
        'red_flag_density': red_flag_dens
    }

    return {**numeric_features, **binary_flags}

def process_features(df):
    print("Extracting fast continuous numeric & parallel binary features...")
    def _row_extract(row):
        txt = str(row.get('raw_text', row.get('full_text', '')))
        comp = str(row.get('company_profile', ''))
        ttl = str(row.get('title', ''))
        return extract_features_from_text(txt, company=comp, title=ttl, company_profile=comp)
        
    features_list = df.apply(_row_extract, axis=1).tolist()
    features_df = pd.DataFrame(features_list)
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

if __name__ == "__main__":
    main()
