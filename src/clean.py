import os
import re
import html
import pandas as pd

def clean_text_preserve_case(text):
    if not isinstance(text, str):
        return ""
    # Unescape HTML entities
    text = html.unescape(text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_text(text):
    text = clean_text_preserve_case(text)
    return text.lower()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    emscad_path = os.path.join(data_dir, "fake_job_postings.csv")
    indian_path = os.path.join(data_dir, "indian_job_fraud.csv")
    
    print("Loading datasets...")
    df_emscad = pd.read_csv(emscad_path)
    df_indian = pd.read_csv(indian_path)
    
    print(f"EMSCAD shape: {df_emscad.shape}")
    print(f"Indian shape: {df_indian.shape}")
    
    # Align EMSCAD schema
    df_emscad_clean = pd.DataFrame()
    df_emscad_clean['title'] = df_emscad['title'].fillna('')
    df_emscad_clean['company_profile'] = df_emscad['company_profile'].fillna('')
    df_emscad_clean['description'] = df_emscad['description'].fillna('')
    df_emscad_clean['requirements'] = df_emscad['requirements'].fillna('')
    df_emscad_clean['fraudulent'] = pd.to_numeric(df_emscad['fraudulent'], errors='coerce').fillna(0).astype(int)
    
    # Align Indian dataset schema
    df_indian_clean = pd.DataFrame()
    df_indian_clean['title'] = df_indian['title'].fillna('')
    df_indian_clean['company_profile'] = df_indian['company'].fillna('') if 'company' in df_indian.columns else ''
    df_indian_clean['description'] = df_indian['description'].fillna('')
    
    reqs = df_indian['requirements'].fillna('')
    if 'contact' in df_indian.columns:
        contacts = df_indian['contact'].fillna('')
        df_indian_clean['requirements'] = reqs + " " + contacts
    else:
        df_indian_clean['requirements'] = reqs
        
    if 'label' in df_indian.columns:
        label_col = df_indian['label']
        if label_col.dtype == object:
            df_indian_clean['fraudulent'] = label_col.astype(str).str.lower().apply(
                lambda x: 1 if x in ['1', 'fake', 'scam', 'fraudulent', 'true'] else 0
            )
        else:
            df_indian_clean['fraudulent'] = pd.to_numeric(label_col, errors='coerce').fillna(0).astype(int)
    elif 'fraudulent' in df_indian.columns:
        df_indian_clean['fraudulent'] = pd.to_numeric(df_indian['fraudulent'], errors='coerce').fillna(0).astype(int)
    else:
        df_indian_clean['fraudulent'] = 0

    merged_df = pd.concat([df_emscad_clean, df_indian_clean], ignore_index=True)
    
    # Create raw_text preserving case/punctuation for structural feature extraction
    merged_df['raw_text'] = (
        merged_df['title'] + " " +
        merged_df['company_profile'] + " " +
        merged_df['description'] + " " +
        merged_df['requirements']
    ).apply(clean_text_preserve_case)

    # Clean lowercased text for TF-IDF / NLP
    merged_df['full_text'] = merged_df['raw_text'].apply(clean_text)
    
    # Filter out empty full_text rows
    merged_df = merged_df[merged_df['full_text'].str.len() > 10].reset_index(drop=True)
    
    output_path = os.path.join(data_dir, "cleaned.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"Saved cleaned dataset to {output_path} with {len(merged_df)} rows.")
    print(f"Class distribution:\n{merged_df['fraudulent'].value_counts()}")

if __name__ == "__main__":
    main()
