
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_loader import load_data

# Function to create and store embeddings
def create_vector_store(url):
    documents = load_data(url)
    if not documents:
        print("No documents loaded, cannot create vector store.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    texts_content = [doc.page_content for doc in texts]

    # Wrap the SentenceTransformer model in HuggingFaceEmbeddings
    embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    
    vector_store = FAISS.from_texts(
        texts=texts_content,
        embedding=embedding
    )

    vector_store.save_local("app/vectorstore/brainlox_faiss")
    print("Vector store created and saved successfully!")

if __name__ == "__main__":
    url = "https://brainlox.com/courses/category/technical"
    # url = "https://www.merge.dev/blog/webhooks-vs-polling"
    create_vector_store(url)