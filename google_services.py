import os
import logging
from google.cloud import storage, language_v1
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from google.cloud import language_v1
import re

def generate_transcript_from_video(gcs_video_uri, base_filename):
    model = GenerativeModel("gemini-1.5-pro-002")
    video_part = Part.from_uri(gcs_video_uri, mime_type="video/*")
    generation_config = {"max_output_tokens": 8192, "temperature": 0.7, "top_p": 0.9}
    safety_settings = [
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
    ]

    responses = model.generate_content(
        [video_part, "Generate a transcript of this video and separate between speakers using name of each speaker"],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    transcript_text = ""
    transcript_file = f"{base_filename}_transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        for response in responses:
            transcript_text += response.text
            f.write(response.text)

    return transcript_file, transcript_text

def generate_transcript_from_file(gcs_uri, base_filename):
    # Logic to determine type (video, text, image) and process accordingly
    file_extension = base_filename.split('.')[-1].lower()

    if file_extension in ['mp4', 'mkv', 'avi']:
        # Process video file
        return generate_transcript_from_video(gcs_uri, base_filename)
    elif file_extension in ['txt', 'csv', 'pdf']:
        # Process text, CSV, or PDF files
        transcript_text = extract_text_from_file(gcs_uri, base_filename, file_extension)        #extract_text_from_file
        return f"{base_filename}_transcript.txt", transcript_text
    elif file_extension in ['.jpg', '.jpeg', '.png']:                  #'jpg', 'png'
        # Process images
        transcript_text = extract_text_from_image(gcs_uri, base_filename, file_extension)  # Pass file_type here    #extract_text_from_image
        return f"{base_filename}_transcript.txt", transcript_text
    elif file_extension in ['.doc', '.docx']:
        return extract_text_from_doc(file_path)
    else:
        raise ValueError("Unsupported file type")


# Utility to extract text from image using Tesseract
def extract_text_from_image(image_path):
    # Open the image
    image = Image.open(image_path)
    # Convert to grayscale (improves OCR accuracy)
    image = image.convert('L')
    # Apply thresholding to improve OCR performance
    image = image.point(lambda p: p > 200 and 255)
    # Use Tesseract to extract text from the image
    text = pytesseract.image_to_string(image)
    return text

# Utility to extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_path):
    text = ""
    # Open the PDF
    doc = fitz.open(pdf_path)
    # Loop through each page and extract text
    for page in doc:
        text += page.get_text()
    return text

# Utility to extract text from DOC or DOCX using python-docx
def extract_text_from_doc(doc_path):
    text = ""
    # Open the Word document
    document = Document(doc_path)
    # Loop through each paragraph and extract text
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text




# def extract_text_from_file(gcs_file_uri, base_filename, file_type):
#     model = GenerativeModel("gemini-1.5-pro-002")
#     mime_type = None
#     if file_type == "pdf":
#         mime_type = "application/pdf"
#         file_part = Part.from_uri(gcs_file_uri, mime_type=mime_type)
#     elif file_type == "csv":
#         mime_type = "text/csv"
#         file_part = Part.from_uri(gcs_file_uri, mime_type=mime_type)
#     elif file_type == "txt":
#         mime_type = "text/plain"
#         file_part = Part.from_uri(gcs_file_uri, mime_type=mime_type)
#     else:
#         raise ValueError("Unsupported file type")

#     generation_config = {"max_output_tokens": 8192, "temperature": 0.7, "top_p": 0.9}
#     safety_settings = [
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#     ]

#     responses = model.generate_content(
#         [file_part, "Generate a transcript of this file"],
#         generation_config=generation_config,
#         safety_settings=safety_settings,
#         stream=True,
#     )

#     transcript_text = ""
#     transcript_file = f"{base_filename}_transcript.txt"
#     with open(transcript_file, "w", encoding="utf-8") as f:
#         for response in responses:
#             transcript_text += response.text
#             f.write(response.text)

#     return transcript_file, transcript_text

# def extract_text_from_image(gcs_image_uri, base_filename, file_type):
#     model = GenerativeModel("gemini-1.5-pro-002")
#     mime_type = None
#     if file_type == "jpg" or file_type == "jpeg":
#         mime_type = "image/jpeg"
#         image_part = Part.from_uri(gcs_image_uri, mime_type=mime_type)
#     elif file_type == "png":
#         mime_type = "image/png"
#         image_part = Part.from_uri(gcs_image_uri, mime_type=mime_type)
#     else:
#         raise ValueError("Unsupported file type")
    
#     generation_config = {"max_output_tokens": 8192, "temperature": 0.7, "top_p": 0.9}
#     safety_settings = [
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#         SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
#     ]

#     responses = model.generate_content(
#         [image_part, "Generate a transcript of this image"],
#         generation_config=generation_config,
#         safety_settings=safety_settings,
#         stream=True,
#     )

#     transcript_text = ""
#     transcript_file = f"{base_filename}_transcript.txt"
#     with open(transcript_file, "w", encoding="utf-8") as f:
#         for response in responses:
#             transcript_text += response.text
#             f.write(response.text)

#     return transcript_file, transcript_text

# def analyze_sentiment(text):
    
#     if not isinstance(text, str) or not text.strip():
#         raise ValueError("Input text for sentiment analysis must be a non-empty string.")
    
#     client = language_v1.LanguageServiceClient()
#     document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
#     response = client.analyze_sentiment(request={"document": document})
#     sentiment = response.document_sentiment
#     return {"score": sentiment.score, "magnitude": sentiment.magnitude}

def analyze_sentiment(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text for sentiment analysis must be a non-empty string.")
    
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment
    
    # Interpret score
    if sentiment.score < -0.5:
        sentiment_description = "Aggressive or Highly Negative"
    elif -0.5 <= sentiment.score < 0:
        sentiment_description = "Negative"
    elif sentiment.score == 0:
        sentiment_description = "Neutral"
    elif 0 < sentiment.score <= 0.5:
        sentiment_description = "Positive"
    else:
        sentiment_description = "Highly Positive"

    # Interpret magnitude
    if sentiment.magnitude < 1.0:
        intensity_description = "Low Intensity"
    elif 1.0 <= sentiment.magnitude < 3.0:
        intensity_description = "Moderate Intensity"
    else:
        intensity_description = "High Intensity"
    
    return {
        "sentiment": sentiment_description,
        "intensity": intensity_description
    }

# def analyze_sentiment(transcript_text):
#     # Check if the input is a valid non-empty string
#     if not isinstance(transcript_text, str) or not transcript_text.strip():
#         raise ValueError("Input text for sentiment analysis must be a non-empty string.")
    
#     # Instantiate the client
#     client = language_v1.LanguageServiceClient()
    
#     # Prepare the document for analysis
#     document = language_v1.Document(content=transcript_text, type_=language_v1.Document.Type.PLAIN_TEXT)
    
#     # Analyze the sentiment of the document
#     response = client.analyze_sentiment(request={"document": document})
#     sentiment = response.document_sentiment
    
#     # Return the sentiment score and magnitude
#     return {"score": sentiment.score, "magnitude": sentiment.magnitude}


# def speaker_sentiment_analysis(transcript):
#     speaker_pattern = r"\[([^\]]+)\]"  # Matches speaker labels like [Narrator], [ChatGPT Assistant 1]
    
#     # Split transcript into chunks by speakers
#     speaker_segments = re.split(speaker_pattern, transcript)
#     sentiment_results = {}

#     # Iterate over the split text to identify speakers and their content
#     for i in range(1, len(speaker_segments), 2):
#         speaker = speaker_segments[i].strip()
#         content = speaker_segments[i + 1].strip()

#         # Aggregate content for each speaker
#         if speaker not in sentiment_results:
#             sentiment_results[speaker] = {"text": "", "sentiment": []}
#         sentiment_results[speaker]["text"] += " " + content

#     # Perform sentiment analysis for each speaker
#     for speaker, data in sentiment_results.items():
#         sentiment = analyze_sentiment(data["text"])
#         sentiment_results[speaker]["sentiment"] = sentiment

#     return sentiment_results



def speaker_sentiment_analysis(transcript):
    speaker_pattern = r"\[([^\]]+)\]"  # Matches speaker labels like [Narrator], [ChatGPT Assistant 1]
    
    # Split transcript into chunks by speakers
    speaker_segments = re.split(speaker_pattern, transcript)
    sentiment_results = {}

    # Iterate over the split text to identify speakers and their content
    for i in range(1, len(speaker_segments), 2):
        speaker = speaker_segments[i].strip()
        content = speaker_segments[i + 1].strip()

        # Aggregate content for each speaker
        if speaker not in sentiment_results:
            sentiment_results[speaker] = {"text": "", "sentiment": {}}
        sentiment_results[speaker]["text"] += " " + content

    # Perform sentiment analysis for each speaker
    for speaker, data in sentiment_results.items():
        sentiment = analyze_sentiment(data["text"])
        sentiment_results[speaker]["sentiment"] = {
            "sentiment_description": sentiment["sentiment"],
            "intensity_description": sentiment["intensity"]
        }

    return sentiment_results


def extract_insights(transcript_text):
    model = GenerativeModel("gemini-1.5-pro-002")
    text_part = Part.from_text(transcript_text)
    generation_config = {"max_output_tokens": 1024, "temperature": 0.5, "top_p": 0.9}
    safety_settings = [
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
    ]

    responses = model.generate_content(
        [text_part, "Extract key insights from the text like important points."],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    insights = ""
    for response in responses:
        insights += response.text

    return insights

def generate_summary(transcript_text):
    model = GenerativeModel("gemini-1.5-pro-002")
    text_part = Part.from_text(transcript_text)
    generation_config = {"max_output_tokens": 1024, "temperature": 0.5, "top_p": 0.9}
    safety_settings = [
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
    ]

    responses = model.generate_content(
        [text_part, "Summarize the text in a concise paragraph."],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    summary = ""
    for response in responses:
        summary += response.text

    return summary

def generate_messages(transcript_text):
    model = GenerativeModel("gemini-1.5-pro-002")
    text_part = Part.from_text(transcript_text)
    generation_config = {"max_output_tokens": 1024, "temperature": 0.7, "top_p": 0.9}
    safety_settings = [
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
    ]

    responses = model.generate_content(
        [text_part, "Generate a few quotes or messages for instagram and twitter."],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    messages = ""
    for response in responses:
        messages += response.text

    return messages



def initialize_gemini_model():
    model = GenerativeModel("gemini-1.5-pro-002")
    generation_config = {"max_output_tokens": 1024, "temperature": 0.1, "top_p": 0.9}
    safety_settings = [
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
    ]
    return model, generation_config, safety_settings


def talk_to_data_bot_continuous(transcript_text, question):
    model, generation_config, safety_settings = initialize_gemini_model()

    # Initialize conversation history
    conversation_history = [{"role": "system", "content": transcript_text}]
    conversation_history.append({"role": "user", "content": question})

    # Create the request by converting conversation history to Part objects
    conversation_parts = [Part.from_text(turn["content"]) for turn in conversation_history]

    # Get model response
    responses = model.generate_content(
        conversation_parts,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    # Collect the response
    answer = ""
    for response in responses:
        answer += response.text

    return answer

