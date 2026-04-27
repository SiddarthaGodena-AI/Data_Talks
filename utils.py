import os
from google.cloud import storage
import vertexai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit

# Google Cloud Config
PROJECT_ID = "inoday-retail"
LOCATION = "us-central1"
GCS_BUCKET_NAME = "inoday-talkwithdata-analysis"
vertexai.init(project=PROJECT_ID, location=LOCATION)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def upload_to_gcs(local_path, destination_blob_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "E:\\Inoday\\TalkToData\\inoday-retail-b76cf3aacd5a.json"
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_path)
    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{destination_blob_name}"
    return gcs_uri

def save_transcript_to_pdf(transcript_text, pdf_file):
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    x_margin = inch * 0.5
    y_margin = height - inch * 1.5
    line_height = 14

    lines = simpleSplit(transcript_text, 'Helvetica', 10, width - 2 * x_margin)
    y_position = y_margin
    for line in lines:
        c.drawString(x_margin, y_position, line)
        y_position -= line_height
        if y_position < inch:  # Page overflow
            c.showPage()
            y_position = height - inch * 1.5

    c.save()
