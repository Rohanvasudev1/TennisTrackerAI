from ultralytics import YOLO
model = YOLO('yolov8x.pt')  # Load a custom model
result = model.track("testingvideos/video.mp4", conf =0.2, save = True)
print(result[0].boxes.xyxy)  # Print the bounding boxes
#note that tennis ball is detected v raarely so hard to find 
#therefore need to fine tune detector model 
