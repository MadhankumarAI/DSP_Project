"""
Lab Task 13: Multimodal LLM (Vision-Language RAG)
- Load a medical image dataset, use a pretrained vision-language model
- Convert each image into text
- Use RAG to have a collection of docs based on images
- Combine image context, user question & retrieved documents
- Generate answer with evidence docs
- Evaluate answer quality, retrieval performance & hallucination rate
"""
import glob
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, AutoModelForSeq2SeqLM, AutoTokenizer
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

IMAGE_FOLDER = "./images"  # put medical images here
QUESTIONS = ["What abnormality is visible?", "Is there any sign of infection?"]

# 1. Pretrained vision-language model -> convert each image into text (caption)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption_image(path):
    image = Image.open(path).convert("RGB")
    tokens = blip_model.generate(**blip_processor(image, return_tensors="pt"))
    return blip_processor.decode(tokens[0], skip_special_tokens=True)

docs = [Document(page_content=caption_image(p), metadata={"source": p}) for p in glob.glob(f"{IMAGE_FOLDER}/*")]

# 2. RAG: embed image captions & store in FAISS
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# flan-t5 loaded directly (pipeline("text2text-generation") is removed in this transformers version)
flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def generate(prompt):
    inputs = flan_tokenizer(prompt, return_tensors="pt", truncation=True)
    output_tokens = flan_model.generate(**inputs, max_new_tokens=64)
    return flan_tokenizer.decode(output_tokens[0], skip_special_tokens=True)

# 3-5. Combine image context + question + retrieved docs -> answer with evidence
for question in QUESTIONS:
    evidence = retriever.invoke(question)
    context = "\n".join(doc.page_content for doc in evidence)
    answer = generate(f"Context (image descriptions):\n{context}\n\nQuestion: {question}\nAnswer:")

    print(f"\nQ: {question}")
    print("Answer:", answer)
    print("Evidence docs (image source, caption):", [(d.metadata["source"], d.page_content) for d in evidence])
    # Evaluate: if the answer isn't grounded in any evidence caption, flag possible hallucination
    grounded = any(word in context.lower() for word in answer.lower().split() if len(word) > 4)
    print("Hallucination check:", "grounded in retrieved evidence" if grounded else "possible hallucination")
