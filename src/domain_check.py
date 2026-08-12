import re
import urllib.parse
from datetime import datetime
from rapidfuzz import fuzz, distance

# Top 30 Indian companies, IT giants, and major job portals
TOP_INDIAN_DOMAINS = [
    "tcs", "infosys", "wipro", "hcl", "techmahindra", "accenture", "cognizant", 
    "amazon", "flipkart", "paytm", "swiggy", "zomato", "internshala", "naukri", 
    "foundit", "indeed", "linkedin", "tata", "reliance", "icicibank", "hdfcbank", 
    "sbi", "wns", "genpact", "capgemini", "ltimindtree", "persistent", "zoho", "deloitte", "myntra"
]

COMMON_FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com",
    "yandex.com", "mail.com", "icloud.com", "protonmail.com"
}

URL_REGEX = re.compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
    re.IGNORECASE
)

EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    re.IGNORECASE
)

def extract_urls_and_domains(text):
    if not isinstance(text, str):
        return [], []
    
    urls = URL_REGEX.findall(text)
    emails = EMAIL_REGEX.findall(text)
    
    domains = []
    
    for url in urls:
        try:
            parsed = urllib.parse.urlparse(url if url.startswith(('http://', 'https://')) else 'http://' + url)
            netloc = parsed.netloc.split(':')[0].lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            if netloc and netloc not in domains:
                domains.append(netloc)
        except Exception:
            pass
            
    for email_match in emails:
        domain = email_match.lower().strip()
        if domain and domain not in domains:
            domains.append(domain)
            
    return urls, domains

def check_typosquatting(domain_name):
    """
    Check if a domain name is a typosquat or suspicious variant of a top portal/company.
    Returns (is_typosquat, matched_target, similarity_score)
    """
    base_name = domain_name.split('.')[0].lower()
    
    # Remove common sub-slugs
    cleaned_base = re.sub(r'-(hiring|careers|jobs|portal|verify|interview|hr|recruitment|apply|india)', '', base_name)
    
    # If exact match to known legitimate company domain, it's not a typosquat
    if base_name in TOP_INDIAN_DOMAINS or cleaned_base in TOP_INDIAN_DOMAINS:
        return False, None, 0
        
    for target in TOP_INDIAN_DOMAINS:
        # Distance checks
        ratio = fuzz.ratio(cleaned_base, target)
        lev_dist = distance.Levenshtein.distance(cleaned_base, target)
        
        # Typosquat condition: high similarity but not exact match, or lev distance 1-2
        if (ratio >= 78 and ratio < 100) or (1 <= lev_dist <= 2 and len(target) >= 4):
            return True, target, ratio
            
    return False, None, 0

def check_domain_whois_age(domain_name):
    """
    Query WHOIS age for domain. Times out quickly if unreachable.
    Returns (age_days, creation_date_str, is_recent)
    """
    try:
        import whois
        w = whois.whois(domain_name)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            now = datetime.now()
            age_days = (now - creation_date).days
            date_str = creation_date.strftime("%Y-%m-%d")
            is_recent = age_days < 180
            return age_days, date_str, is_recent
    except Exception:
        pass
    return None, None, False

def analyze_domains(text, claimed_company=""):
    """
    Comprehensive domain check on posting text.
    Returns dict with domain risk features and human-readable flags.
    """
    urls, domains = extract_urls_and_domains(text)
    
    flags = []
    has_recent_domain = 0
    has_typosquat = 0
    has_free_email = 0
    company_domain_mismatch = 0
    
    if not domains:
        return {
            'domain_count': 0,
            'has_recent_domain': 0,
            'has_typosquat': 0,
            'has_free_email': 0,
            'company_domain_mismatch': 0,
            'flags': []
        }
        
    claimed_comp_clean = claimed_company.lower().strip() if claimed_company else ""
    
    for dom in domains:
        # Free email check
        if dom in COMMON_FREE_DOMAINS:
            has_free_email = 1
            flags.append(f"Uses public webmail domain '{dom}' instead of official corporate domain.")
            if claimed_comp_clean and claimed_comp_clean not in ["n/a", "unknown", ""]:
                company_domain_mismatch = 1
            continue
            
        # Typosquatting check
        is_typo, target, ratio = check_typosquatting(dom)
        if is_typo:
            has_typosquat = 1
            flags.append(f"Domain '{dom}' is a likely typosquat of official company/portal '{target}'.")
            
        # WHOIS age check
        age_days, date_str, is_recent = check_domain_whois_age(dom)
        if is_recent:
            has_recent_domain = 1
            flags.append(f"Domain '{dom}' was registered recently ({age_days} days ago on {date_str}).")
            
        # Company name match check
        if claimed_comp_clean and len(claimed_comp_clean) > 3:
            comp_base = re.sub(r'[^a-z0-9]', '', claimed_comp_clean)
            dom_base = re.sub(r'[^a-z0-9]', '', dom.split('.')[0])
            if comp_base not in dom_base and dom_base not in comp_base:
                # Check fuzzy similarity
                sim = fuzz.partial_ratio(comp_base, dom_base)
                if sim < 60 and dom not in COMMON_FREE_DOMAINS:
                    company_domain_mismatch = 1
                    flags.append(f"Claimed company '{claimed_company}' does not match domain name '{dom}'.")

    return {
        'domain_count': len(domains),
        'has_recent_domain': has_recent_domain,
        'has_typosquat': has_typosquat,
        'has_free_email': has_free_email,
        'company_domain_mismatch': company_domain_mismatch,
        'flags': flags
    }
