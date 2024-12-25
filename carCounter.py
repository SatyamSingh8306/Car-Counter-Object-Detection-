from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

model = YOLO("./Yolo/yolov8l.pt")
cap = cv2.VideoCapture("./Video/cars.mp4")
mask = cv2.imread("./Image/mask.png")
totalCount = []
trackers = Sort(max_age=20,min_hits=3,iou_threshold=0.3 )

# cap.set(3,640)
# cap.set(4,480)
limits = [400,297,673,297]


classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]



while True:
    
    sucess,img = cap.read()
    mask = cv2.resize(mask,(img.shape[1],img.shape[0]))
    imgRegion = cv2.bitwise_and(img,mask)

    imgGraphics = cv2.imread("./Image/graphics.png",cv2.IMREAD_UNCHANGED)
    img =cvzone.overlayPNG(img,imgGraphics,(0,0))
    result = model(imgRegion,stream=True)

    detections = np.empty((0,5))
    for r in result:
        boxes = r.boxes
        for box in boxes:

            #Bounding Box
            '''choice 1'''
            x1,y1,x2,y2=box.xyxy[0]
            x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
            w = x2-x1
            h = y2-y1
            #cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),1)

            '''choice 2'''
            # x1,y1,w,h = box.xywh[0]
            # x1,y1,w,h = int(x1),int(y1),int(w),int(h)
            

            #confidence value
            conf = (math.ceil(box.conf[0]*100))/100

            #class 
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass=="person" or currentClass=="car" or currentClass=="truck" or currentClass=="motor" or currentClass== "motorbike" and conf>0.3:

                # cvzone.cornerRect(img,(x1,y1,w,h),l=8)

                # cvzone.putTextRect(img,f"{classNames[cls]} {conf}",pos=(max(0,x1),max(35,y1-20)),
                #                 scale=0.8,thickness=1,offset=3)
                currentArray = np.array([x1,y1,x2,y2,conf])
                detections = np.vstack((detections,currentArray))

    resultsTracker = trackers.update(detections)
    cv2.line(img,(limits[0],limits[1]),(limits[2],limits[3]),(0,0,255),4)
    for results in resultsTracker:
        x1,y1,x2,y2,id = results
        x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
        w,h = x2-x1,y2-y1
        cvzone.cornerRect(img,(x1,y1,w,h),l=8,rt=1,colorR=(255,0,255))
        cvzone.putTextRect(img,f"{id}",pos=(max(0,x1),max(35,y1)),
                                scale=2,thickness=3,offset=10)
        cx,cy = x1+w//2,y1+h//2
        cv2.circle(img,radius=5,center=(cx,cy),color=(0,255,255),thickness=cv2.FILLED)

        if limits[0]<cx <limits[2] and limits[1] - 15<cy<limits[3]+15:
            if totalCount.count(id)==0:
                totalCount.append(id)
                cv2.line(img,(limits[0],limits[1]),(limits[2],limits[3]),(0,255,0),4)
            

    # cvzone.putTextRect(img,f"Count: {len(totalCount)}",pos=(50,50),
    #                             scale=2,thickness=3,offset=10)
    cv2.putText(img,str(len(totalCount)),(255,100),cv2.FONT_HERSHEY_PLAIN,5,(50,50,255),8)
    cv2.imshow("image",img)
    # cv2.imshow("imageRegion",imgRegion)        
    
    
    if cv2.waitKey(1) & 0xFF ==ord('x'):
        break

cv2.destroyAllWindows()
