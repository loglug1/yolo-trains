from flask import Flask, send_from_directory
from flask_socketio import SocketIO, send, emit
from ai_modules.yolo11s import Yolo11s
from utilities.base64_transcoder import Base64_Transcoder

# Defines this file for flask as the WSGI app
app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="https://piehost.com")

yolo = Yolo11s()

# Serves content from the static directory to the root URL using flask
@app.route("/")
@app.route("/<path:file>")
def static_page(file = "index.html"):
    return send_from_directory("static", file)

# Test SocketIO Functions: https://piehost.com/socketio-tester?v=4&url=http://localhost:5000
@socketio.event
def predict_objects(base64_frame):
    nparr_frame = Base64_Transcoder.base64_to_nparray(base64_frame)
    yolo.predict_objects_in(nparr_frame)
    nparr_processed_frame = yolo.get_image()
    base64_processed_frame = Base64_Transcoder.nparray_to_base64(nparr_processed_frame)
    emit(base64_processed_frame)

@socketio.event
def test_base64_transcoder(base64_image):
    nparr_image = Base64_Transcoder.base64_to_nparray(base64_image)
    base64_response = Base64_Transcoder.base64_to_nparray(nparr_image)
    emit(base64_response)

@socketio.event
def get_json():
    emit(yolo.get_boxes_json)

if __name__ == '__main__':
    socketio.run(app)

