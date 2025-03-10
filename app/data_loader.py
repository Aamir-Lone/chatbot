import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader

def load_data(source, source_type="url"):
    documents = []

    if source_type == "url":
        response = requests.get(source, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            texts = soup.get_text(separator=" ")
            documents.append(texts)
        else:
            print(f"Failed to fetch URL: {source}")

    elif source_type == "pdf":
        try:
            reader = PdfReader(source)
            for page in reader.pages:
                if page and page.extract_text():
                    documents.append(page.extract_text())
        except Exception as e:
            print(f"Failed to read PDF: {source}. Error: {e}")

    return documents
