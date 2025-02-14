'''
FILE: abc_model.py
Author: Benjamin Small
DATE Created: 2/14/2025
LAST Updated: 2/14/2025

Description: Provides a constrict class outline for all models to have for interchangability within object detection models to use

'''

from abc import ABC, abstractmethod
import json

class ObjectDetectionModel :
  @abstractmethod
  def set_model_path(self, url) :
    pass
  def get_bounding_boxes(self, frame) :
    pass