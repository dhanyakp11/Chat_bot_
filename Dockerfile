# Use official Python image as base
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Start both FastAPI and Streamlit using a process manager
CMD ["bash", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
