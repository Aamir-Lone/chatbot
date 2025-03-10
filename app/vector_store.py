from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

vector_store_path = "app/vectorstore/brainlox_faiss"

def create_vector_store(source, source_type):
    documents = []

    if source_type == "url":
        loader = WebBaseLoader(source)
        documents = loader.load()

    if not documents:
        raise ValueError("No documents loaded from the source")
    
    elif source_type == "pdf":
        try:
            from io import BytesIO
            reader = PdfReader(BytesIO(source))
            for page in reader.pages:
                if page and page.extract_text():
                    documents.append(page.extract_text())
        except Exception as e:
            raise Exception(f"Failed to read PDF data. Error: {str(e)}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    vector_store = FAISS.from_documents(texts, embedding)
    vector_store.save_local(vector_store_path)

    print(f"Vector store created with {len(texts)} documents and saved to {vector_store_path}")
