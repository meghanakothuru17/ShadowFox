from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from collections import Counter
import re
import io
import PyPDF2
from docx import Document
import pandas as pd
import uvicornice, then your backend is in Python, so the fix is:

Put the Python backend online, and

Point your frontend to that online URL (not localhost).

1. Deploy your Python backend (simple plan with Render)
Use Render’s free tier to host a small Flask/FastAPI/Django API.
​

High‑level steps:

Make sure your backend project has at least:

app.py or main.py (your Flask/FastAPI code)

requirements.txt listing packages like flask or fastapi, uvicorn, etc.
​
​

For Flask, also a Procfile (example below).
​
​

Push the backend code to a separate GitHub repo (not the frontend one on Pages).
​
​

Go to render.com → New → Web Service → Connect GitHub and select that backend repo.
​

Set:

Runtime: Python

Start command (examples):

Flask: gunicorn app:app (replace app with your file name if needed)
​
​

FastAPI: uvicorn main:app --host 0.0.0.0 --port 10000 (adjust file name)
​

Click “Create Web Service”.

After deploy, Render gives a URL like:
https://your-backend.onrender.com
​

Your file‑upload route will then be something like:
https://your-backend.onrender.com/upload

(Replace /upload with whatever route your Python code uses.)

Minimal Flask example (if you need it)
python
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join("uploads", filename))
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()
requirements.txt (example):

text
Flask
gunicorn
Procfile:

text
web: gunicorn app:app
Adjust names to your real file/variables.
​
​

2. Change your frontend fetch URL
Right now your JS probably has something like:

js
fetch("http://localhost:5000/upload", {
  method: "POST",
  body: formData,
});
On GitHub Pages this will fail with “unable to fetch” because there is no localhost backend.
​

After deploying backend on Render (or Railway, etc.), change it to:

js
fetch("https://your-backend.onrender.com/upload", {
  method: "POST",
  body: formData,
});
Replace with your exact Render URL and route.
​

Then:

Re‑upload/update your index.html (or JS file) in the GitHub Pages repo.

Wait for Pages to redeploy, refresh your site, and try uploading again.

What to send next so this can be made exact
Reply with:

Your Python code that handles the file upload route (the @app.route("/...") function).

The fetch (or axios) code from your frontend where you upload the file.

Then the exact Render configuration (start command) and the exact new URL to put in your JS can be written for you.
import os
from typing import List

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Initialize FastAPI app
app = FastAPI(title="Keyword Extractor API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
stop_words = set(stopwords.words('english'))

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_text_from_excel(file_content: bytes) -> str:
    """Extract text from Excel file"""
    try:
        excel_file = io.BytesIO(file_content)
        df = pd.read_excel(excel_file)
        text = ""
        for column in df.columns:
            text += " ".join(df[column].astype(str).values) + " "
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel: {str(e)}")

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading text file: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and preprocess text"""
    # Remove extra whitespace and special characters
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.lower().strip()
    return text

def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """Extract keywords from text using NLTK"""
    
    # Clean text
    cleaned_text = clean_text(text)
    
    # Tokenize
    tokens = word_tokenize(cleaned_text)
    
    # Filter out stop words and short words
    filtered_tokens = [
        word for word in tokens 
        if word not in stop_words 
        and len(word) > 2 
        and word.isalpha()
    ]
    
    # Get POS tags
    pos_tags = pos_tag(filtered_tokens)
    
    # Extract nouns, adjectives, and verbs
    important_words = [
        word for word, pos in pos_tags 
        if pos.startswith(('NN', 'JJ', 'VB'))  # Nouns, Adjectives, Verbs
    ]
    
    # Count frequency
    word_freq = Counter(important_words)
    
    # Get most common keywords
    keywords = [word for word, count in word_freq.most_common(max_keywords)]
    
    return keywords

def get_file_stats(text: str) -> dict:
    """Get basic statistics about the text"""
    words = text.split()
    return {
        "word_count": len(words),
        "character_count": len(text),
        "paragraph_count": len(text.split('\n\n'))
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Keyword Extractor API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is working properly"}

@app.post("/extract-keywords")
async def extract_keywords_endpoint(file: UploadFile = File(...)):
    """Extract keywords from uploaded file"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file extension
    file_extension = file.filename.split('.')[-1].lower()
    
    # Supported file types
    supported_types = ['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'xls']
    if file_extension not in supported_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported types: {', '.join(supported_types)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
        
        # Extract text based on file type
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file_content)
        elif file_extension in ['docx', 'doc']:
            text = extract_text_from_docx(file_content)
        elif file_extension in ['xlsx', 'xls']:
            text = extract_text_from_excel(file_content)
        elif file_extension in ['txt', 'md']:
            text = extract_text_from_txt(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Validate extracted text
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="File appears to be empty or contains insufficient text")
        
        # Extract keywords
        keywords = extract_keywords(text)
        
        # Get file statistics
        stats = get_file_stats(text)
        
        # Prepare response
        response = {
            "filename": file.filename,
            "keywords": keywords,
            "keyword_count": len(keywords),
            "word_count": stats["word_count"],
            "character_count": stats["character_count"],
            "status": "success"
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/test-keywords")
async def test_keywords():
    """Test endpoint with sample text"""
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    and statistical models. Deep learning uses neural networks with multiple layers. 
    Natural language processing helps computers understand human language. 
    Data science combines programming, statistics, and domain expertise.
    """
    
    keywords = extract_keywords(sample_text)
    stats = get_file_stats(sample_text)
    
    return {
        "sample_text": sample_text.strip(),
        "keywords": keywords,
        "keyword_count": len(keywords),
        "word_count": stats["word_count"],
        "status": "success"
    }

if __name__ == "__main__":
    print("Starting Keyword Extractor API...")
    print("API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Test endpoint: http://localhost:8000/test-keywords")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )