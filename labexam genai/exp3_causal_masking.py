"""
Experiment 3: Implement Causal Masking for test sentences
Sentence: "The cat sat on the mask"
T1: Attention matrix before masking
T2: Attention matrix after masking
T3: Explain the difference
"""
import numpy as np

sentence = "The cat sat on the mask".split()
num_tokens = len(sentence)

# Fake query/key vectors just to produce a score matrix for the demo
np.random.seed(0)
query = np.random.rand(num_tokens, 4)
key = np.random.rand(num_tokens, 4)
scores = query @ key.T / np.sqrt(4)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

# T1: attention matrix BEFORE masking (every token can see every other token)
attention_before = softmax(scores)

# T2: attention matrix AFTER causal masking (token i can only see tokens <= i)
causal_mask = np.triu(np.ones((num_tokens, num_tokens)), k=1) * -1e9  # upper triangle -> -inf
attention_after = softmax(scores + causal_mask)

np.set_printoptions(precision=2, suppress=True)
print("Tokens:", sentence)
print("\nAttention BEFORE masking:\n", attention_before)
print("\nAttention AFTER causal masking:\n", attention_after)

# T3: explanation
print("""
T3 - Difference:
Before masking, every token's attention row has non-zero weight on ALL tokens,
including future tokens (look-ahead), which is not allowed in autoregressive
generation. After causal masking, the upper triangle is forced to ~0 so each
token i only attends to tokens 0..i (itself and the past) - this is what lets
a decoder generate text left-to-right without "cheating" by seeing the future.
""")
