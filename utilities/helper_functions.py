import sqlite3
import hashlib
import cv2
import os

def db_connect(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    return conn, cursor

# Function to get file hashes (used as ids for videos and models)
def get_sha256(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

# Function to pull frame from video file
def get_frame_from_file(video_path, frame_num):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    success, image = cap.read()
    cap.release()
    if success:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Convert Frame Extracted using CV2 to RGB (Because of historical reasons. Ask ChatGPT why.)
    else:
        raise FileNotFoundError(video_path)

# Function to Get Number of Frames in Video File
def get_num_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(video_path)
    num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    return num_frames

# Functions used in validating uploaded files
def validate_extension(filename, extension_list):
    return '.' in filename and filename.split('.')[1].lower() in extension_list
def get_basename(filename):
    return filename.split('.')[0]

# Create folders if they do not exist
def create_folder_when_missing(path):
    if not os.path.exists(path):
        os.makedirs(path)