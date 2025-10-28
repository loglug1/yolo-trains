from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
from datetime import datetime, timedelta, UTC
from db_connect.database import Response, Model, Videos, Frame, Object

def influx_connect(token, org, url):
  client = InfluxDBClient(url=url, token=token, org=org)
  writer = client.write_api(write_options=SYNCHRONOUS)
  return client, writer

def insert_objects_influx(client, writer, bucket, model: Model, video: Videos, frame: Frame, objects: list[Object]) -> Response : 
  try : 

    EPOCH = datetime(2025, 1, 1, tzinfo=UTC)
    frametime = frame.frame_number / video.framerate

    points = []
    for obj in objects:
      points.append(
        Point("object") 
        .tag("model_id", model.model_uuid)
        .field("model", model.title) 
        .tag("video_id", video.video_uuid)
        .field("video", video.title) 
        .tag("object", obj.type) 
        .field("confidence", obj.confidence) 
        .field("x1", obj.x1) 
        .field("y1", obj.y1) 
        .field("x2", obj.x2) 
        .field("y2", obj.y2) 
        .time(EPOCH + timedelta(seconds=frametime), WritePrecision.NS)
      )

    writer.write(bucket=bucket, record=points)
    return Response("success", f"Objects inserted into influx successfully.")
  
  except Exception as e :
    return Response("error", f"Insert objects into influx failed: {str(e)}")