from yolo11s import Yolo11s

def main() :
  yolo = Yolo11s()
  yolo.set_model_path("../ob_detect_models/yolo11s.pt")
  yolo.get_bounding_boxes("../test_images/big.PNG")


if __name__ =="__main__":
  main()