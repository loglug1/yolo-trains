import pytest
import os

# ======================================== DATABASE TESTING ===========================================
import sqlite3
from db_connect.database import *

# Fixture to set up and tear down the database connection for tests
@pytest.fixture(scope="class", autouse=True)
def db_connection(request):
  DATABASE = "testing"

  if os.path.exists(f"{DATABASE}.db"):
    os.remove(f"{DATABASE}.db")

  conn = sqlite3.connect(f"{DATABASE}.db")
  cursor = conn.cursor()

  request.cls.conn = conn
  request.cls.cursor = cursor

  request.cls.model_uuid = "123e4567-e89b-12d3-a456-4266141740w1"
  request.cls.video_uuid = "123e4567-e89b-12d3-a456-4266141740w1"
  request.cls.frame_uuid = "123e4567-e89b-12d3-a456-4266141740w1"
  request.cls.frame_uuid2 = "123e4567-e89b-12d3-a456-4266141740w2"

  assert create_tables(conn, cursor).status == "success"

  yield

  conn.close()
  if os.path.exists(f"{DATABASE}.db"):
    os.remove(f"{DATABASE}.db")


# Test class for database definitions
@pytest.mark.usefixtures("db_connection")
class TestDatabaseDefinitions :
  def test_insert_video(self):
    assert insert_video(self.conn, self.cursor, self.video_uuid, "Sample Video", "https://video.com", 30.0).status == "success"
    assert insert_video(self.conn, self.cursor, self.video_uuid, "Sample Video", "https://video.com", 30.0).status == "error"

  def test_insert_model(self):
    assert insert_model(self.conn, self.cursor, self.model_uuid, "Sample Model", "https://model.com").status == "success"
    assert insert_model(self.conn, self.cursor, self.model_uuid, "Sample Model", "https://model.com").status == "error"

  def test_insert_frame(self):
    assert insert_frame(self.conn, self.cursor, self.frame_uuid, self.video_uuid, 1).status == "success"
    assert insert_frame(self.conn, self.cursor, self.frame_uuid, self.video_uuid, 1).status == "error"

  def test_insert_frames(self):
    assert insert_frames(self.conn, self.cursor, [[self.frame_uuid2, self.video_uuid, 2]]).status == "success"
    assert insert_frames(self.conn, self.cursor, [[self.frame_uuid2, self.video_uuid, 2]]).status == "error"

  def test_insert_processed_frame(self):
    assert insert_processed_frame(self.conn, self.cursor, self.frame_uuid, self.model_uuid).status == "success"
    assert insert_processed_frame(self.conn, self.cursor, self.frame_uuid, self.model_uuid).status == "error"

  def test_insert_processed_frames(self):
    assert insert_processed_frames(self.conn, self.cursor, [[self.frame_uuid2, self.model_uuid]]).status == "success"
    assert insert_processed_frames(self.conn, self.cursor, [[self.frame_uuid2, self.model_uuid]]).status == "error"

  def test_insert_object_type(self):
    assert insert_object_type(self.conn, self.cursor, self.model_uuid, 1, "person").status == "success"
    assert insert_object_type(self.conn, self.cursor, self.model_uuid, 1, "person").status == "error"

  def test_insert_object(self):
    assert insert_object(self.conn, self.cursor, 1, self.frame_uuid, self.model_uuid, 0.95, 0.1, 0.1, 0.5, 0.5).status == "success"
    assert insert_object(self.conn, self.cursor, 1, self.frame_uuid, self.model_uuid, 0.95, 0.1, 0.1, 0.5, 0.5).status == "error"

  def test_get_video(self):
    assert get_video(self.conn, self.cursor, self.video_uuid).response.status == "success"
    dummy = get_video(self.conn, self.cursor, "non_existent_uuid")
    assert dummy.response.status == "success"
    assert dummy.video is None
    assert get_video_list(self.conn, self.cursor).response.status == "success"

  def test_get_model(self):
    assert get_model(self.conn, self.cursor, self.model_uuid).response.status == "success"
    dummy = get_model(self.conn, self.cursor, "non_existent_uuid")
    assert dummy.response.status == "success"
    assert dummy.model is None
    assert get_model_list(self.conn, self.cursor).response.status == "success"

  def test_get_object_type(self):
    assert get_object_type(self.conn, self.cursor, 1).response.status == "success"
    dummy = get_object_type(self.conn, self.cursor, 999)
    assert dummy.response.status == "success"
    assert dummy.object_type is None
    assert get_object_type_list(self.conn, self.cursor).response.status == "success"
    assert get_object_type_list_by_model_by_video(self.conn, self.cursor, self.model_uuid, self.video_uuid).response.status == "success"

  def test_get_frame(self):
    assert get_frame(self.conn, self.cursor, self.video_uuid, 1).response.status == "success"
    dummy = get_frame(self.conn, self.cursor, self.video_uuid, 999)
    assert dummy.response.status == "success"
    assert dummy.frame is None
    assert get_frame_list(self.conn, self.cursor, self.video_uuid).response.status == "success"
    assert get_frame_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid, 1).response.status == "success"
    assert get_frame_list_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid).response.status == "success"
    assert get_unprocessed_frame_list(self.conn, self.cursor, self.video_uuid, self.model_uuid).response.status == "success"

  def test_get_processed_frame(self):
    assert get_processed_frame(self.conn, self.cursor, self.video_uuid, self.model_uuid, 1).response.status == "success"
    dummy = get_processed_frame(self.conn, self.cursor, self.video_uuid, self.model_uuid, 999)
    assert dummy.response.status == "success"
    assert dummy.processed_frame is None
    assert get_processed_frame_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid, 1).response.status == "success"
    dummy2 = get_processed_frame_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid, 999)
    assert dummy2.response.status == "success"
    assert dummy2.processed_frame is None
    assert get_processed_frame_list_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid).response.status == "success"
    assert get_processed_frame_list(self.conn, self.cursor, self.video_uuid, self.model_uuid).response.status == "success"
    assert get_processed_frame_history_with_objects(self.conn, self.cursor, self.video_uuid, self.model_uuid, 1).response.status == "success"

# ======================================== END DATABASE TESTING =======================================



