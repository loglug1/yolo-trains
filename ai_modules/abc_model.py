'''
FILE: abc_model.py
Author: Benjamin Small
DATE Created: 2/14/2025
LAST Updated: 2/14/2025

Description: Provides a constrict class outline for all models to have for interchangability within object detection models to use

'''

from abc import ABC, abstractmethod
import base64
import json
import numpy as np

class ObjectDetectionModel :
  @abstractmethod
  def set_model_path(self, url) :
    pass
  def predict_objects_in(self, image: np.ndarray) -> float :
    pass
  def get_image(self) -> np.ndarray :
    pass
  def get_base64_prediction(self) -> base64 :
    pass
  def get_boxes_json(self) -> json :
    pass