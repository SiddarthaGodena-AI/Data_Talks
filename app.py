from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from utils import allowed_file, upload_to_gcs
from google_services import (
    generate_transcript_from_file,
    analyze_sentiment,
    extract_insights,
    generate_summary,
    generate_messages,
    talk_to_data_bot_continuous,
    speaker_sentiment_analysis
)
import google.auth

# Load Google Cloud credentials
credentials, project = google.auth.load_credentials_from_file(
    'E:\\Inoday\\TalkToData\\inoday-retail-b76cf3aacd5a.json'
)

# Flask Config
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'txt', 'pdf', 'csv', 'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)

        # Upload to GCS
        gcs_uri = upload_to_gcs(local_path, filename)
        return jsonify({"gcs_uri": gcs_uri, "filename": filename})

    return jsonify({"error": "Invalid file type"}), 400

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    gcs_uri = data.get('gcs_uri')
    filename = data.get('filename')

    if not gcs_uri or not filename:
        return jsonify({"error": "Missing GCS URI or filename"}), 400

    # Perform transcription
    transcript_file, transcript_text = generate_transcript_from_file(gcs_uri, filename)
    return jsonify({"transcript_file": transcript_file, "transcript_text": transcript_text})

@app.route('/analyze_sentiment', methods=['POST'])
def sentiment_analysis():
    data = request.json
    transcript_text = data.get('transcript_text')

    if not transcript_text:
        return jsonify({"error": "Missing transcript text"}), 400

    sentiment = analyze_sentiment(transcript_text)
    return jsonify({"sentiment": sentiment})

@app.route('/speaker_sentiment', methods=['POST'])
def handle_speaker_sentiment():
    data = request.json
    transcript_text = data.get('transcript_text')

    if not transcript_text:
        return jsonify({"error": "Missing transcript text"}), 400

    try:
        # Call the renamed function with transcript_text
        sentiment_results = speaker_sentiment_analysis(transcript_text)
        return jsonify({"speaker_sentiment": sentiment_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/extract_insights', methods=['POST'])
def extract_insights_route():
    data = request.json
    transcript_text = data.get('transcript_text')

    if not transcript_text:
        return jsonify({"error": "Missing transcript text"}), 400

    insights = extract_insights(transcript_text)
    return jsonify({"insights": insights})

@app.route('/generate_summary', methods=['POST'])
def generate_summary_route():
    data = request.json
    transcript_text = data.get('transcript_text')

    if not transcript_text:
        return jsonify({"error": "Missing transcript text"}), 400

    summary = generate_summary(transcript_text)
    return jsonify({"summary": summary})

@app.route('/generate_messages', methods=['POST'])
def generate_messages_route():
    data = request.json
    transcript_text = data.get('transcript_text')

    if not transcript_text:
        return jsonify({"error": "Missing transcript text"}), 400

    messages = generate_messages(transcript_text)
    return jsonify({"messages": messages})

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    transcript_text = data.get('transcript_text')
    question = data.get('question')

    if not transcript_text or not question:
        return jsonify({"error": "Missing transcript text or question"}), 400

    # Call the Talk to Data Bot
    answer = talk_to_data_bot_continuous(transcript_text, question)

    if answer:
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": "Could not process the question"}), 500

if __name__ == '__main__':
    app.run(debug=True)
