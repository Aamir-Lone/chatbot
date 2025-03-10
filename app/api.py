from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from vector_store import create_vector_store

app = Flask(__name__)

embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

vector_store_path = "app/vectorstore/brainlox_faiss"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Langchain chatbot API is running!"})

@app.route('/load', methods=['POST'])
def load_data():
    data = request.json
    source = data.get('source')
    source_type = data.get('source_type')

    if not source or not source_type:
        return jsonify({'error': 'Source and source_type are required'}), 400

    try:
        create_vector_store(source, source_type)
        return jsonify({'message': 'Vector store updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    try:
        vector_store = FAISS.load_local(
            vector_store_path,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )

        docs = vector_store.similarity_search(user_input, k=5)

        response = {
            'query': user_input,
            'results': [doc.page_content for doc in docs]
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
