'''
FILE: yolo11s.py
Author: Benjamin Small
DATE Created: 2/14/2025
LAST Updated: 2/14/2025

Description: Uses the abc_model class requirements to implement the yolo version 11s. 

'''

from abc_model import ObjectDetectionModel
import cv2
from ultralytics import YOLO

class Yolo11s(ObjectDetectionModel) :
  def set_model_path(self, url) :
    self.model = YOLO(url)
  def get_bounding_boxes(self, frame) :
    image = cv2.imread(frame)

    width = 800
    (h, w) = image.shape[:2]
    ratio = width / float(w)
    new_width = width
    new_height = int(h * ratio)
    resize_img = cv2.resize(image, (new_width, new_height))

    
    results = self.model(resize_img)
    img_with_boxes = results[0].plot()

    cv2.imshow("YOLOv11s Detection", img_with_boxes)
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 


