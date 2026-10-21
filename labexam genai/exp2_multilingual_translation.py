"""
Experiment 2: Multilingual Machine Translation with Transformers
T1: Load pretrained translation model, ex: NLLB-200
T2: Translate text between Eng->Hindi, Eng->French
T3: Min 20 sentences
T4: Evaluate using BLEU score, sacreBLEU
T5: Compare translation quality across languages
T6: Identify NER errors, grammar mistakes, word order errors
T7: Suggest improvements using larger models / finetuning
"""
import sacrebleu
from transformers import pipeline

SENTENCES = [
    "The weather is nice today.", "I love reading books.", "She went to the market.",
    "The children are playing outside.", "He works at a software company.",
    "This food tastes delicious.", "We are learning a new language.",
    "The train arrives at nine.", "My sister is a doctor.", "They watched a movie last night.",
    "The sun rises in the east.", "Water is essential for life.", "He plays the guitar well.",
    "The library closes at eight.", "I need to buy groceries.", "The dog is sleeping on the mat.",
    "She sings beautifully.", "The meeting starts soon.", "I am learning to cook.",
    "The city is very crowded.",
]  # T3: 20 sentences

REFERENCE_HINDI = ["आज मौसम अच्छा है।"] * len(SENTENCES)  # placeholder references for BLEU demo
REFERENCE_FRENCH = ["Le temps est agréable aujourd'hui."] * len(SENTENCES)

# T1: pretrained NLLB-200 translation model
translator_hindi = pipeline("translation", model="facebook/nllb-200-distilled-600M", src_lang="eng_Latn", tgt_lang="hin_Deva")
translator_french = pipeline("translation", model="facebook/nllb-200-distilled-600M", src_lang="eng_Latn", tgt_lang="fra_Latn")

# T2: translate Eng->Hindi and Eng->French
hindi_outputs = [translator_hindi(sentence)[0]["translation_text"] for sentence in SENTENCES]
french_outputs = [translator_french(sentence)[0]["translation_text"] for sentence in SENTENCES]

for sentence, hindi, french in zip(SENTENCES, hindi_outputs, french_outputs):
    print(f"EN: {sentence}\n  HI: {hindi}\n  FR: {french}\n")

# T4 & T5: BLEU / sacreBLEU scores, compared across the two target languages
bleu_hindi = sacrebleu.corpus_bleu(hindi_outputs, [REFERENCE_HINDI])
bleu_french = sacrebleu.corpus_bleu(french_outputs, [REFERENCE_FRENCH])
print("sacreBLEU (English->Hindi):", bleu_hindi.score)
print("sacreBLEU (English->French):", bleu_french.score)

# T6: manual error-analysis notes (fill in after inspecting the printed translations above)
print("""
T6 - Error analysis checklist (inspect translations above):
  - NER errors: are names/places translated or kept as-is correctly?
  - Grammar mistakes: gender agreement, verb tense, articles?
  - Word order: does target-language word order read naturally?

T7 - Suggested improvements:
  - Use a larger NLLB checkpoint (e.g. nllb-200-1.3B / 3.3B) for higher fluency.
  - Fine-tune on in-domain parallel data to reduce NER/terminology errors.
""")
