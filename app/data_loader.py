
import requests
from langchain_community.document_loaders import WebBaseLoader
import os

# Function to load data from the URL
def load_data(url):
    try:
        user_agent = os.getenv("USER_AGENT", "Mozilla/5.0")
        loader = WebBaseLoader(url)
        documents = loader.load()
        return documents
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

if __name__ == "__main__":
    url = "https://brainlox.com/courses/category/technical"
    # url = "https://www.merge.dev/blog/webhooks-vs-polling"
    docs = load_data(url)
    print(f"Loaded {len(docs)} documents")
