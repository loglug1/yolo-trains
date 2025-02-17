'''
FILE: yolo11s.py
Author: Benjamin Small
DATE Created: 2/14/2025
LAST Updated: 2/14/2025

Description: Uses the abc_model class requirements to implement the yolo version 11s. 

'''

from ai_modules.abc_model import ObjectDetectionModel
import cv2
from ultralytics import YOLO

class Yolo11s(ObjectDetectionModel) :
  def __init__(self) :
    self.results = None
  def set_model_path(self, url) :
    self.model = YOLO(url)
  def predict_objects_in(self, image) :
    self.results = self.model(image)

    speed_dict = self.results[0].speed
    speed = 0.0
    for key, value in speed_dict.items():
      speed += value

    return speed
    
  def get_image(self):
    return self.results[0].plot()