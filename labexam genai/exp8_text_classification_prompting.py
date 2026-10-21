"""
Experiment 8: Text Classification via Prompting
AG News - World, Sports, Business, Sci/Tech -> classify article
i) Zero-shot, few-shot, role-based chain-of-thought & structured
   output prompting using accuracy, precision, recall, F1-score
"""
from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sklearn.metrics import classification_report

NUM_SAMPLES = 20
LABELS = ["World", "Sports", "Business", "Sci/Tech"]

# flan-t5 loaded directly (not via pipeline() - the "text2text-generation" task
# and its pipeline class were removed in this transformers version)
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def generate(prompt, max_new_tokens=30):
    inputs = flan_tokenizer(prompt, return_tensors="pt", truncation=True)
    output_tokens = flan_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return flan_tokenizer.decode(output_tokens[0], skip_special_tokens=True)

dataset = load_dataset("fancyzhx/ag_news", split=f"test[:{NUM_SAMPLES}]")
articles = dataset["text"]
gold_labels = [LABELS[i] for i in dataset["label"]]

FEW_SHOT_EXAMPLES = """Example 1: "The team won the championship game." -> Sports
Example 2: "The central bank raised interest rates." -> Business
Example 3: "A new exoplanet was discovered by astronomers." -> Sci/Tech
Example 4: "Leaders met to discuss the peace treaty." -> World
"""

PROMPTS = {
    "zero_shot": lambda article: f"Classify this news article into one of {LABELS}: \"{article}\"\nCategory:",
    "few_shot": lambda article: f"{FEW_SHOT_EXAMPLES}\nNow classify: \"{article}\"\nCategory:",
    "role_cot": lambda article: (
        f"You are an expert news editor. Think step by step about the topic, then classify "
        f"this article into one of {LABELS}.\nArticle: \"{article}\"\nReasoning and final category:"
    ),
    "structured_output": lambda article: (
        f"Classify the article below. Respond ONLY in the format Category: <label>, "
        f"where <label> is one of {LABELS}.\nArticle: \"{article}\"\nCategory:"
    ),
}

def extract_label(generated_text):
    match = next((label for label in LABELS if label.lower() in generated_text.lower()), None)
    return match or "Unknown"

for strategy_name, build_prompt in PROMPTS.items():
    predictions = []
    for article in articles:
        output_text = generate(build_prompt(article))
        predictions.append(extract_label(output_text))

    print(f"\n=== Prompting strategy: {strategy_name} ===")
    print(classification_report(gold_labels, predictions, labels=LABELS, zero_division=0))
