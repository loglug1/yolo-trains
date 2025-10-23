# STANDARD RESPONSE CLASS
class Response:
  def __init__(self, status: str, message: str):
    self.status = status
    self.message = message

  def __str__(self):
    return f"[{self.status.upper()}] {self.message}"


# CREATE TABLES AND INDEXES FUNCTION
def create_tables(conn, cursor) -> Response :
  queries = [
    f"""
      CREATE TABLE IF NOT EXISTS videos (
        video_uuid VARCHAR(16) UNIQUE PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        video_url VARCHAR(255) NOT NULL,
        frame_rate FLOAT NOT NULL
      );
    """, 

    f"""
      CREATE INDEX IF NOT EXISTS idx_title ON videos (title);
    """,

    f"""
      CREATE TABLE IF NOT EXISTS models (
        model_uuid VARCHAR(16) UNIQUE PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        model_url VARCHAR(255) NOT NULL
      );
    """, 

    f"""
      CREATE TABLE IF NOT EXISTS frames (
        frame_uuid VARCHAR(16) UNIQUE PRIMARY KEY,
        video_uuid REFERENCES videos(video_uuid),
        frame_number INTEGER NOT NULL,
        CONSTRAINT unique_frame UNIQUE (video_uuid, frame_number)
      );
    """, 

    f"""
      CREATE INDEX IF NOT EXISTS idx_frames_video ON frames (video_uuid);
    """,

    f"""
      CREATE TABLE IF NOT EXISTS processed_frames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_uuid REFERENCES frames(frame_uuid),
        model_uuid REFERENCES models(model_uuid),
        CONSTRAINT unique_frame UNIQUE (frame_uuid, model_uuid)
      );
    """,

    f"""
      CREATE INDEX IF NOT EXISTS idx_model_frame ON processed_frames (model_uuid, frame_uuid);
    """,

    f"""
      CREATE TABLE IF NOT EXISTS object_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_uuid REFERENCES models(model_uuid),
        class_id INTEGER NOT NULL,
        name VARCHAR(50) NOT NULL,
        CONSTRAINT unique_type UNIQUE (model_uuid, class_id)
      );
    """,

    f"""
      CREATE TABLE IF NOT EXISTS objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id REFERENCES object_types(id),
        frame_uuid REFERENCES frames(frame_uuid),
        model_uuid REFERENCES models(model_uuid),
        confidence FLOAT NOT NULL,
        x1 FLOAT NOT NULL,
        y1 FLOAT NOT NULL,
        x2 FLOAT NOT NULL,
        y2 FLOAT NOT NULL,
        CONSTRAINT unique_object UNIQUE (type_id, frame_uuid, model_uuid, x1, y1, x2, y2)
      );
    """,

    f"""
      CREATE INDEX IF NOT EXISTS idx_objects_model_frame ON objects (model_uuid, frame_uuid);
    """,

    f"""
      CREATE INDEX IF NOT EXISTS idx_objects_frame ON objects (frame_uuid);
    """,
  ]

  try :
    for query in queries :
      cursor.execute(query)
      conn.commit()
    return Response("success", "Tables established successfully.")

  except Exception as e :
    return Response("error", f"Create tables failed: {str(e)}")
  

# INSERT FUNCTIONS
def insert_video(conn, cursor, video_uuid: str, title: str, video_url: str, frame_rate: float) -> Response :
  try :
    cursor.execute("""INSERT INTO videos (video_uuid, title, video_url) VALUES (?, ?, ?, ?)""", (video_uuid, title, video_url, frame_rate))
    conn.commit()
    return Response("success", f"Video {video_uuid} inserted successfully.")

  except Exception as e :
    return Response("error", f"Insert video failed: {str(e)}")

def insert_model(conn, cursor, model_uuid: str, title: str, model_url: str) -> Response :
  try :
    cursor.execute("""INSERT INTO models (model_uuid, title, model_url) VALUES (?, ?, ?)""", (model_uuid, title, model_url))
    conn.commit()
    return Response("success", f"Model {model_uuid} inserted successfully.")
  
  except Exception as e :
    return Response("error", f"Insert model failed: {str(e)}")

def insert_frame(conn, cursor, frame_uuid: str, video_uuid: str, frame_number: int) -> Response :
  try :
    cursor.execute("""INSERT INTO frames (frame_uuid, video_uuid, frame_number) VALUES (?, ?, ?)""", (frame_uuid, video_uuid, frame_number))
    conn.commit()
    return Response("success", f"Frame {frame_uuid} inserted successfully.")

  except Exception as e :
    return Response("error", f"Insert frame failed: {str(e)}")

def insert_frames(conn, cursor, frame_data) -> Response :
  try :
    cursor.executemany("""INSERT INTO frames (frame_uuid, video_uuid, frame_number) VALUES (?, ?, ?)""", frame_data)
    conn.commit()
    return Response("success", f"Frames inserted successfully.")

  except Exception as e :
    return Response("error", f"Insert frames failed: {str(e)}")
  
def insert_processed_frame(conn, cursor, frame_uuid: str, model_uuid: str) -> Response :
  try :
    cursor.execute("""INSERT INTO processed_frames (frame_uuid, model_uuid) VALUES (?, ?)""", (frame_uuid, model_uuid))
    conn.commit()
    return Response("success", f"Processed frame {frame_uuid} with model {model_uuid} inserted successfully.")
  
  except Exception as e :
    return Response("error", f"Insert processed frame failed: {str(e)}")
  
def insert_processed_frames(conn, cursor, frame_data) -> Response :
  try :
    cursor.executemany("""INSERT INTO processed_frames (frame_uuid, model_uuid) VALUES (?, ?)""", frame_data)
    conn.commit()
    return Response("success", f"Processed frames inserted successfully.")
  
  except Exception as e :
    return Response("error", f"Insert processed frames failed: {str(e)}")

def insert_object(conn, cursor, class_id: int, frame_uuid: str, model_uuid: str, 
                    confidence: float, x1: float, y1: float, x2: float, y2: float) -> Response :
  try :
    cursor.execute("""INSERT INTO objects (type_id, frame_uuid, model_uuid, confidence, x1, y1, x2, y2) VALUES (
                    (SELECT id 
                    FROM object_types 
                    WHERE model_uuid = ? AND class_id = ? 
                    LIMIT 1),
                    ?, ?, ?, ?, ?, ?, ?)""", 
                    (model_uuid, class_id, frame_uuid, model_uuid, confidence, x1, y1, x2, y2))
    conn.commit()
    return Response("success", f"Object in frame {frame_uuid} inserted successfully.") 
  
  except Exception as e :
    return Response("error", f"Insert object failed: {str(e)}")

def insert_object_type(conn, cursor, model_uuid: str, class_id: int, name: str) -> Response :
  try :
    cursor.execute("""INSERT INTO object_types (model_uuid, class_id, name) VALUES (?, ?, ?)""", (model_uuid, class_id, name))
    conn.commit()
    return Response("success", f"Object type {name} inserted successfully.")
  
  except Exception as e :
    return Response("error", f"Insert object type failed: {str(e)}")


# QUERY VIDEO FUNCTIONS
# classes
class Videos:
  def __init__(self, video_uuid: str, title: str, video_url: str, frame_rate: float):
    self.video_uuid = video_uuid
    self.title = title
    self.video_url = video_url
    self.framerate = frame_rate

  def __str__(self):
    return f"[{self.video_uuid}] {self.title} {self.video_url} {self.framerate}fps"
  
class VideoResponse:
  def __init__(self, response: Response, video: Videos | None):
    self.response = response
    self.video = video

  def __str__(self):
    return str(self.response) + (f"\n{self.video}" if self.video else "")
  
class VideoListResponse:
  def __init__(self, response: Response, videos: list[Videos]):
    self.response = response
    self.videos = videos

  def __str__(self):
    return str(self.response) + ("\n" + "\n".join([str(video) for video in self.videos]) if self.videos else "")

# definitions
def get_video_list(conn, cursor) -> VideoListResponse :
  try :
    cursor.execute("SELECT video_uuid, title, video_url, frame_rate FROM videos")
    rows = cursor.fetchall()
    videos = [Videos(video_uuid=row[0], title=row[1], video_url=row[2], frame_rate=row[3]) for row in rows]
    return VideoListResponse(Response("success", "Videos fetched successfully."), videos)
  
  except Exception as e :
    return VideoListResponse(Response("error", f"Get video list failed: {str(e)}"), [])
  
def get_video(conn, cursor, video_uuid: str) -> VideoResponse :
  try :
    cursor.execute("SELECT video_uuid, title, video_url, frame_rate FROM videos WHERE video_uuid = ?", (video_uuid,))
    row = cursor.fetchone()
    if row :
      video = Videos(video_uuid=row[0], title=row[1], video_url=row[2], frame_rate=row[3])
      return VideoResponse(Response("success", f"Video {video_uuid} fetched successfully."), video)
    else :
      return VideoResponse(Response("success", f"Video {video_uuid} not found."), None)
  
  except Exception as e :
    return VideoResponse(Response("error", f"Get video failed: {str(e)}"), None)
  

# QUERY MODEL FUNCTIONS
# classes
class Model:
  def __init__(self, model_uuid: str, title: str, model_url: str):
    self.model_uuid = model_uuid
    self.title = title
    self.model_url = model_url

  def __str__(self):
    return f"[{self.model_uuid}] {self.title} ({self.model_url})"
  
class ModelResponse:
  def __init__(self, response: Response, model: Model | None):
    self.response = response
    self.model = model

  def __str__(self):
    return str(self.response) + (f"\n{self.model}" if self.model else "")
  
class ModelListResponse:
  def __init__(self, response: Response, models: list[Model]):
    self.response = response
    self.models = models

  def __str__(self):
    return str(self.response) + ("\n" + "\n".join([str(model) for model in self.models]) if self.models else "")
  
# definitions
def get_model_list(conn, cursor) -> ModelListResponse :
  try :
    cursor.execute("SELECT model_uuid, title, model_url FROM models")
    rows = cursor.fetchall()
    models = [Model(model_uuid=row[0], title=row[1], model_url=row[2]) for row in rows]
    return ModelListResponse(Response("success", "Models fetched successfully."), models)

  except Exception as e :
    return ModelListResponse(Response("error", f"Get model list failed: {str(e)}"), [])
  
def get_model(conn, cursor, model_uuid: str) -> ModelResponse :
  try :
    cursor.execute("SELECT model_uuid, title, model_url FROM models WHERE model_uuid = ?", (model_uuid,))
    row = cursor.fetchone()
    if row :
      model = Model(model_uuid=row[0], title=row[1], model_url=row[2])
      return ModelResponse(Response("success", f"Model {model_uuid} fetched successfully."), model)
    else :
      return ModelResponse(Response("success", f"Model {model_uuid} not found."), None)
    
  except Exception as e :
    return ModelResponse(Response("error", f"Get model failed: {str(e)}"), None)


# QUERY OBJECT-TYPES FUNCTIONS
# classes
class ObjectType:
  def __init__(self, type: int, name: str):
    self.type = type
    self.name = name

  def __str__(self):
    return f"[{self.type}] {self.name}"
  
class ObjectTypeResponse:
  def __init__(self, response: Response, object_type: ObjectType | None):
    self.response = response
    self.object_type = object_type

  def __str__(self):
    return str(self.response) + (f"\n{self.object_type}" if self.object_type else "")
  
class ObjectTypeListResponse:
  def __init__(self, response: Response, object_types: list[ObjectType]):
    self.response = response
    self.object_types = object_types

  def __str__(self):
    return str(self.response) + ("\n" + "\n".join([str(object_type) for object_type in self.object_types]) if self.object_types else "")
  
# definitions
def get_object_type_list(conn, cursor) -> ObjectTypeListResponse :
  try :
    cursor.execute("SELECT id, name FROM object_types")
    rows = cursor.fetchall()
    object_types = [ObjectType(type=row[0], name=row[1]) for row in rows]
    return ObjectTypeListResponse(Response("success", "Object types fetched successfully."), object_types)
  
  except Exception as e :
    return ObjectTypeListResponse(Response("error", f"Get object type list failed: {str(e)}"), [])
  
def get_object_type_list_by_model_by_video(conn, cursor, model_uuid: str, video_uuid: str) -> ObjectTypeListResponse :
  try :
    cursor.execute("""
      SELECT DISTINCT ot.id, ot.name
      FROM object_types ot
      JOIN objects o ON ot.id = o.type_id
      JOIN frames f ON o.frame_uuid = f.frame_uuid
      WHERE ot.model_uuid = ? AND f.video_uuid = ?
    """, (model_uuid, video_uuid))
    rows = cursor.fetchall()
    object_types = [ObjectType(type=row[0], name=row[1]) for row in rows]
    return ObjectTypeListResponse(Response("success", f"Object types for model {model_uuid} and video {video_uuid} fetched successfully."), object_types)
  
  except Exception as e :
    return ObjectTypeListResponse(Response("error", f"Get object type list by model and video failed: {str(e)}"), [])
  
def get_object_type(conn, cursor, type: int) -> ObjectTypeResponse :
  try :
    cursor.execute("SELECT id, name FROM object_types WHERE id = ?", (type,))
    row = cursor.fetchone()
    if row :
      object_type = ObjectType(type=row[0], name=row[1])
      return ObjectTypeResponse(Response("success", f"Object type {type} fetched successfully."), object_type)
    else :
      return ObjectTypeResponse(Response("success", f"Object type {type} not found."), None) 
    
  except Exception as e :
    return ObjectTypeResponse(Response("error", f"Get object type failed: {str(e)}"), None)
  

# QUERY FRAMES AND OBJECTS FUNCTIONS
# classes
class Object:
  def __init__(self, type: str, confidence: float, x1: float, y1: float, x2: float, y2: float, class_id: int):
    self.type = type
    self.confidence = confidence
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.class_id = class_id

  def __str__(self):
    return f"Type: {self.type}, Confidence: {self.confidence}, Bound: ({self.x1}, {self.y1}, {self.x2}, {self.y2})"
  
  __repr__ = __str__

class Frame:
  def __init__(self, frame_uuid: str, video_uuid: str, frame_number: int, objects: list[Object] = []):
    self.frame_uuid = frame_uuid
    self.video_uuid = video_uuid
    self.frame_number = frame_number
    self.objects: list[Object] = []

  def __str__(self):
    return f"[{self.frame_uuid}] Video: {self.video_uuid}, Frame Number: {self.frame_number}" + (f", Objects: {len(self.objects)}" if self.objects else "")
  
  def add_objects(self, objects: list[Object]):
    self.objects.extend(objects)

  def add_object(self, object: Object):
    self.objects.append(object)

  def to_dict(self) -> dict:
    frame_dict = {'frame_num': self.frame_number, 'objects': [o.__dict__ for o in self.objects]}
    return frame_dict

class FrameResponse:
  def __init__(self, response: Response, video_url: str | None, frame: Frame | None):
    self.response = response
    self.video_url = video_url
    self.frame = frame
  
  def __str__(self):
    return str(self.response) + (f"\n{self.video_url}" if self.video_url else "") + (f"\n{self.frame}" if self.frame else "")
  
class FrameListResponse:
  def __init__(self, response: Response, video_url: str | None, frames: list[Frame]):
    self.response = response
    self.video_url = video_url
    self.frames = frames

  def __str__(self):
    return str(self.response) + (f"\n{self.video_url}" if self.video_url else "") + ("\n" + "\n".join([str(frame) for frame in self.frames]) if self.frames else "")
  
# definitions
def get_frame(conn, cursor, video_uuid: str, frame_number: int) -> FrameResponse :
  try :
    cursor.execute("SELECT video_url FROM videos WHERE video_uuid = ?", (video_uuid,))
    video_url = cursor.fetchone()
    cursor.execute("SELECT frame_uuid, video_uuid, frame_number FROM frames WHERE video_uuid = ? AND frame_number = ?", (video_uuid, frame_number))
    row = cursor.fetchone()
    if row :
      frame = Frame(frame_uuid=row[0], video_uuid=row[1], frame_number=row[2])
      return FrameResponse(Response("success", f"Frame {frame_number} of video {video_uuid} fetched successfully."), video_url, frame)
    else :
      return FrameResponse(Response("success", f"Frame {frame_number} of video {video_uuid} not found."), None, None)
    
  except Exception as e :
    return FrameResponse(Response("error", f"Get frame failed: {str(e)}"), None, None)
  
def get_frame_with_objects(conn, cursor, video_uuid: str, model_uuid: str, frame_number: int) -> FrameResponse :
  try :
    cursor.execute("SELECT video_url FROM videos WHERE video_uuid = ?", (video_uuid,))
    video_url = cursor.fetchone()
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, f.frame_number,
        ot.name, o.model_uuid, o.confidence, o.x1, o.y1, o.x2, o.y2, ot.class_id
      FROM frames f
      LEFT JOIN objects o ON f.frame_uuid = o.frame_uuid
      LEFT JOIN object_types ot ON o.type_id = ot.id
      WHERE f.video_uuid = ? AND f.frame_number = ? AND o.model_uuid = ?
    """, (video_uuid, frame_number, model_uuid))
    rows = cursor.fetchall()
    if rows :
      first_row = rows[0]
      frame = Frame(frame_uuid=first_row[0], video_uuid=first_row[1], frame_number=first_row[2])
      objects = []
      for row in rows :
        if row[4] is not None :  # if there is an object
          obj = Object(type=row[3], confidence=row[5], x1=row[6], y1=row[7], x2=row[8], y2=row[9], class_id=row[10])
          objects.append(obj)
      frame.add_objects(objects)
      return FrameResponse(Response("success", f"Frame {frame_number} of video {video_uuid} with model {model_uuid} fetched successfully."), video_url, frame)
    else :
      return FrameResponse(Response("success", f"Frame {frame_number} of video {video_uuid} with model {model_uuid} not found."), None, None)

  except Exception as e :
    return FrameResponse(Response("error", f"Get frame with objects failed: {str(e)}"), None, None)
  
def get_frame_list(conn, cursor, video_uuid: str) -> FrameListResponse :
  try :
    cursor.execute("SELECT video_url FROM videos WHERE video_uuid = ?", (video_uuid,))
    video_url = cursor.fetchone()
    cursor.execute("""SELECT frame_uuid, video_uuid, frame_number FROM frames WHERE video_uuid = ? ORDER BY frame_number ASC""", (video_uuid, ))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows :
        frame_uuid = row[0]
        if frame_uuid not in frames_dict :
          frames_dict[frame_uuid] = Frame(frame_uuid=row[0], video_uuid=row[1], frame_number=row[2], objects={})
        frames = list(frames_dict.values())
      return FrameListResponse(Response("success", f"Frames of video {video_uuid} fetched successfully."), video_url, frames)
    else :
      return FrameListResponse(Response("success", f"No frames found for video {video_uuid}."), None, [])

  except Exception as e :
    return FrameListResponse(Response("error", f"Get frames failed: {str(e)}"), None, [])

def get_frame_list_with_objects(conn, cursor, video_uuid: str, model_uuid: str) -> FrameListResponse :
  try :
    cursor.execute("SELECT video_url FROM videos WHERE video_uuid = ?", (video_uuid,))
    video_url = cursor.fetchone()[0]
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, f.frame_number,
        ot.name, o.model_uuid, o.confidence, o.x1, o.y1, o.x2, o.y2, ot.class_id
      FROM frames f
      LEFT JOIN objects o 
        ON f.frame_uuid = o.frame_uuid AND o.model_uuid = ?
      LEFT JOIN object_types ot 
        ON o.type_id = ot.id
      WHERE f.video_uuid = ?
      ORDER BY f.frame_number ASC
    """, (model_uuid, video_uuid))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows :
        frame_uuid = row[0]
        if frame_uuid not in frames_dict :
          frames_dict[frame_uuid] = Frame(frame_uuid=row[0], video_uuid=row[1], frame_number=row[2], objects=[])
        if row[4] is not None :  # if there is an object
          obj = Object(type=row[3], confidence=row[5], x1=row[6], y1=row[7], x2=row[8], y2=row[9], class_id=row[10])
          frames_dict[frame_uuid].add_object(obj)
      frames = list(frames_dict.values())
      return FrameListResponse(Response("success", f"Frames of video {video_uuid} with model {model_uuid} fetched successfully."), video_url, frames)
    else :
      return FrameListResponse(Response("success", f"No frames found for video {video_uuid} with model {model_uuid}."), None, [])

  except Exception as e :
    return FrameListResponse(Response("error", f"Get frames with objects failed: {str(e)}"), None, [])
  
def get_unprocessed_frame_list(conn, cursor, video_uuid: str, model_uuid: str) -> FrameListResponse :
  try :
    cursor.execute("SELECT video_url FROM videos WHERE video_uuid = ?", (video_uuid,))
    video_url = cursor.fetchone()
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, f.frame_number 
      FROM frames f
      WHERE video_uuid = ? AND NOT EXISTS (
        SELECT 1
        FROM processed_frames pf
        WHERE f.frame_uuid = pf.frame_uuid AND pf.model_uuid = ? 
      )
      ORDER BY frame_number ASC
    """, (video_uuid, model_uuid))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows :
        frame_uuid = row[0]
        if frame_uuid not in frames_dict :
          frames_dict[frame_uuid] = Frame(frame_uuid=row[0], video_uuid=row[1], frame_number=row[2], objects={})
        frames = list(frames_dict.values())
      return FrameListResponse(Response("success", f"Unprocessed frames of video {video_uuid} fetched successfully."), video_url, frames)
    else :
      return FrameListResponse(Response("success", f"No unprocessed frames found for video {video_uuid}."), None, [])

  except Exception as e :
    return FrameListResponse(Response("error", f"Get unprocessed frames failed: {str(e)}"), None, [])


# QUERY PROCESSED-FRAMES FUNCTIONS
# classes
class ProcessedFrame:
  def __init__(self, frame_uuid: str, video_uuid: str, model_uuid: str, frame_number: int, objects: list[Object] = None) :
    self.frame_uuid = frame_uuid
    self.video_uuid = video_uuid
    self.model_uuid = model_uuid
    self.frame_number = frame_number
    if objects is None:
      self.objects = list[Object]()
    else:
      self.objects: list[Object] = objects

  def __str__(self):
    return f"Frame: {self.frame_uuid} Video: {self.video_uuid} Model: {self.model_uuid} Number: {self.frame_number}" + (f", Objects: {len(self.objects)}" if self.objects else "")
  
  def add_objects(self, objects: list[Object]):
    self.objects.extend(objects)

  def add_object(self, object: Object):
    self.objects.append(object)

  def to_dict(self) -> dict:
    frame_dict = {'frame_num': self.frame_number, 'objects': [o.__dict__ for o in self.objects], 'model_id': self.model_uuid}
    return frame_dict
  
class HistoricProcessedFrame(ProcessedFrame):
  def __init__(self, frame_uuid: str, video_uuid: str, model_uuid: str, frame_number: int, model_name: str, objects: list[Object] = None) :
    super().__init__(frame_uuid, video_uuid, model_uuid, frame_number, objects)
    self.model_name = model_name
  
  def to_dict(self) -> dict:
    frame_dict = {'frame_num': self.frame_number, 'objects': [o.__dict__ for o in self.objects], 'model_id': self.model_uuid, 'model_name': self.model_name}
    return frame_dict

class ProcessedFrameResponse:
  def __init__(self, response: Response, processed_frame: ProcessedFrame) :
    self.response = response
    self.processed_frame = processed_frame

  def __str__(self):
    return str(self.response) + (f"\n{self.processed_frame}" if self.processed_frame else "")
  
class ProcessedFrameListResponse:
  def __init__(self, response: Response, processed_frames: list[ProcessedFrame]):
    self.response = response
    self.processed_frames = processed_frames

  def __str__(self):
    return str(self.response) + ("\n" + "\n".join([str(frame) for frame in self.processed_frames]) if self.processed_frames else "")
  
# definitions 
def get_processed_frame(conn, cursor, video_uuid: str, model_uuid: str, frame_number: int) -> ProcessedFrameResponse :
  try : 
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, pf.model_uuid, f.frame_number
      FROM frames f
      LEFT JOIN processed_frames pf ON f.frame_uuid = pf.frame_uuid
      WHERE f.video_uuid = ? AND f.frame_number = ? AND pf.model_uuid = ? 
    """, (video_uuid, frame_number, model_uuid))
    row = cursor.fetchone()
    if row :
      processed_frame = ProcessedFrame(frame_uuid=row[0], video_uuid=row[1], model_uuid=row[2], frame_number=row[3])
      return ProcessedFrameResponse(Response("success", f"Processed frame for {video_uuid}, model {model_uuid}, and {frame_number} successfully found."), processed_frame)
    else :
      return ProcessedFrameResponse(Response("success", f"Processed frame for {video_uuid}, model {model_uuid}, and {frame_number} not found."), None)
    
  except Exception as e :
    return ProcessedFrameResponse(Response("error", f"Get processed frame failed: {str(e)}"), None)
  
def get_processed_frame_with_objects(conn, cursor, video_uuid: str, model_uuid: str, frame_number: int) -> ProcessedFrameResponse :
  try :
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, pf.model_uuid, f.frame_number,
        ot.name, o.model_uuid, o.confidence, o.x1, o.y1, o.x2, o.y2, ot.class_id
      FROM frames f
      LEFT JOIN processed_frames pf ON f.frame_uuid = pf.frame_uuid
      LEFT JOIN objects o ON f.frame_uuid = o.frame_uuid AND pf.model_uuid = o.model_uuid
      LEFT JOIN object_types ot ON o.type_id = ot.id
      WHERE f.video_uuid = ? AND f.frame_number = ? AND pf.model_uuid = ? 
    """, (video_uuid, frame_number, model_uuid))
    rows = cursor.fetchall()
    if rows :
      first_row = rows[0]
      processed_frame = ProcessedFrame(frame_uuid=first_row[0], video_uuid=first_row[1], model_uuid=first_row[2], frame_number=first_row[3])
      objects = []
      for row in rows :
        if row[5] is not None :
          obj = Object(type=row[4], confidence=row[6], x1=row[7], y1=row[8], x2=row[9], y2=row[10], class_id=row[11])
          objects.append(obj)
      processed_frame.add_objects(objects)
      return ProcessedFrameResponse(Response("success", f"Processed frame for {video_uuid}, model {model_uuid}, and {frame_number} successfully found."), processed_frame)
    else :
      return ProcessedFrameResponse(Response("success", f"Processed frame for {video_uuid}, model {model_uuid}, and {frame_number} not found."), None)
    
  except Exception as e :
    return ProcessedFrameResponse(Response("error", f"Get processed frame failed: {str(e)}"), None)

def get_processed_frame_list(conn, cursor, video_uuid: str, model_uuid: str) -> ProcessedFrameListResponse :
  try : 
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, pf.model_uuid, f.frame_number
      FROM frames f
      LEFT JOIN processed_frames pf ON f.frame_uuid = pf.frame_uuid
      WHERE f.video_uuid = ? AND pf.model_uuid = ? 
    """, (video_uuid, model_uuid))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows:
        frame_uuid = row[0]
        if frame_uuid not in frames_dict :
          frames_dict[frame_uuid] = ProcessedFrame(frame_uuid=row[0], video_uuid=row[1], model_uuid=row[2], frame_number=row[3])
      frames = list(frames_dict.values())
      return ProcessedFrameListResponse(Response("success", f"Frames of video {video_uuid} and model {model_uuid} fetched successfully."), frames)
    else :
      return ProcessedFrameListResponse(Response("success", f"No frames found for video {video_uuid} and model {model_uuid}."), [])
    
  except Exception as e :
    return ProcessedFrameListResponse(Response("error", f"Get frames failed: {str(e)}"), [])
  
def get_processed_frame_list_with_objects(conn, cursor, video_uuid: str, model_uuid: str) -> ProcessedFrameListResponse :
  try : 
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, pf.model_uuid, f.frame_number,
        ot.name, o.model_uuid, o.confidence, o.x1, o.y1, o.x2, o.y2, ot.class_id
      FROM frames f
      LEFT JOIN processed_frames pf 
        ON f.frame_uuid = pf.frame_uuid
      LEFT JOIN objects o 
        ON f.frame_uuid = o.frame_uuid AND o.model_uuid = ?
      LEFT JOIN object_types ot 
        ON o.type_id = ot.id
      WHERE f.video_uuid = ? AND pf.model_uuid = ? 
      ORDER BY f.frame_number ASC
    """, (model_uuid, video_uuid, model_uuid))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows:
        frame_uuid = row[0]
        if frame_uuid not in frames_dict :
          frames_dict[frame_uuid] = ProcessedFrame(frame_uuid=row[0], video_uuid=row[1], model_uuid=row[2], frame_number=row[3])
        if row[5] is not None :
          obj = Object(type=row[4], confidence=row[6], x1=row[7], y1=row[8], x2=row[9], y2=row[10], class_id=row[11])
          frames_dict[frame_uuid].add_object(obj)
      frames = list(frames_dict.values())
      return ProcessedFrameListResponse(Response("success", f"Frames of video {video_uuid} and model {model_uuid} fetched successfully."), frames)
    else :
      return ProcessedFrameListResponse(Response("success", f"No frames found for video {video_uuid} and model {model_uuid}."), [])
    
  except Exception as e :
    return ProcessedFrameListResponse(Response("error", f"Get frames failed: {str(e)}"), [])
  
def get_processed_frame_history_with_objects(conn, cursor, video_uuid: str, model_uuid: str, frame_num: int) -> ProcessedFrameListResponse :
  try : 
    cursor.execute("""
      SELECT f.frame_uuid, f.video_uuid, pf.model_uuid, f.frame_number,
        ot.name, o.model_uuid, o.confidence, o.x1, o.y1, o.x2, o.y2, ot.class_id, m.title
      FROM frames f
      LEFT JOIN processed_frames pf 
        ON f.frame_uuid = pf.frame_uuid
      LEFT JOIN objects o 
        ON f.frame_uuid = o.frame_uuid AND pf.model_uuid = o.model_uuid
      LEFT JOIN object_types ot 
        ON o.type_id = ot.id
      LEFT JOIN models m
        ON m.model_uuid = pf.model_uuid
      WHERE f.video_uuid = ? AND pf.model_uuid != ? AND f.frame_number = ?
    """, (video_uuid, model_uuid, frame_num))
    rows = cursor.fetchall()
    if rows :
      frames_dict = {}
      for row in rows:
        model_uuid = row[2]
        if model_uuid not in frames_dict :
          frames_dict[model_uuid] = HistoricProcessedFrame(frame_uuid=row[0], video_uuid=row[1], model_uuid=row[2], frame_number=row[3], model_name=row[12])
        if row[5] is not None:
          obj = Object(type=row[4], confidence=row[6], x1=row[7], y1=row[8], x2=row[9], y2=row[10], class_id=row[11])
          frames_dict[model_uuid].add_object(obj)
      frames = list(frames_dict.values())
      return ProcessedFrameListResponse(Response("success", f"Frames of video {video_uuid} and model {model_uuid} fetched successfully."), frames)
    else :
      return ProcessedFrameListResponse(Response("success", f"No frames found for video {video_uuid} and model {model_uuid}."), [])
    
  except Exception as e :
    return ProcessedFrameListResponse(Response("error", f"Get frames failed: {str(e)}"), [])