from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'mp4', 'txt', 'pdf', 'csv', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if a file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """Route to handle file upload."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Save the file to the upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Process the file based on its type
    file_extension = file.filename.rsplit('.', 1)[1].lower()

    if file_extension == 'mp4':
        # Add video processing logic here
        return jsonify({"message": "Video file uploaded and processed", "file": file.filename}), 200

    elif file_extension == 'txt':
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({"message": "Text file uploaded", "content": content}), 200

    elif file_extension == 'pdf':
        # Add PDF processing logic here (e.g., extract text using PyPDF2 or PyMuPDF)
        return jsonify({"message": "PDF file uploaded"}), 200

    elif file_extension == 'csv':
        # Add CSV processing logic here (e.g., read using pandas)
        return jsonify({"message": "CSV file uploaded"}), 200

    elif file_extension in {'jpg', 'jpeg', 'png'}:
        # Add image processing logic here (e.g., OCR using Tesseract)
        return jsonify({"message": "Image file uploaded"}), 200

    else:
        return jsonify({"error": "Unsupported file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)
