"""
Experiment 6: RAG over PDFs with LangChain
1) Load research PDFs using LangChain. Generate embeddings using
   HuggingFace. Store embeddings in Chroma / FAISS
2) Create retriever using similarity search. Build LangChain RAG using
   i) Retriever  ii) Prompt template  iii) LLM  iv) Output parser
3) Return answer along with source document & page number
4) Evaluate system on atleast 10 questions & compare retrieved docs
   with k = 3, 5, 10
"""
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

PDF_FOLDER = "./pdfs"          # put research PDFs here
QUESTIONS = [
    "What is the main contribution of the paper?", "What dataset was used?",
    "What evaluation metric was used?", "What is the proposed method called?",
    "What are the limitations mentioned?", "What future work is suggested?",
    "What baseline models were compared?", "What problem does the paper solve?",
    "What architecture is used?", "What are the key results?",
]  # at least 10 questions

# 1. Load PDFs, split into chunks, embed with HuggingFace, store in FAISS
pages = []
for pdf_path in glob.glob(f"{PDF_FOLDER}/*.pdf"):
    pages.extend(PyPDFLoader(pdf_path).load())  # each page keeps its page_number + source metadata

chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(pages)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 2. RAG chain: retriever -> prompt template -> LLM -> output parser
llm = HuggingFacePipeline.from_model_id(model_id="google/flan-t5-base", task="text2text-generation")
prompt = ChatPromptTemplate.from_template(
    "Answer the question using only the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def answer_with_sources(question, k=3):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever.invoke(question)
    chain = {"context": lambda _: format_docs(retrieved_docs), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    answer = chain.invoke(question)
    sources = [(doc.metadata.get("source"), doc.metadata.get("page")) for doc in retrieved_docs]
    return answer, sources

# 4. Evaluate on all questions, comparing retrieval at k = 3, 5, 10
for question in QUESTIONS:
    print(f"\nQ: {question}")
    for k in (3, 5, 10):
        answer, sources = answer_with_sources(question, k=k)
        print(f"  [k={k}] Answer: {answer}\n         Sources (file, page): {sources}")
