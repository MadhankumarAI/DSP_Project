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
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

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

REFERENCE_HINDI = ["आ मौसम अच्छा है।"] * len(SENTENCES)  # placeholder references for BLEU demo
REFERENCE_FRENCH = ["Le temps est agréable aujourd'hui."] * len(SENTENCES)

# T1: pretrained NLLB-200 translation model (loaded once, reused for both languages)
model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang="eng_Latn")
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate(text, target_lang):
    inputs = tokenizer(text, return_tensors="pt")
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_lang)
    output_tokens = model.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=60)
    return tokenizer.decode(output_tokens[0], skip_special_tokens=True)

# T2: translate Eng->Hindi and Eng->French
hindi_outputs = [translate(sentence, "hin_Deva") for sentence in SENTENCES]
french_outputs = [translate(sentence, "fra_Latn") for sentence in SENTENCES]

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
