from ai_modules.yolo11s import Yolo11s
import cv2

def main() :
  yolo = Yolo11s()
  image = cv2.imread("test_images/big.PNG")
  yolo.set_model_path("ob_detect_models/yolo11s.pt")
  yolo.predict_objects_in(image)
  image_with_boxes = yolo.get_image()
  cv2.imshow("YOLOv11s Detection", image_with_boxes)
  cv2.waitKey(0) 
  cv2.destroyAllWindows()


if __name__ =="__main__":
  main()