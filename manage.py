from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import zipfile
import cv2
import base64
import json

app = Flask(__name__)
CORS(app)

VIDEO_PATH = 'video.mp4'
UPLOAD_FOLDER = 'uploaded_files'


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
def generate_data():
    x, y, width, length, i = (20, 20, 10, 10, 0) 
    label = "test one"
    while True:
        if i > 10:
            label = "test one"
            i, width, length = (0, 10, 10)
        else:
            if i == 5:
                label = "test two"
            i, width, length = (i + 1, width + i, length + i)
        yield {'x': x, 'y': y, 'width': width, 'length': length, "label":label}

def video_stream_generator():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise RuntimeError("Video file could not be opened")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # Stop the loop if no frames are left
            _, buffer = cv2.imencode('.jpg', frame)
            frame_encoded = base64.b64encode(buffer).decode('utf-8')
            yield f"data: {json.dumps({'frame': frame_encoded, 'metadata': generate_data()})}\n\n"
    finally:
        cap.release()

@app.route('/video_stream')
def video_stream():
    return Response(video_stream_generator(), mimetype='text/event-stream')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.zip'):
        zip_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(UPLOAD_FOLDER)
        os.remove(zip_path)  
        return "Files have been uploaded and extracted", 200
    
    return "Invalid file format", 400


@app.route('/test')
def test():
    return jsonify({'message': 'Server is running!'})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
