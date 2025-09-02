from flask import Flask, send_from_directory, request
from werkzeug.utils import secure_filename
import os
from flask_socketio import SocketIO, send, emit
from ai_modules.yolo11s import Yolo11s
from utilities.base64_transcoder import Base64_Transcoder
import argparse
import uuid
import hashlib
#from ai_modules.tensorflow import TensorFlowModel

# Defines this file for flask as the WSGI app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000 * 1000 # 2GB max model file size

parser = argparse.ArgumentParser(description='Run Railway Object Detection ')

parser.add_argument('--address', dest='hostname', default="localhost", help="Network interface to start the socketIO/webserver on.")
parser.add_argument('--port', dest='port', default='5000', help="Specifies the port for the socketIO/web server to start on.")

args = parser.parse_args()

hostname = args.hostname
port = args.port

socketio = SocketIO(app, cors_allowed_origins=["https://piehost.com",f"http://{hostname}:{port}"], max_http_buffer_size=10*1000000)

# Remembers the default models
DEFAULT_MODELS = {'yolo': 'ai_modules/ob_detect_models/yolo11s.pt'}
model_file = DEFAULT_MODELS['yolo']
def change_model_file(new_model_path):
    if model_file not in DEFAULT_MODELS.values():
        os.remove(model_file)
    model_file = new_model_path

# Function to get file hashes (used as ids for videos and models)
def get_sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

object_detection_model = Yolo11s()

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

# Constant defining what file types can be uploaded
ALLOWED_MODEL_EXTENSIONS = ['pt']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mkv']
MODEL_LOCATION = 'ai_modules/ob_detect_models/custom/'
VIDEO_LOCATION = 'test_videos/upload/'
def validate_extension(filename, extension_list):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_MODEL_EXTENSIONS
def get_basename(filename):
    return filename.split('.')[0]

@app.route("/models", methods=['POST'])
def upload_model():
    if request.method == 'POST':
        if 'model_file' not in request.files:
            return "File part not found in request", 400
        file = request.files['model_file']
        if file.filename == '':
            return "No file uploaded", 400
        if not file or not validate_extension(file.filename, ALLOWED_MODEL_EXTENSIONS):
            return "Invalid file extension", 400
        file_bytes = file.read()
        # Generate Metadata for model
        model_id = get_sha256(file_bytes)
        name = get_basename(file.filename)

        # Save Model to Blob Storage
        file_extension = secure_filename(file.filename).split('.')[1].lower()
        new_path = os.path.join(MODEL_LOCATION, secure_filename(name) + '.' + file_extension)
        file.save(new_path)

        # Save Model Database Entry

    
        # Return model info
        return {'model_id': model_id, 'name': name}, 201
    
@app.route("/videos", methods=['POST'])
def upload_video():
    if request.method == 'POST':
        if 'video_file' not in request.files:
            return "File part not found in request", 400
        file = request.files['video_file']
        if file.filename == '':
            return "No file uploaded", 400
        if not file or not validate_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return "Invalid file extension", 400
        file_bytes = file.read()
        # Generate Metadata for video
        video_id = get_sha256(file_bytes)
        name = get_basename(file.filename)
        # Get Number of Video Frames
        num_frames = 25
        for i in range(0,25):
            socketio.send("Frame {i}")

        # Save Video Database Entry

        # Return video info
        return {'video_id': video_id, 'name': name, 'num_frames': num_frames}


def _fake_worker(id):
    print("Before count")
    for i in range(0,25):
        socketio.sleep(1)
        socketio.send(f"{id}: Frame {i}")
    print("Post count")

@app.route('/videos/<video_id>')
def get_video(video_id):
    socketio.start_background_task(_fake_worker, (video_id,))
    return "response", 200
            

# Output Connection Events to Console
@socketio.on('connect')
def notify_connection(auth):
    print("Client Connected!")

# Test SocketIO Functions: https://piehost.com/socketio-tester?v=4&url=http://localhost:5000
@socketio.event
def test_socket(data):
    print("Received Test Data: ", data)
    emit("test_response", data)


# Main socket event that receives frames and processes them using the currently active AI model
frame_count = 0
@socketio.event
def predict_objects(base64_frame):
    # Convert frame to numpy array
    nparr_frame = Base64_Transcoder.data_url_to_nparray(base64_frame)
    # Run predictions on numpy array frame
    object_detection_model.predict_objects_in(nparr_frame)
    # Get image with boxes as numpy array
    nparr_processed_frame = object_detection_model.get_image()
    # Convert annotated numpy array image back to base64
    base64_processed_frame = Base64_Transcoder.nparray_to_data_url(nparr_processed_frame)
    # Send annotated image to client

    emit("receive_annotated_frame", base64_processed_frame)
    emit("objects_json_response", object_detection_model.get_boxes_json())
    global frame_count
    frame_count += 1
    print(f"Sent frame. {frame_count}")

# Socket event to test the base64 transcoder functions
@socketio.event
def test_base64_transcoder(base64_image):
    # Convert base64 input to numpy array
    nparr_image = Base64_Transcoder.data_url_to_nparray(base64_image)
    # Convert numpy array back to base64 to verify lossless conversion
    base64_response = Base64_Transcoder.nparray_to_base64(nparr_image)
    # Respond with converted data
    emit(base64_response)

# Socket event that will respond with the JSON of objects
@socketio.event
def get_json():
    emit(object_detection_model.get_boxes_json)

if __name__ == '__main__':
    socketio.run(app, host = hostname, port = port)

