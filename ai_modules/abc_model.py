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
  # predict objects in image and return processing time
  def predict_objects_in(self, image: np.ndarray) -> float :
    pass
  # return previously predicted image
  @abstractmethod
  def get_image(self) -> np.ndarray :
    pass
  # return JSON of objects detected in image with probabilities and locations
  @abstractmethod
  def get_boxes_json(self) -> str :
    pass