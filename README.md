# 📚 Chatbot Application with FastAPI, LangChain & Streamlit

This is an AI-powered chatbot that processes **PDF documents**, extracts relevant information, and answers user queries using **FastAPI (Backend), LangChain, Llama.cpp (Embeddings), Qdrant (Vector DB), and Streamlit (Frontend).**  

---

## 🚀 Features
✅ Upload PDFs and extract text  
✅ Store document embeddings in **Qdrant**  
✅ Query the chatbot and get AI-powered answers  
✅ Uses **LangChain** for text chunking & embeddings  
✅ **FastAPI** for backend, **Streamlit** for frontend  
✅ **Dockerized** for easy deployment  

---

API Documentation
1️⃣ Upload a PDF

Endpoint: /upload/
Method: POST
Description: Uploads a PDF, extracts text, generates embeddings, and stores them in Qdrant.

2️⃣ Chat with the AI

Endpoint: /chat/
Method: POST
Description: Takes a user query, retrieves relevant context from Qdrant, and returns an AI-generated response.

------

Download and place the model in the folder models

Go to Huggingface and download this model "mxbai-embed-large-v1-f16.gguf" and place it in models folder 

Login to Groqcloud and create an API Key and update it in the config.py file
------
Install Dependencies
$pip install -r requirements.txt

Start the Backend (FastAPI)
$uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
🚀 FastAPI runs on http://127.0.0.1:8000

Start the Frontend (Streamlit)
$streamlit run frontend/app.py
🎨 Streamlit runs on http://127.0.0.1:8501

------------

🐳 Docker Setup
Build Docker Image
$docker build -t chatbot-app .

Run Docker Container
$docker run -p 8000:8000 -p 8501:8501 chatbot-app

Run with Docker Compose (Backend + Qdrant)
$docker-compose up --build


