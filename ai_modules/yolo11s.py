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
    width = 800
    (h, w) = image.shape[:2]
    ratio = width / float(w)
    new_width = width
    new_height = int(h * ratio)
    resize_img = cv2.resize(image, (new_width, new_height))

    self.results = self.model(resize_img)
    
  def get_image(self):
    return self.results[0].plot()