FROM python:3.11-slim

# Install system dependencies including Tesseract OCR and OpenCV requirements
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn fastapi python-multipart

# Copy project files
COPY . .

# Expose ports: 8000 (FastAPI API) and 8501 (Streamlit)
EXPOSE 8000 8501

# Default command to run FastAPI backend or Streamlit
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
