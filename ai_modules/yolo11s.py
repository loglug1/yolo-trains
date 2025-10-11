'''
FILE: yolo11s.py
Author: Benjamin Small
DATE Created: 2/14/2025
LAST Updated: 2/14/2025

Description: Uses the abc_model class requirements to implement the yolo version 11s. 

'''

from ai_modules.abc_model import ObjectDetectionModel
from ultralytics import YOLO
import numpy as np
import os

class Yolo11s(ObjectDetectionModel) :

  def __init__(self, model_path = "ai_modules/ob_detect_models/yolo11s.pt") :
    self.model = YOLO(model_path)
    self.results = None

  def set_model_path(self, url) :
    print("This function is depricated. Pass model into initializer instead.")
    self.model = YOLO(url)

  def predict_objects_in(self, image: np.ndarray) -> float :
    gpu_device = os.environ.get('HIP_VISIBLE_DEVICES', 'cpu')
    print("Using GPU: ", gpu_device)
    generator = self.model.predict(image, verbose=False, stream=True, device=gpu_device)
    self.result = next(generator)
    speed_dict = self.result.speed
    speed = 0.0
    for key, value in speed_dict.items():
      speed += value
    return speed
    
  def get_image(self) -> np.ndarray :
    return self.result.plot()
  
  def get_boxes_json(self) -> str :
    return self.result.to_json()