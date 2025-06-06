from flask import Flask, send_from_directory
from flask_socketio import SocketIO, send, emit
from ai_modules.yolo11s import Yolo11s
from utilities.base64_transcoder import Base64_Transcoder
import argparse
from ai_modules.tensorflow import TensorFlowModel

# Defines this file for flask as the WSGI app
app = Flask(__name__)

parser = argparse.ArgumentParser(description='Run Railway Object Detection ')

parser.add_argument('--address', dest='hostname', default="localhost", help="Network interface to start the socketIO/webserver on.")
parser.add_argument('--port', dest='port', default='5000', help="Specifies the port for the socketIO/web server to start on.")

args = parser.parse_args()

hostname = args.hostname
port = args.port

socketio = SocketIO(app, cors_allowed_origins=["https://piehost.com",f"http://{hostname}:{port}"], max_http_buffer_size=10*1000000)

yolo = Yolo11s()
#tensor = TensorFlowModel("ssd_mobilenet_v2_coco_2018_05_09/ssd_mobilenet_v2_coco_2018_05_09/saved_model/saved_model.pb")

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)


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
    yolo.predict_objects_in(nparr_frame)
    # Get image with boxes as numpy array
    nparr_processed_frame = yolo.get_image()
    # Convert annotated numpy array image back to base64
    base64_processed_frame = Base64_Transcoder.nparray_to_data_url(nparr_processed_frame)
    # Send annotated image to client

    emit("receive_annotated_frame", base64_processed_frame)
    emit("objects_json_response", yolo.get_boxes_json())
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
    emit(yolo.get_boxes_json)

if __name__ == '__main__':
    socketio.run(app, host = hostname, port = port)

