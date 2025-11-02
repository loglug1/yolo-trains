from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import os
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from ai_modules.abc_model import ObjectDetectionModel
from ai_modules.yolo11s import Yolo11s
from utilities.base64_transcoder import Base64_Transcoder
from utilities.helper_functions import db_connect, get_sha256, get_num_frames, get_basename, get_frame_from_file, validate_extension, create_folder_when_missing, get_annotated_frame, get_hex_from_word, get_framerate_from_file
from db_connect.database import Videos, Frame, Object, Model, ProcessedFrame, get_object_type_list_by_model_by_video, get_unprocessed_frame_list, get_processed_frame_list_with_objects, get_video_list as db_get_video_list, get_model_list as db_get_model_list, insert_frame, insert_video, create_tables, insert_model, get_video, get_frame_list, get_frame_list_with_objects, get_model, insert_object, insert_object_type, get_processed_frame as db_get_processed_frame, insert_processed_frame, get_frame, get_processed_frame_with_objects, insert_frames, get_processed_frame_history_with_objects
from db_connect.influx import influx_connect, insert_objects_influx
from utilities.secrets_handler import read_secret
import argparse
import uuid
import threading
import json
#from ai_modules.tensorflow import TensorFlowModel

# Defines this file for flask as the WSGI app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000 * 1000 # 2GB max model file size

# Environment Variables are prefered way to configure program
hostname = os.environ.get('ROD_HOSTNAME', '0.0.0.0')
port = os.environ.get('ROD_PORT', '5000')
upload_path = os.environ.get('ROD_DATA_PATH', 'uploads')
allowed_origins = os.environ.get('ROD_ALLOWED_ORIGINS', None)
if allowed_origins is not None:
    allowed_origins = allowed_origins.split(",")
else:
    allowed_origins = '*'

# Arg parser for legacy support
parser = argparse.ArgumentParser(description='Run Railway Object Detection ')
parser.add_argument('--address', dest='hostname', default=hostname, help="Network interface to start the socketIO/webserver on.")
parser.add_argument('--port', dest='port', default=port, help="Specifies the port for the socketIO/web server to start on.")
parser.add_argument('--uploads', dest='upload_path', default=upload_path, help="Specifies path to store uploaded files.")
args = parser.parse_args()
hostname = args.hostname
port = args.port
upload_path = args.upload_path

# Get Influx Config from Environment
influxdb_token = os.environ.get('INFLUXDB_TOKEN', '')
influxdb_org = os.environ.get('INFLUXDB_ORG', '')
influxdb_url = os.environ.get('INFLUXDB_URL', '')
influxdb_bucket = os.environ.get('INFLUXDB_BUCKET', '')

# Read Influx Token from secret file if desired
influxdb_token_secret = read_secret(os.environ.get('INFLUXDB_TOKEN_FILE', ''))
if influxdb_token_secret is not None:
    influxdb_token = influxdb_token_secret

# Constants defining what file types can be uploaded
ALLOWED_MODEL_EXTENSIONS = ['pt']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'mkv']

# Constants defining file paths
MODEL_LOCATION = f"{upload_path}/models/"
VIDEO_LOCATION = f"{upload_path}/videos/"
DATABASE = f'{upload_path}/database.db'

# Ensure paths exists
create_folder_when_missing(upload_path)
create_folder_when_missing(MODEL_LOCATION)
create_folder_when_missing(VIDEO_LOCATION)

# Ensure that the database exists and contains default model
conn, cursor = db_connect(DATABASE)
create_tables(conn, cursor)
insert_model(conn, cursor, 'default', "Default Ultralytics Yolo Model", "ai_modules/ob_detect_models/yolo11s.pt")
conn.close()

tasks = list() # Used to keep track of tasks in progress

socketio = SocketIO(app, cors_allowed_origins=allowed_origins, max_http_buffer_size=10*1000000, async_mode='threading')

# ======================================== API ENDPOINTS =======================================

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

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
        try:
            file_bytes = file.read()
            file.seek(0)
            # Generate Metadata for model
            model_id = get_sha256(file_bytes)
            name = get_basename(file.filename)
            # Save Model to Blob Storage
            file_extension = secure_filename(file.filename).split('.')[1].lower()
            model_path = os.path.join(MODEL_LOCATION, secure_filename(name + '.' + file_extension))
            file.save(model_path)
            try:
                Yolo11s(model_path)
            except:
                os.remove(model_path)
                return "Error loading model file!", 400
            # Save Model Database Entry
            conn, cursor = db_connect(DATABASE)
            insert_model(conn, cursor,model_id, name, model_path)
            # Return model info
            return {'model_id': model_id, 'name': name}, 201
        except Exception as e:
            return e, 500
    
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
        try:
            file_bytes = file.read()
            file.seek(0)
            # Generate Metadata for video
            video_id = get_sha256(file_bytes)
            name = get_basename(file.filename)
            file_extension = secure_filename(file.filename).split('.')[1].lower()
            video_path = os.path.join(VIDEO_LOCATION, secure_filename(video_id + '.' + file_extension))
            # Save Video to Video Upload Location
            if os.path.exists(video_path):
                return "Filename already exists in upload location!", 409
            file.save(video_path)
            # Get Video Framerate
            framerate = get_framerate_from_file(video_path)
            # Save Video Database Entry (Happens before saving video to ensure that the video doesn't already exist)
            conn, cursor = db_connect(DATABASE)
            res = insert_video(conn, cursor, video_id, name, video_path, framerate)
            if res.status != 'success':
                conn.close()
                return res.message, 409
            # Get frame count and validate video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                os.remove(video_path)
                conn.close()
                return 'Invalid Video File', 400
            num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            # Insert Frames into Database
            frame_data = list()
            for frame_num in range(int(num_frames)):
                frame_data.append((str(uuid.uuid4()), video_id, frame_num))
            res = insert_frames(conn, cursor, frame_data)
            if res.status != 'success':
                conn.close()
                return res.message, 400
            # Return video info
            return {'video_id': video_id, 'name': name, 'num_frames': num_frames}, 201
        except Exception as e:
            conn.close()
            return e, 500
        
# Get list of videos available
@app.route('/videos', methods=['GET']) 
def get_video_list():
    # Get videos from database
    conn, cursor = db_connect(DATABASE)
    res = db_get_video_list(conn, cursor)
    conn.close()
    # Return Videos
    if res.response.status == 'success':
        video_list = [{'video_id': video.video_uuid, 'title': video.title} for video in res.videos]
        return jsonify(video_list), 200
    else:
        return res.response.message, 500

# Get list of models available
@app.route('/models', methods=['GET']) 
def get_model_list():
    # Get models from database
    conn, cursor = db_connect(DATABASE)
    res = db_get_model_list(conn, cursor)
    conn.close()
    # Return Models
    if res.response.status == 'success':
        model_list = [{'model_id': model.model_uuid, 'title': model.title} for model in res.models]
        return jsonify(model_list), 200
    else:
        return res.response.message, 500
    
# Get list of object classes found in specific model/video
@app.route('/objects/<model_id>/<video_id>', methods=['GET'])
def fetch_object_types(model_id, video_id):
    # Get object types from database
    conn, cursor = db_connect(DATABASE)
    res = get_object_type_list_by_model_by_video(conn, cursor, model_id, video_id)
    conn.close()
    if res.response.status != 'success':
        return res.response.message, 500
    # Return Object Types
    model_list = [{'name': type.name, 'color': get_hex_from_word(type.name)} for type in res.object_types]
    return jsonify(model_list), 200

# Get All Unprocessed Frames for Video
@app.route('/videos/<video_id>', methods=['GET'])
def fetch_video(video_id):
    conn, cursor = db_connect(DATABASE)
    # Get Video Info
    res = get_video(conn, cursor, video_id)
    if res.response.status != 'success':
        return res.response.message, 500
    video = res.video
    # Get Number of Frames
    try:
        num_frames = get_num_frames(video.video_url)
    except FileNotFoundError as e:
        return "File not found: " + e, 500
    # Get Framelist
    res = get_frame_list(conn, cursor, video_id)
    if res.response.status != 'success':
        return res.response.message, 500
    frame_list = [frame.to_dict() for frame in res.frames]
    conn.close()
    return jsonify({'video_id': video_id, 'title': video.title, 'num_frames': num_frames, 'frames': frame_list}), 200

# Get all processed frames for this video (start processing or just return database)
@app.route('/models/<model_id>/<video_id>', methods=['GET']) 
def get_all_processed_frames(model_id, video_id):
    # Get Video Metadata from DB
    conn, cursor = db_connect(DATABASE)
    res = get_video(conn, cursor, video_id)
    conn.close()
    if res.response.status != 'success':
        return res.response.message, 500
    video = res.video
    # Get Number of Frames in Video
    try:
        num_frames = get_num_frames(video.video_url)
    except FileNotFoundError as e:
        return "File not found: " + e, 500
    # Get Processed Frames
    conn, cursor = db_connect(DATABASE)
    res = get_processed_frame_list_with_objects(conn, cursor, video_id, model_id)
    conn.close()
    if res.response.status != 'success':
        return res.response.message, 500
    processed_frames = [frame.to_dict() for frame in res.processed_frames]
    # Check if task already exists for model/video combo
    task_id = str(uuid.uuid5(uuid.NAMESPACE_URL, model_id + video_id)) # Creates a deterministic UUID based on the model and video ids
    with threading.Lock():
        task_started = task_id in tasks # Boolean (separate from if statement so it can be in a threading.Lock())
    if task_started:
        return {'connection_id': task_id, 'num_frames': num_frames, 'frames': processed_frames}, 200
    # Get Unprocessed Frames
    conn, cursor = db_connect(DATABASE)
    res = get_unprocessed_frame_list(conn, cursor, video_id, model_id)
    conn.close()
    if res.response.status != 'success' and "No unprocessed frames" not in res.response.message:
        return res.response.message, 500
    unprocessed_frames = res.frames
    # If there are unprocessed frames left, start the subroutine
    if len(unprocessed_frames) > 0:
        if not task_started:
            socketio.start_background_task(_process_all_frames, model_id, video, unprocessed_frames, task_id)
        return {'connection_id': task_id, 'num_frames': num_frames, 'frames': processed_frames}, 200
    return {'num_frames': num_frames, 'frames': processed_frames}, 200

# Get Specific Unprocessed Frame img element
@app.route('/videos/<video_id>/<int:frame_num>', defaults={'response_format': ''})
@app.route('/videos/<video_id>/<int:frame_num>/<string:response_format>', methods=['GET'])
def get_raw_frame(video_id, frame_num, response_format):
    conn, cursor = db_connect(DATABASE)
    res = get_video(conn, cursor, video_id)
    conn.close()
    if res.response.status != 'success':
        return res.response.message, 500
    if res.response.status == 'success' and 'not found.' in res.response.message:
        conn.close()
        return res.response.message, 404
    video_path = res.video.video_url
    try:
        image = get_frame_from_file(video_path, frame_num)
        data_url = Base64_Transcoder.nparray_to_data_url(image)
    except FileNotFoundError as e:
        return "File not found: " + e, 500
    if response_format == 'img':
        return f"<img src='{data_url}' alt='Unprocessed Frame' />", 200
    return {'video_id': video_id, 'frame_num': frame_num, 'image': data_url}, 200

# Get specific processed frame
@app.route('/models/<model_id>/<video_id>/<int:frame_num>', defaults={'min_conf': 0, 'max_conf': 1, 'response_format': ''})
@app.route('/models/<model_id>/<video_id>/<int:frame_num>/<float:min_conf>/<float:max_conf>', defaults={'response_format': ''})
@app.route('/models/<model_id>/<video_id>/<int:frame_num>/<float:min_conf>/<float:max_conf>/<string:response_format>', methods=['GET'])
def get_processed_frame(model_id, video_id, frame_num, min_conf, max_conf, response_format):
    # Get Model Metadata
    conn, cursor = db_connect(DATABASE)
    res = get_model(conn, cursor, model_id)
    if res.response.status != 'success':
        conn.close()
        return res.response.message, 500
    if res.response.status == 'success' and 'not found.' in res.response.message:
        conn.close()
        return res.response.message, 404
    model = res.model
    # Get Video Metadata
    res = get_video(conn, cursor, video_id)
    if res.response.status != 'success':
        conn.close()
        return res.response.message, 500
    if res.response.status == 'success' and 'not found.' in res.response.message:
        conn.close()
        return res.response.message, 404
    video = res.video
    res = get_processed_frame_with_objects(conn, cursor, video_id, model_id, frame_num)
    if res.response.status == 'error':
        conn.close()
        return res.response.message, 500
    if "not found." in res.response.message:
        # Get unprocessed frame and process if not found
        res = get_frame(conn, cursor, video_id, frame_num)
        if res.response.status != 'success':
            conn.close()
            return res.response.message, 500
        conn.close()
        frame_dict = process_single_frame(model, video, res.frame, min_conf, max_conf)
    else:
        # Generate boxes image and return from DB if found
        conn.close()
        frame_dict = res.processed_frame.to_dict()
        try:
            image = get_frame_from_file(video.video_url, frame_num)
        except FileNotFoundError as e:
            return "File not found: " + e, 500
        frame_dict['image'] = Base64_Transcoder.nparray_to_data_url(get_annotated_frame(res.processed_frame, image, min_conf, max_conf))
    # Return frame_dict in desired format
    if response_format == 'img':
        return f"<img src='{frame_dict['image']}' alt='Processed Frame' />", 200
    return frame_dict, 200

# Get Specific Processed Frame History
@app.route('/models/<model_id>/<video_id>/<int:frame_num>/history', methods=['GET']) 
def get_frame_prediction_history(model_id, video_id, frame_num):
    conn, cursor = db_connect(DATABASE)
    res = get_processed_frame_history_with_objects(conn, cursor, video_id, model_id, frame_num)
    conn.close()
    if res.response.status != 'success':
        return res.response.message, 500
    processed_frames = [frame.to_dict() for frame in res.processed_frames]
    return {'frames': processed_frames}, 200

# ======================================== Frame Processing Functions ==========================================

def _process_all_frames(model_id: str, video: Videos, frames: list[Frame], task_id: str):
    with threading.Lock():
        if task_id in tasks:
            return
        tasks.append(task_id) # Mark as active task for reconnection
    # Get Model Metadata
    conn, cursor = db_connect(DATABASE)
    res = get_model(conn, cursor, model_id)
    if res.response.status != 'success':
        conn.close()
        return
    model = res.model
    # Load object detection model with model file
    object_detection_model = Yolo11s(res.model.model_url)
    for frame in frames:
        processed_frame = process_frame_helper(model, video, frame, object_detection_model)
        socketio.emit('processed_frame', json.dumps(processed_frame), to=task_id)
    # Mark as Complete
    with threading.Lock():
        tasks.remove(task_id)
    conn.close()

def process_single_frame(model: Model, video: Videos, frame: Frame, min_conf: float = 0, max_conf: float = 1):
    object_detection_model = Yolo11s(model.model_url)
    processed_frame = process_frame_helper(model, video, frame, object_detection_model, min_conf, max_conf)
    return processed_frame

def process_frame_helper(model: Model, video: Videos, frame: Frame, object_detection_model: ObjectDetectionModel, min_conf: float = 0, max_conf: float = 1):
    # Get Frame Image
    frame_image = get_frame_from_file(video.video_url, frame.frame_number)
    # Run predictions on frame
    object_detection_model.predict_objects_in(frame_image)
    # Write detected objects to database
    objects = json.loads(object_detection_model.get_boxes_json())
    converted_objects = list[Object]()
    conn, cursor = db_connect(DATABASE)
    for object in objects:
        #converted_objects.append({'type': object['name'], 'confidence': object['confidence'], 'x1': object['box']['x1'], 'y1': object['box']['y1'], 'x2': object['box']['x2'], 'y2': object['box']['y2']})
        converted_objects.append(Object(object['name'], object['confidence'], object['box']['x1'], object['box']['y1'], object['box']['x2'], object['box']['y2'], object['class']))
        insert_object_type(conn, cursor, model.model_uuid, object['class'], object['name'], commit = False)
        res = insert_object(conn, cursor, object['class'], frame.frame_uuid, model.model_uuid, object['confidence'], object['box']['x1'], object['box']['y1'], object['box']['x2'], object['box']['y2'], commit = False)
        if res.status != 'success':
            print("Error inserting Object: ", res.message)
            continue
    if influxdb_url != '':
        client, writer = influx_connect(influxdb_token, influxdb_org, influxdb_url) # These are from environment variables parsed at the top of this file
        res = insert_objects_influx(client, writer, influxdb_bucket, model, video, frame, converted_objects)
        if res.status != 'success':
            print("Influx error: ", res.message)
    # Mark Frame as Processed
    res = insert_processed_frame(conn, cursor, frame.frame_uuid, model.model_uuid)
    if res.status != 'success':
        print("Error saving frame: ", res.message)
    conn.close()
    # Get Frame with boxes drawn
    pframe = ProcessedFrame(frame.frame_uuid, video.video_uuid, model.model_uuid, frame.frame_number, converted_objects)
    annotated_image = get_annotated_frame(pframe, frame_image, min_conf, max_conf)
    return {'frame_num': frame.frame_number, 'image': Base64_Transcoder.nparray_to_data_url(annotated_image), 'objects': [vars(converted_object) for converted_object in converted_objects]}

# ====================================== SocketIO Event Handlers ==============================================

@socketio.on('join')
def on_join(room_id):
    print(f"Client joined {room_id}.")
    join_room(room_id)
    send(f"Joined {room_id}.")
    
@socketio.on('leave')
def on_leave(room_id):
    print(f"Client left {room_id}.")
    leave_room(room_id)
    send(f"Left {room_id}.")

@app.route('/test/socketio/<room_id>')
def test_room_send(room_id):
    socketio.send("Test message", to=room_id)
    return '', 200

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
    socketio.run(app, host = hostname, port = port, allow_unsafe_werkzeug=True)

