from ai_modules.abc_model import ObjectDetectionModel
import tensorflow as tf
import numpy as np
import json

class TensorFlowModel(ObjectDetectionModel):
    def __init__(self, model_path: str):
        self.model = tf.saved_model.load(model_path)
        self.results = None
        
    def predict_objects_in(self, image: np.ndarray):
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        
        model_function = self.model.signatures['serving_default']
        self.results = model_function(input_tensor)
        
    def get_image(self) -> np.ndarray:
        return self.results['detection_boxes'] 

    def get_boxes_json(self) -> str:
        if self.results is None:
            return json.dumps({"error": "No prediction made"})
        
        boxes = self.results['detection_boxes'].numpy().tolist()
        scores = self.results['detection_scores'].numpy().tolist()
        classes = self.results['detection_classes'].numpy().tolist()
        
        result_dict = {
            'boxes': boxes,
            'scores': scores,
            'classes': classes
        }
        return json.dumps(result_dict)

