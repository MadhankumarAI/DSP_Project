"""
Experiment 1: Abstractive Text Summarization
1. Load a pretrained model (facebook / google)
2. Use a dataset such as CNN/DailyMail or BBC
3. Generate summaries for at least 20 docs
4. Compare generated summaries with reference summaries
5. Evaluate using ROUGE-1, ROUGE-2, ROUGE-L
"""
from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from rouge_score import rouge_scorer

NUM_DOCS = 20

# 1. Pretrained abstractive summarization model (Facebook's BART).
# Loaded directly via tokenizer/model (not pipeline("summarization")/pipeline(
# "text-generation")) - pipeline task names keep changing across transformers
# versions, and "text-generation" expects a causal LM, not BART's seq2seq model.
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    output_tokens = model.generate(**inputs, max_length=120, min_length=30)
    return tokenizer.decode(output_tokens[0], skip_special_tokens=True)

# 2. Dataset: CNN/DailyMail (articles + reference "highlights" summaries)
dataset = load_dataset("abisee/cnn_dailymail", "3.0.0", split=f"test[:{NUM_DOCS}]")

scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
totals = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

# 3-5. Generate summaries, compare with references, accumulate ROUGE scores
for i, article in enumerate(dataset):
    reference_summary = article["highlights"]
    generated_summary = summarize(article["article"])

    scores = scorer.score(reference_summary, generated_summary)
    for metric in totals:
        totals[metric] += scores[metric].fmeasure

    print(f"\n--- Document {i + 1} ---")
    print("Generated:", generated_summary)
    print("Reference:", reference_summary)

print("\n=== Average ROUGE scores over", NUM_DOCS, "documents ===")
for metric, total in totals.items():
    print(f"{metric}: {total / NUM_DOCS:.4f}")
