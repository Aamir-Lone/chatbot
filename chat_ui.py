import streamlit as st
import requests

# Streamlit UI
st.title("Langchain Chatbot")
st.write("Interact with the chatbot built using Langchain and FAISS")

# User input
user_input = st.text_input("Ask something about technical courses:")

if st.button("Send"):
    if user_input:
        try:
            response = requests.post(
                "http://localhost:5000/chat",
                json={"message": user_input}
            )
            if response.status_code == 200:
                data = response.json()
                st.subheader("Results:")
                for result in data.get("results", []):
                    st.write(f"- {result}")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")
    else:
        st.warning("Please enter a message before sending.")

# Run this with: streamlit run chat_ui.py
