
from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)

# Load the FAISS vector store
embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
# embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
vector_store = FAISS.load_local(
    "C:\\langchain_chatbot\\app\\vectorstore\\brainlox_faiss",
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Langchain chatbot API is running!"})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Retrieve similar documents from the vector store
        docs = vector_store.similarity_search(user_input, k=5)

        # Prepare the response
        response = {
            'query': user_input,
            'results': [doc.page_content for doc in docs]
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
