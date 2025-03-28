from ai_modules.yolo11s import Yolo11s
import argparse
import cv2

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input", "-i", dest="file_in", type=str, help="Path to source video file for testing. Type 'camera' to use webcam (press Ctrl+C to quit)", required=True)
    arg_parser.add_argument("--out", "-o", dest="file_out", default=None, type=str, help="Name to save processed video as without extension.", required=False)
    args = arg_parser.parse_args()

    # open input video either from camera or file
    if args.file_in == "camera":
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(args.file_in)
    if cap.isOpened() == False: # verify file could be opened
        cap.release()
        raise Exception("Error opening input file!")
    
    # calculate smaller resolution while keeping aspect ratio
    width = 800
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    ratio = width / float(w)
    new_width = width
    new_height = int(h * ratio)
    
    # get fps metadata for calculating frame skipping when processing
    fps = cap.get(cv2.CAP_PROP_FPS)
    fpms = fps / 1000

    # if an output filename is specified, save to file instead of displaying
    if args.file_out != None:
        out = cv2.VideoWriter(args.file_out + ".mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (new_width, new_height))
        if out.isOpened() == False:
            raise Exception("Error writing to output file!")
    
    yolo = Yolo11s("ai_modules/ob_detect_models/yolo11s.pt")

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False: # when frames stop being read, end
            break

        # resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height))

        # generate bounding boxes on image
        processing_time = yolo.predict_objects_in(resized_frame)
        processed_frame = yolo.get_image()


        if args.file_out == None:
            # display frame to live video feed of processed video
            cv2.imshow("YOLO Video Feed", processed_frame)
            # jump forward in video to simulate "real time" (actually is faster than real time)
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + int(processing_time * fpms))
        else:
            out.write(processed_frame)
        cv2.waitKey(1)

        # frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
        # print(f'OBJECTS IN FRAME #{frame_num}:')
        # print(yolo.get_boxes_json())
        print(processed_frame.dtype)

    cap.release()
    if args.file_out != None:
        out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()