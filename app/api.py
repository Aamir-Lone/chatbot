
# ***********************************************************************************

from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from vector_store import create_vector_store
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



# embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

vector_store_path = "app/vectorstore/brainlox_faiss"

# Load FLAN-T5 model for response generation
# rag_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
rag_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Langchain chatbot API is running!"})

@app.route('/load', methods=['POST'])
def load_data():
    if 'file' in request.files:
        pdf_file = request.files['file']
        if pdf_file.filename == '':
            return jsonify({'error': 'No file uploaded'}), 400

        try:
            pdf_content = pdf_file.read()
            create_vector_store(pdf_content, "pdf")
            return jsonify({'message': 'PDF data loaded successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

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
        # context = " ".join([doc.page_content.replace('\n', ' ') for doc in docs])
        context = "\n\n---\n\n".join([f"Document {i+1}:\n{doc.page_content.replace('\n', ' ')}" for i, doc in enumerate(docs)])

        # Use FLAN-T5 model to generate response based on context and query
        # prompt = f"Context: {context}\nQuery: {user_input}\nAnswer:"

        prompt = f"""
        Using ONLY the following context, provide a comprehensive and detailed answer to the question.
        Give a thorough explanation using multiple sentences and include all relevant information from the context.
        If the context contains a definition or explanation, include it fully in your answer.
        Don't be brief - aim to provide a complete answer.

        IMPORTANT: If the context does not contain information directly relevant to the question, you MUST respond with ONLY:
        "I don't have enough information in the provided context to answer this question."

        DO NOT use any prior knowledge or information outside of the provided context.
        DO NOT try to answer the question if the context is not relevant.
        DO NOT make up information that is not in the context.

        Context:
        {context}

        Question: {user_input}

        Detailed Answer:
        """
        # generated_response = rag_pipeline(prompt, max_length=500, num_return_sequences=1)
        generated_response = rag_pipeline(
            prompt, 
            max_length=500, 
            min_length=50,  #100 Encourage longer responses
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,  # Add some creativity
            no_repeat_ngram_size=3  # Reduce repetition
        )

        # Clean and format the response
        response_text = generated_response[0]['generated_text']

        # Remove excessive newlines and multiple spaces
        response_text = " ".join(response_text.split())

        response = {
            'query': user_input,
            'results': response_text
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     # app.run(host='0.0.0.0', port=5000, debug=True)
#     app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    from waitress import serve
    print("Starting server on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)


    #*************************************************************************************************

    from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from vector_store import create_vector_store
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

vector_store_path = "app/vectorstore/brainlox_faiss"

# Load FLAN-T5 model for response generation
# rag_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
rag_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Langchain chatbot API is running!"})

@app.route('/load', methods=['POST'])
def load_data():
    if 'file' in request.files:
        pdf_file = request.files['file']
        if pdf_file.filename == '':
            return jsonify({'error': 'No file uploaded'}), 400

        try:
            pdf_content = pdf_file.read()
            create_vector_store(pdf_content, "pdf")
            return jsonify({'message': 'PDF data loaded successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

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

        # Get relevant documents and their scores
        docs_with_scores = vector_store.similarity_search_with_score(user_input, k=5)
        
        # Check if documents are relevant (using a threshold)
        relevant_docs = []
        for doc, score in docs_with_scores:
            # For FAISS, lower score means more relevant
            # You may need to adjust this threshold based on testing
            if score < 1.4:  # Threshold value - adjust as needed
                relevant_docs.append(doc)
        
        # If no relevant documents found, return early
        if not relevant_docs:
            return jsonify({
                'query': user_input,
                'results': "I don't have information about that in my knowledge base. The documents I have access to don't cover this topic."
            })
        
        # Proceed with generating response using relevant documents
        context = "\n\n---\n\n".join([f"Document {i+1}:\n{doc.page_content.replace('\n', ' ')}" for i, doc in enumerate(relevant_docs)])
        
        # Use FLAN-T5 model to generate response based on context and query
        prompt = f"""
RETRIEVAL TASK: Answer the question using ONLY information from the provided context.

Context:
{context}

Question: {user_input}

Instructions:
1. If the context contains information that directly answers the question, provide a thorough and detailed answer.
2. If the context does NOT contain information related to the question, respond EXACTLY with:
   "I don't have information about that in my knowledge base. The documents I have access to don't cover this topic."
3. Do not use any prior knowledge.
4. Do not make up information.
5. Do not be creative.
6. Do not try to be helpful by guessing.

Answer:
"""
        
        generated_response = rag_pipeline(
            prompt, 
            max_length=500, 
            min_length=20,  # Reduced from 50 to allow for "I don't have information" responses
            num_return_sequences=1,
            do_sample=False,  # Set to False for more deterministic responses
            temperature=0.2,  # Reduced from 0.7 to make responses less creative
            no_repeat_ngram_size=3  # Reduce repetition
        )

        # Clean and format the response
        response_text = generated_response[0]['generated_text']

        # Remove excessive newlines and multiple spaces
        response_text = " ".join(response_text.split())

        response = {
            'query': user_input,
            'results': response_text
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from waitress import serve
    print("Starting server on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)