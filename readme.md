# Langchain Custom Chatbot

This project is a custom chatbot built using Langchain. It scrapes data from a webpage, creates embeddings, stores them in a vector store, and serves a simple conversational API through Flask. The chatbot fetches relevant content based on user queries by searching for similar embeddings in the vector store.

## Project Structure

```
project-root/
|-- app/
|   |-- data_loader.py         # Loads data from the target URL
|   |-- vector_store.py        # Creates and stores embeddings using Hugging Face
|   |-- api.py                 # Flask API to handle chat requests
|   |-- vectorstore/           # Folder containing the FAISS vector store
|-- requirements.txt          # Required dependencies
|-- README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the Repository:**

```
git clone https://github.com/Aamir-Lone/langchain_chatbot
cd langchain_chatbot
```

2. **Set Up Virtual Environment (Optional but Recommended):**

```
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

3. **Install Dependencies:**

```
pip install -r requirements.txt
```

4. **Set Up Environment Variables:**
Create a `.env` file in the root directory:

```
OPENAI_API_KEY=<your-openai-api-key>
USER_AGENT=Mozilla/5.0
```

5. **Load Data and Create Vector Store:**

```
python app/vector_store.py
```

6. **Run the Flask API:**

```
python app/api.py
```

The API will be running at `http://localhost:5000`

## Testing the API

1. **Check if the API is Running:**

```
GET http://localhost:5000/
```
Response:
```
{
  "message": "Langchain chatbot API is running!"
}
```

2. **Send a Chat Message:(Using Postman)**
    send a post request 
```

POST http://localhost:5000/chat
Content-Type: application/json

{
  "message": "Tell me about technical courses"
}
```

Response:
```
{
  "query": "Tell me about technical courses",
  "results": [
    "Course 1 details...",
    "Course 2 details...",
    ...
  ]
}
```

## Why Hugging Face Embeddings?

i chose Hugging Face embeddings (specifically the `sentence-transformers/all-MiniLM-L6-v2` model) because:
- **Open-Source and Free:** Hugging Face models are open and don’t require paid API usage.
- **Local Execution:** No API calls, faster inference without network latency.
- **Flexibility:** Access to a wide variety of state-of-the-art models optimized for different NLP tasks.

> **Note:** i kept the OpenAI embeddings implementation in a separate branch named `test1` for reference and experimentation.

## Additional Notes

- The FAISS vector store is saved in `app/vectorstore/brainlox_faiss`
- If accuracy needs improvement, try experimenting with different text splitters or embedding models.
- Ensure your `.env` file contains necessary keys if using the OpenAI branch.



