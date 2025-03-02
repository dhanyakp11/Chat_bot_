import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import llama_cpp
from langchain_groq import ChatGroq
from qdrant_client import QdrantClient
import os

from config import UPLOAD_DIR, QDRANT_HOST, COLLECTION_NAME, MODEL_PATH , GROQ_API_KEY , COLLECTION_NAME , QDRANT_HOST , MODEL_NAME

# ---------------------------- FastAPI Backend ---------------------------- #

# Initialize FastAPI app
app = FastAPI()


# Initialize Qdrant client
client = QdrantClient(QDRANT_HOST)

# Initialize Groq's LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Qdrant client
client = QdrantClient(QDRANT_HOST)

# Ensure Qdrant collection exists
def ensure_collection():
    collections = [col.name for col in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

ensure_collection()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles file upload, processes text, generates embeddings, and stores in Qdrant."""
    try:
        # Save file locally
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from PDF
        reader = PdfReader(file_path)
        pdf_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        documents = [pdf_text]

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        document_chunks = text_splitter.create_documents(documents)

        # Load embedding model
        embedding_model = llama_cpp.Llama(model_path=MODEL_PATH, embedding=True, verbose=False)

        # Generate embeddings
        embeddings = [
            embedding_model.create_embedding(doc.page_content)["data"][0]["embedding"]
            for doc in document_chunks
        ]

        # Store in Qdrant
        points = [
            PointStruct(
                id=str(uuid.uuid4()), vector=embedding, payload={"text": doc.page_content}
            )
            for doc, embedding in zip(document_chunks, embeddings)
        ]
        client.upsert(collection_name=COLLECTION_NAME, wait=True, points=points)

        return JSONResponse(content={"filename": file.filename, "message": "File uploaded and processed successfully"})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




@app.post("/chat/")
async def chat(query: str):
    try:
        embedding_model = llama_cpp.Llama(model_path=MODEL_PATH, embedding=True, verbose=False)
        query_vector = embedding_model.embed(query)

        search_result = client.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=3)
        if not search_result:
            return JSONResponse(content={"response": "No relevant information found."})

        context = "\n\n".join([row.payload["text"] for row in search_result])
        
        prompt = f"""
        You are an AI assistant answering user questions.
        
        Context:
        {context}
        
        User: {query}
        Assistant:
        """
        
        response = llm.invoke(prompt)
        # print("respose=====",response)
        response_text = response.content
        # print("response_text-----------",response_text)

        return JSONResponse(content={"response": response_text})


    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
