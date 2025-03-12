import streamlit as st
import requests

API_URL = "http://localhost:5000"

st.title("Langchain Custom Chatbot")

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
        response = requests.post(f"{API_URL}/load", json={"source": source, "source_type": "url"})
        try:
            st.sidebar.success(response.json().get("message", "Data loaded successfully!"))
        except Exception as e:
            st.sidebar.error(f"Failed to load data: {str(e)}")
    elif source_type == "PDF" and source:
        files = {"file": ("uploaded.pdf", source.getvalue(), "application/pdf")}
        response = requests.post(f"{API_URL}/load", files=files)
        try:
            st.sidebar.success(response.json().get("message", "PDF data loaded successfully!"))
        except Exception as e:
            st.sidebar.error(f"Failed to load PDF data: {str(e)}")

st.header("Chat with the Bot")

user_input = st.text_input("Your question:")

if st.button("Send"):
    if user_input:
        response = requests.post(f"{API_URL}/chat", json={"message": user_input})
        try:
            # result = response.json().get("results", [])
            # for res in result:
            #     st.write(res)
            result = response.json().get("results", "")
            st.write(result)
        except Exception as e:
            st.error(f"Failed to fetch response: {str(e)}")
    else:
        st.warning("Please enter a question to proceed.")
