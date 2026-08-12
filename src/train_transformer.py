import os
import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

MODEL_NAME = "distilbert-base-multilingual-cased"

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")
    transformer_dir = os.path.join(models_dir, "transformer")
    os.makedirs(transformer_dir, exist_ok=True)
    
    cleaned_path = os.path.join(data_dir, "cleaned.csv")
    if not os.path.exists(cleaned_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_path}. Run clean.py first.")
        
    print("Loading dataset for transformer fine-tuning...")
    df = pd.read_csv(cleaned_path)
    df['full_text'] = df['full_text'].fillna('')
    
    # Subsample if dataset is very large to ensure quick training in hackathon environment
    if len(df) > 5000:
        df = df.sample(n=5000, random_state=42).reset_index(drop=True)
        
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['fraudulent'])
    
    print(f"Loading tokenizer: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    def tokenize_function(examples):
        return tokenizer(examples["full_text"], truncation=True, max_length=256, padding="max_length")
        
    train_ds = Dataset.from_pandas(train_df[['full_text', 'fraudulent']].rename(columns={'fraudulent': 'label'}))
    val_ds = Dataset.from_pandas(val_df[['full_text', 'fraudulent']].rename(columns={'fraudulent': 'label'}))
    
    train_tokenized = train_ds.map(tokenize_function, batched=True)
    val_tokenized = val_ds.map(tokenize_function, batched=True)
    
    print("Loading pre-trained transformer model...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    
    training_args = TrainingArguments(
        output_dir=os.path.join(models_dir, "transformer_checkpoints"),
        num_train_epochs=2,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        learning_rate=3e-5,
        weight_decay=0.01,
        fp16=torch.cuda.is_available(),
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=val_tokenized,
        tokenizer=tokenizer,
    )
    
    print("Fine-tuning DistilBERT model...")
    trainer.train()
    
    print(f"Saving final transformer model to {transformer_dir}...")
    model.save_pretrained(transformer_dir)
    tokenizer.save_pretrained(transformer_dir)
    print("Transformer fine-tuning completed successfully!")

if __name__ == "__main__":
    main()
