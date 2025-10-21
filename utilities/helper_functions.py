from db_connect.database import ProcessedFrame
import sqlite3
import hashlib
import numpy
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

def get_framerate_from_file(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(video_path)
    framerate = cap.get(cv2.CAP_PROP_FPS)
    return framerate

# Functions used in validating uploaded files
def validate_extension(filename, extension_list):
    return '.' in filename and filename.split('.')[1].lower() in extension_list
def get_basename(filename):
    return filename.split('.')[0]

# Create folders if they do not exist
def create_folder_when_missing(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_color_from_word(word):
    # Hash the word to a hexadecimal string
    hash_object = hashlib.md5(word.encode())
    digested_hash = hash_object.hexdigest()

    return (int(digested_hash[0:2], 16), int(digested_hash[2:4], 16), int(digested_hash[4:6], 16))

def get_hex_from_word(word):
    # Hash the word to a hexadecimal string
    hash_object = hashlib.md5(word.encode())
    digested_hash = hash_object.hexdigest()

    return f"#{digested_hash[0:6]}"

# Function to draw objects onto frame
def get_annotated_frame(processed_frame: ProcessedFrame, frame_img: numpy.ndarray) :
    if processed_frame.objects is None :
        return frame_img
    
    updated_frame = frame_img
    for obj in processed_frame.objects :
        tl_pt = (round(obj.x1), round(obj.y1))
        br_pt = (round(obj.x2), round(obj.y2))
        #bc = colors(obj.class_id if obj.class_id is not None else 0, bgr=True)
        color = get_color_from_word(obj.type)

        updated_frame = cv2.rectangle(updated_frame, tl_pt, br_pt, color, 2)

        # Code to add text labels:
        label = f"{obj.type}: {(obj.confidence * 100):.2f}%"
        color = get_color_from_word(obj.type)
        # For the text background
        # Finds space required by the text so that we can put a background with that amount of width.
        (w, h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)

        # Prints the text.
        updated_frame = cv2.rectangle(updated_frame, (tl_pt[0], tl_pt[1] - 20), (tl_pt[0] + w, tl_pt[1]), color, -1)
        updated_frame = cv2.putText(updated_frame, label, (tl_pt[0], tl_pt[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return updated_frame