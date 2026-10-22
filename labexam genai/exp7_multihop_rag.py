"""
Experiment 7: Multihop RAG
i) Load HotpotQA dataset, extract questions & support documents
ii) Generate embeddings of sentence transformers & store in FAISS
iii) Retrieve most relevant docs for HOP1, create second query using
     info from HOP1
iv) Combine both retrieved docs & send to LLM to generate final
    answer. Compare single-hop & 2-hop RAG with exact match & F1-score
"""
import re
import string
import numpy as np
import faiss
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

NUM_QUESTIONS = 10
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# flan-t5 loaded directly (not via pipeline() - the "text2text-generation" task
# and its pipeline class were removed in this transformers version)
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def generate(prompt):
    inputs = flan_tokenizer(prompt, return_tensors="pt", truncation=True)
    output_tokens = flan_model.generate(**inputs, max_new_tokens=64)
    return flan_tokenizer.decode(output_tokens[0], skip_special_tokens=True)

# i) Load HotpotQA, extract questions + support (context) documents
dataset = load_dataset("hotpotqa/hotpot_qa", "distractor", split=f"validation[:{NUM_QUESTIONS}]", trust_remote_code=True)

def normalize(text):
    text = text.lower()
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    return " ".join(text.split())

def exact_match(prediction, gold):
    return int(normalize(prediction) == normalize(gold))

def f1_score(prediction, gold):
    pred_tokens, gold_tokens = normalize(prediction).split(), normalize(gold).split()
    common = set(pred_tokens) & set(gold_tokens)
    if not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)

single_hop_scores, multi_hop_scores = [], []

for item in dataset:
    question, gold_answer = item["question"], item["answer"]
    sentences = [s for group in item["context"]["sentences"] for s in group]  # flatten all support sentences

    # ii) Embed all sentences for this question & store in a FAISS index
    sentence_vectors = embedder.encode(sentences)
    index = faiss.IndexFlatL2(sentence_vectors.shape[1])
    index.add(np.array(sentence_vectors))

    # iii) HOP1: retrieve top doc for the original question
    query_vector = embedder.encode([question])
    _, hop1_idx = index.search(np.array(query_vector), 1)
    hop1_doc = sentences[hop1_idx[0][0]]

    # single-hop RAG answer (context = HOP1 doc only)
    single_hop_answer = generate(f"Context: {hop1_doc}\nQuestion: {question}\nAnswer:")

    # second query built from HOP1 info, retrieve HOP2 doc
    hop2_query = f"{question} {hop1_doc}"
    hop2_vector = embedder.encode([hop2_query])
    _, hop2_idx = index.search(np.array(hop2_vector), 1)
    hop2_doc = sentences[hop2_idx[0][0]]

    # iv) combine both retrieved docs, generate final (2-hop) answer
    combined_context = hop1_doc + " " + hop2_doc
    multi_hop_answer = generate(f"Context: {combined_context}\nQuestion: {question}\nAnswer:")

    single_hop_scores.append((exact_match(single_hop_answer, gold_answer), f1_score(single_hop_answer, gold_answer)))
    multi_hop_scores.append((exact_match(multi_hop_answer, gold_answer), f1_score(multi_hop_answer, gold_answer)))
    print(f"\nQ: {question}\nGold: {gold_answer}\n1-hop: {single_hop_answer}\n2-hop: {multi_hop_answer}")

avg = lambda scores, i: sum(s[i] for s in scores) / len(scores)
print("\n=== Single-hop RAG === EM:", avg(single_hop_scores, 0), "F1:", avg(single_hop_scores, 1))
print("=== 2-hop RAG       === EM:", avg(multi_hop_scores, 0), "F1:", avg(multi_hop_scores, 1))
