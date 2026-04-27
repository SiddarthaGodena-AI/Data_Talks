# 📊 Talk to Data – Multimodal AI Analysis Platform
An end-to-end AI-powered data interaction system that allows users to upload videos, documents, images, and datasets, convert them into text, and perform deep analysis using Gemini (Vertex AI).

This project enables:
🎥 Video → Transcript
📄 Documents → Insights
🧠 AI-powered summarization & sentiment analysis
💬 Conversational “Talk to Data” chatbot
🚀 Features
📂 Multi-Format File Support

Upload and process:
Videos: mp4, mkv, avi
Documents: pdf, txt, csv
Images: jpg, png
(Extensible to more formats)

🎙️ Smart Transcription Engine
Video → Speaker-separated transcript using Gemini
Documents → Text extraction (PDF, CSV, TXT)
Images → OCR-based text extraction

😊 Sentiment Analysis
Uses Google Cloud Natural Language API
Provides:
Sentiment classification (Positive, Negative, etc.)
Intensity level (Low, Moderate, High)

👥 Speaker-Level Sentiment
Detects speakers from transcript
Performs individual sentiment analysis per speaker

🔍 Insight Extraction
Extracts key points from transcripts using Gemini
Useful for:
Meetings
Calls
Lectures

📝 AI Summary Generation
Generates concise summaries of large transcripts

📢 Social Media Content Generator
Creates:
Instagram captions
Twitter/X posts
Based on transcript content

💬 Talk to Data (Conversational AI)
Ask questions on uploaded data
Maintains context-aware conversation
Powered by Gemini

🧩 Project Structure
├── app.py                # Main Flask application (API routes)
├── google_services.py    # AI & GCP processing logic
├── utils.py              # File handling & GCS upload utilities
├── test.py               # Testing endpoints for file uploads
├── uploads/              # Temporary file storage
├── templates/            # HTML UI (index page)

⚙️ Tech Stack
Layer	Technology
Backend	Flask
AI Models	Gemini (Vertex AI)
NLP	Google Natural Language API
Storage	Google Cloud Storage (GCS)
OCR	Tesseract (optional/local)
PDF Processing	PyMuPDF / ReportLab
Authentication	Google Service Account

🔑 Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/your-username/talk-to-data.git
cd talk-to-data

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Setup Google Cloud
Create a Service Account
Enable APIs:
Vertex AI
Cloud Storage
Natural Language API

4️⃣ Configure Credentials
Update paths in code OR set environment variable:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"

5️⃣ Configure GCS Bucket
Inside utils.py:
GCS_BUCKET_NAME = "your-bucket-name"

▶️ Run the Application
python app.py

App runs at:
http://localhost:5000

📡 API Endpoints

📤 Upload File
POST /upload
Returns:
{
  "gcs_uri": "gs://bucket/file",
  "filename": "file.mp4"
}

🎙️ Transcription
POST /transcribe

😊 Sentiment Analysis
POST /analyze_sentiment

👥 Speaker Sentiment
POST /speaker_sentiment

🔍 Extract Insights
POST /extract_insights

📝 Generate Summary
POST /generate_summary

📢 Generate Social Messages
POST /generate_messages

💬 Ask Questions (Talk to Data)
POST /ask

🔄 Workflow
Upload File → Store in GCS → Transcribe/Extract Text
        ↓
   Sentiment Analysis
        ↓
 Insights / Summary / Messages
        ↓
   Conversational Q&A (Talk to Data)
