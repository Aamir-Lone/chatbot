# import streamlit as st
# import requests

# API_URL = "http://localhost:5000"

# st.title("Langchain Custom Chatbot")

# st.sidebar.header("Data Source")
# source_type = st.sidebar.radio("Choose data source type:", ["URL", "PDF"])

# source = None  # Ensure source is always defined
# if source_type == "URL":
#     source = st.sidebar.text_input("Enter the URL:")
# elif source_type == "PDF":
#     source = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

# st.sidebar.write(f"Source Type: {source_type}")
# st.sidebar.write(f"Source: {source}")

# if st.sidebar.button("Load Data"):
#     if source_type == "URL" and source:
#         response = requests.post(f"{API_URL}/load", json={"source": source, "source_type": "url"})
#         try:
#             st.sidebar.success(response.json().get("message", "Data loaded successfully!"))
#         except Exception as e:
#             st.sidebar.error(f"Failed to load data: {str(e)}")
#     elif source_type == "PDF" and source:
#         files = {"file": ("uploaded.pdf", source.getvalue(), "application/pdf")}
#         response = requests.post(f"{API_URL}/load", files=files)
#         try:
#             st.sidebar.success(response.json().get("message", "PDF data loaded successfully!"))
#         except Exception as e:
#             st.sidebar.error(f"Failed to load PDF data: {str(e)}")

# st.header("Chat with the Bot")

# user_input = st.text_input("Your question:")

# if st.button("Send"):
#     if user_input:
#         response = requests.post(f"{API_URL}/chat", json={"message": user_input})
#         try:
#             # result = response.json().get("results", [])
#             # for res in result:
#             #     st.write(res)
#             result = response.json().get("results", "")
#             st.write(result)
#         except Exception as e:
#             st.error(f"Failed to fetch response: {str(e)}")
#     else:
#         st.warning("Please enter a question to proceed.")

import streamlit as st
import requests
import traceback
import time

API_URL = "http://localhost:5000"

st.title("Langchain Custom Chatbot")

# Add API connection status check
try:
    with st.spinner("Checking API connection..."):
        health_response = requests.get(f"{API_URL}/", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Connected to API server")
        else:
            st.error(f"⚠️ API server responded with status code: {health_response.status_code}")
except Exception as e:
    st.error(f"⚠️ Cannot connect to API server at {API_URL}. Please ensure the server is running.")
    st.error(f"Error details: {str(e)}")

st.sidebar.header("Data Source")
source_type = st.sidebar.radio("Choose data source type:", ["URL", "PDF"])

source = None  # Ensure source is always defined
if source_type == "URL":
    source = st.sidebar.text_input("Enter the URL:")
elif source_type == "PDF":
    source = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

st.sidebar.write(f"Source Type: {source_type}")
st.sidebar.write(f"Source: {source}")

if st.sidebar.button("Load Data"):
    if source_type == "URL" and source:
        try:
            with st.sidebar.status("Connecting to API...") as status:
                status.update(label="Sending URL to API...", state="running")
                response = requests.post(
                    f"{API_URL}/load", 
                    json={"source": source, "source_type": "url"},
                    timeout=60  # Increased timeout for large files
                )
                status.update(label=f"Received response: {response.status_code}", state="running")
                
                if response.status_code == 200:
                    status.update(label="Data loaded successfully!", state="complete")
                    st.sidebar.success(response.json().get("message", "Data loaded successfully!"))
                else:
                    status.update(label=f"Error: {response.status_code}", state="error")
                    st.sidebar.error(f"Server responded with status code: {response.status_code}")
                    st.sidebar.error(f"Response: {response.text}")
        except requests.exceptions.Timeout:
            st.sidebar.error("Request timed out. The URL might be too large or the server is busy.")
        except Exception as e:
            st.sidebar.error(f"Failed to load data: {str(e)}")
            st.sidebar.error(traceback.format_exc())
    
    elif source_type == "PDF" and source:
        try:
            with st.sidebar.status("Processing PDF...") as status:
                status.update(label="Sending PDF to API...", state="running")
                files = {"file": ("uploaded.pdf", source.getvalue(), "application/pdf")}
                response = requests.post(
                    f"{API_URL}/load", 
                    files=files,
                    timeout=120  # Longer timeout for PDF processing
                )
                status.update(label=f"Received response: {response.status_code}", state="running")
                
                if response.status_code == 200:
                    status.update(label="PDF processed successfully!", state="complete")
                    st.sidebar.success(response.json().get("message", "PDF data loaded successfully!"))
                else:
                    status.update(label=f"Error: {response.status_code}", state="error")
                    st.sidebar.error(f"Server responded with status code: {response.status_code}")
                    st.sidebar.error(f"Response: {response.text}")
        except requests.exceptions.Timeout:
            st.sidebar.error("Request timed out. The PDF might be too large or the server is busy.")
        except Exception as e:
            st.sidebar.error(f"Failed to load PDF data: {str(e)}")
            st.sidebar.error(traceback.format_exc())

# Save conversation history in session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.header("Chat with the Bot")

# Display conversation history
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.write(f"You: {message['content']}")
    else:
        st.write(f"Bot: {message['content']}")

user_input = st.text_input("Your question:")

if st.button("Send"):
    if user_input:
        # Add user message to conversation
        st.session_state.conversation.append({"role": "user", "content": user_input})
        
        # Display the latest user message
        st.write(f"You: {user_input}")
        
        # Show a spinner while waiting for response
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat", 
                    json={"message": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json().get("results", "")
                    
                    # Add bot response to conversation
                    st.session_state.conversation.append({"role": "assistant", "content": result})
                    
                    # Display the response
                    st.write(f"Bot: {result}")
                else:
                    st.error(f"Server error: {response.status_code}")
                    st.error(f"Response: {response.text}")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The server might be busy processing your query.")
            except Exception as e:
                st.error(f"Failed to fetch response: {str(e)}")
                st.error(traceback.format_exc())
    else:
        st.warning("Please enter a question to proceed.")