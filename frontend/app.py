import streamlit as st
import requests

# Set Streamlit page title
st.set_page_config(page_title="Chatbot Application", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")

if "page" not in st.session_state:
    st.session_state.page = "Upload"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.sidebar.button("Upload"):
    st.session_state.page = "Upload"
if st.sidebar.button("Chat"):
    st.session_state.page = "Chat"

# Upload File Page
if st.session_state.page == "Upload":
    st.title("Upload File")
    
    # File uploader widget
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload File"):  # Explicit upload button
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            try:
                with st.spinner("Uploading..."):
                    response = requests.post("http://127.0.0.1:8000/upload/", files=files)
                
                # Display response
                if response.status_code == 200:
                    st.success("✅ File uploaded successfully!")
                else:
                    st.error(f"❌ Upload failed: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error: {e}")

# Chat Page
elif st.session_state.page == "Chat":
    st.title("Chat with AI")

    # Display previous chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])

    # Chat input at the bottom
    user_query = st.chat_input("Enter your message...")

    if user_query:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(f"http://127.0.0.1:8000/chat/?query={user_query}")
            
            if response.status_code == 200:
                ai_response = response.json().get("response", "No response")

                # Store in chat history
                st.session_state.chat_history.append({"question": user_query, "answer": ai_response})

                # Display response
                with st.chat_message("user"):
                    st.write(user_query)
                with st.chat_message("assistant"):
                    st.write(ai_response)
            else:
                st.error(f"❌ Chat failed: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {e}")
