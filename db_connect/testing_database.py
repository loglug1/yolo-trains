from database import *
import uuid
import sqlite3

DATABASE = 'testing'

# setup cursor and connection
conn = sqlite3.connect(f'{DATABASE}.db')
cursor = conn.cursor()

# create tables
print(create_tables(conn, cursor))


# data for testing
model_uuid = "123e4567-e89b-12d3-a456-4266141740w1"
video_uuid = "123e4567-e89b-12d3-a456-4266141740w1"
frame_uuid = "123e4567-e89b-12d3-a456-4266141740w1"

frame_uuid2 = "123e4567-e89b-12d3-a456-4266141740w2"

# test inserts and queries
print(insert_object_type(conn, cursor, model_uuid, 1, "person"))

print(insert_video(conn, cursor, video_uuid, "Sample Video", "https://video.com"))
print(insert_model(conn, cursor, model_uuid, "Sample Model", "https://model.com"))
print(insert_frame(conn, cursor, frame_uuid, video_uuid, 1))
print(insert_frame(conn, cursor, frame_uuid2, video_uuid, 2))
print(insert_processed_frame(conn, cursor, frame_uuid, model_uuid))
print(insert_object(conn, cursor, 1, frame_uuid, model_uuid, 0.95, 0.1, 0.1, 0.5, 0.5))
print(insert_object(conn, cursor, 1, frame_uuid, model_uuid, 0.94, 0.12, 0.1, 0.5, 0.5))


print(insert_model(conn, cursor, str(uuid.uuid4()), "Sample Model", "https://model.com"))

print(get_video_list(conn, cursor))
print(get_video(conn, cursor, video_uuid))
print(get_model_list(conn, cursor))
print(get_model(conn, cursor, model_uuid))
print(get_processed_frame(conn, cursor, video_uuid, model_uuid, 1))
print(get_processed_frame_with_objects(conn, cursor, video_uuid, model_uuid, 1))
print(get_processed_frame(conn, cursor, video_uuid, model_uuid, 2)) # this should error out
print(get_processed_frame_with_objects(conn, cursor, video_uuid, model_uuid, 2)) # this should error out
print(get_processed_frame_list_with_objects(conn, cursor, video_uuid, model_uuid))
print(get_processed_frame_list(conn, cursor, video_uuid, model_uuid))
print(get_object_type_list(conn, cursor))
print(get_object_type_list_by_model_by_video(conn, cursor, model_uuid, video_uuid))
print(get_object_type(conn, cursor, 1))
print(get_frame(conn, cursor, video_uuid, 1))
print(get_frame_with_objects(conn, cursor, video_uuid, model_uuid, 1))
print(get_frame_list(conn, cursor, video_uuid))
print(get_frame_list_with_objects(conn, cursor, video_uuid, model_uuid))
print(get_unprocessed_frame_list(conn, cursor, video_uuid, model_uuid))


object_types = get_object_type_list(conn, cursor).object_types

frame = get_frame_with_objects(conn, cursor, video_uuid, model_uuid, 1).frame
print(frame.objects[0])


frames = [
  ("frame_uuid1", "video_uuid1", 1),
  ("frame_uuid2", "video_uuid1", 2),
  ("frame_uuid3", "video_uuid1", 3),
]

p_frames = [
  ("frame_uuid1", "model_uuid1"),
  ("frame_uuid3", "model_uuid1")
]

print(insert_frames(conn, cursor, frames))
print(insert_processed_frames(conn, cursor, p_frames))
print(get_frame_list(conn, cursor, "video_uuid1"))
print(get_processed_frame_list(conn, cursor, "video_uuid1", "model_uuid1"))
print(get_unprocessed_frame_list(conn, cursor, "video_uuid1", "model_uuid1"))


# close connection
conn.close()