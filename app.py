from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import os
from flask_socketio import SocketIO, send, emit
from ai_modules.yolo11s import Yolo11s
from db_connect.database import get_frame_with_objects, get_video_list as db_get_video_list, get_model_list as db_get_model_list, insert_frame, insert_video, create_tables, insert_model
from utilities.base64_transcoder import Base64_Transcoder
import sqlite3
import argparse
import uuid
import hashlib
import threading
#from ai_modules.tensorflow import TensorFlowModel

# Defines this file for flask as the WSGI app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000 * 1000 # 2GB max model file size

parser = argparse.ArgumentParser(description='Run Railway Object Detection ')

parser.add_argument('--address', dest='hostname', default="localhost", help="Network interface to start the socketIO/webserver on.")
parser.add_argument('--port', dest='port', default='5000', help="Specifies the port for the socketIO/web server to start on.")
parser.add_argument('--uploads', dest='upload_path', default='uploads', help="Specifies path to store uploaded files.")

args = parser.parse_args()

hostname = args.hostname
port = args.port
upload_path = args.upload_path
DATABASE = f'{upload_path}/database'

socketio = SocketIO(app, cors_allowed_origins=["https://piehost.com",f"http://{hostname}:{port}"], max_http_buffer_size=10*1000000, async_mode='threading')

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

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

# Constant defining what file types can be uploaded
ALLOWED_MODEL_EXTENSIONS = ['pt']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mkv']
MODEL_LOCATION = f"{upload_path}/models/"
VIDEO_LOCATION = f"{upload_path}/videos/"
FRAME_LOCATION = f"{upload_path}/frames/"

# Functions used in validating uploaded files
def validate_extension(filename, extension_list):
    return '.' in filename and filename.split('.')[1].lower() in extension_list
def get_basename(filename):
    return filename.split('.')[0]

def db_connect():
    conn = sqlite3.connect(f'{DATABASE}.db')
    cursor = conn.cursor()
    return conn, cursor

tasks = list() # Used to keep track of tasks in progress

# ======================================== API ENDPOINTS =======================================

# Upload a model, model file must be in model_file field of form
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
        model_path = os.path.join(MODEL_LOCATION, secure_filename(name + '.' + file_extension))
        file.save(model_path)

        # Save Model Database Entry
        conn, cursor = db_connect()
        insert_model(conn, cursor,model_id, name, model_path)
    
        # Return model info
        return {'model_id': model_id, 'name': name}, 201
    
# Upload a video, video file must be in video_file field of form
@app.route("/videos", methods=['POST'])
def upload_video():
    if request.method == 'POST':
        if 'video_file' not in request.files:
            return "File part not found in request", 400
        file = request.files['video_file']
        if file.filename == '':
            return "No file uploaded", 400
        if not file or not validate_extension(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return f"Invalid file extension: {file.filename}", 400
        file_bytes = file.read()
        file.seek(0)

        # Generate Metadata for video
        video_id = get_sha256(file_bytes)
        name = get_basename(file.filename)

        # Save Video to Video Upload Location
        file_extension = secure_filename(file.filename).split('.')[1].lower()
        video_path = os.path.join(VIDEO_LOCATION, secure_filename(video_id))
        file.save(video_path)

        # Get frame count
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            os.remove(video_path)
            return 'Invalid Video File', 400
        num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # Save Video Database Entry
        conn, cursor = db_connect()
        res = insert_video(conn, cursor, video_id, name)
        conn.close()
        if res.status != 'success':
            return res.message, 409
        
        # frame_counter = -1
        # while True:
        #     success, frame = cap.read()
        #     if not success: # If getting next frame fails
        #         break
        #     frame_counter += 1
        #     frame_id = str(uuid.uuid4())
        #     frame_path = os.path.join(FRAME_LOCATION, secure_filename(frame_id + '.jpeg'))
        #     cv2.imwrite(frame_path, frame)
        #     insert_frame(conn, cursor, frame_id, video_id, frame_counter, frame_path)
        # cap.release()

        # Return video info
        return {'video_id': video_id, 'name': name, 'num_frames': num_frames}, 201

@app.route('/videos/<video_id>/<int:frame_num>', methods=['GET'])
def get_raw_frame(video_id, frame_num):
    conn, cursor = db_connect()
    cap = cv2.VideoCapture(VIDEO_LOCATION + video_id)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    success, image = cap.read()
    if success:
        return f"<img src='{Base64_Transcoder.nparray_to_data_url(image)}' alt='fake alt' />", 200

@app.route('/videos', methods=['GET']) # Get list of videos available
def get_video_list():
    # Get videos from database
    conn, cursor = db_connect()
    res = db_get_video_list(conn, cursor)
    conn.close()
    # Return Videos
    if res.response.status == 'success':
        return jsonify(res.videos), 200
    else:
        return res.response.message, 500 
    #return jsonify(list({'video_id': 'video1', 'name': 'Cool Video', 'num_frames': 10}, {'video_id': 'video2', 'name': 'Sad Video', 'num_frames': 35}, {'video_id': 'video3', 'name': 'Fun Video', 'num_frames': 1000}))

@app.route('/models', methods=['GET']) # Get list of models available
def get_model_list():
    # Get models from database
    conn, cursor = db_connect()
    res = db_get_model_list(conn, cursor)
    conn.close()
    # Return Models
    if res.response.status == 'success':
        return jsonify(res.models), 200
    else:
        return res.response.message, 500
    #return jsonify(list({'model_id': 'model1', 'name': 'Cool Model'}, {'model_id': 'model2', 'name': 'Fun Model'}, {'model_id': 'model3', 'name': 'Sad Model'}))

@app.route('/models/<model_id>/<video_id>', methods=['GET']) # Get all frames for this video (start processing or just return database)
def get_all_processed_frames(model_id, video_id):
    # Get Video Metadata from DB
    # Get Frames + Objects from DB
    task_id = str(uuid.uuid5(uuid.NAMESPACE_URL, model_id + video_id)) # Creates a deterministic UUID based on the model and video ids
    
    with threading.Lock():
        task_started = task_id in tasks
    
    if not task_started:
        socketio.start_background_task(_process_all_frames, (model_id, video_id, task_id))
        return {'connection_id': task_id}, 200
    else:
        conn, cursor = db_connect()


@app.route('/models/<model_id>/<video_id>/<frame_id>', methods=['GET']) # Get specific processed frame
def get_processed_frame(model_id, video_id, frame_id):
    conn, cursor = db_connect()
    res = get_frame_with_objects(conn, cursor, video_id, model_id, frame_id)
    if res.response.status == 'error' or res.frame.objects[0].type == 'none':
        return
    conn.close()
    process_single_frame(model_id, video_id, frame_id)

# ======================================== Background Thread Functions ==========================================

def _process_all_frames(model_id, video_id, task_id):

    with threading.Lock():
        if task_id in tasks:
            return
        tasks.append(task_id) # Mark as active task for reconnection
    
    object_detection_model = Yolo11s()
    frames = () # Database call gets video and pulls frames
    for frame in frames:
        # Convert frame to numpy array
        nparr_frame = ()
        # Run predictions on numpy array frame
        object_detection_model.predict_objects_in(nparr_frame)
        # Get image with boxes as numpy array
        nparr_processed_frame = object_detection_model.get_image()
        # Convert annotated numpy array image back to base64
        base64_processed_frame = Base64_Transcoder.nparray_to_data_url(nparr_processed_frame)
        socketio.send(base64_processed_frame, to=task_id)
        # Write detected objects to database
    
    with threading.Lock():
        tasks.remove(task_id)


def process_single_frame():
    object_detection_model = Yolo11s()

def _fake_worker(id):
    print("Before count")
    for i in range(0,25):
        socketio.sleep(1)
        socketio.send(f"{id}: Frame {i}")
    print("Post count")

# ====================================== SocketIO Event Handlers ==============================================

@socketio.on('join')
def on_join(data):
    room_id = data['connection_id']
    socketio.join_room(room_id)

# =========================================== MISC ===================================================

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
    object_detection_model = Yolo11s()
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

if __name__ == '__main__':
    conn, cursor = db_connect()
    create_tables(conn, cursor)
    conn.close()
    socketio.run(app, host = hostname, port = port)

