
import re, string, numpy as np, faiss
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 1. Load dataset and models
data = load_dataset("hotpotqa/hotpot_qa", "distractor",
                    split="validation[:10]")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def answer(context, question):
    inputs = tokenizer(f"Context: {context}\nQuestion: {question}\nAnswer:",
                       return_tensors="pt", truncation=True)
    out = model.generate(**inputs, max_new_tokens=40)
    return tokenizer.decode(out[0], skip_special_tokens=True)

def score(pred, gold):
    clean = lambda s: re.sub(r"\W+", " ", s.lower()).split()
    p, g = clean(pred), clean(gold)
    em = int(" ".join(p) == " ".join(g))
    common = sum(min(p.count(w), g.count(w)) for w in set(p))
    f1 = 2*common/(len(p)+len(g)) if p or g else 1.0
    return em, f1

single_scores, multi_scores = [], []

# 2. Retrieve, answer and evaluate
for item in data:
    q, gold = item["question"], item["answer"]
    docs = [s for group in item["context"]["sentences"] for s in group]

    vectors = np.asarray(embedder.encode(docs), dtype="float32")
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    # Hop 1
    _, ids = index.search(np.asarray(embedder.encode([q]), dtype="float32"), 1)
    d1 = docs[ids[0][0]]
    a1 = answer(d1, q)

    # Hop 2: use the first retrieved sentence to expand the query
    q2 = q + " " + d1
    _, ids2 = index.search(np.asarray(embedder.encode([q2]), dtype="float32"), 1)
    d2 = docs[ids2[0][0]]
    a2 = answer(d1 + " " + d2, q)

    single_scores.append(score(a1, gold))
    multi_scores.append(score(a2, gold))

    print(f"\nQ: {q}\nGold: {gold}\n1-hop: {a1}\n2-hop: {a2}")

# 3. Compare EM and F1
for name, scores in [("Single-hop", single_scores),
                     ("Two-hop", multi_scores)]:
    print(f"\n{name}: EM={np.mean([s[0] for s in scores]):.3f}, "
          f"F1={np.mean([s[1] for s in scores]):.3f}")
