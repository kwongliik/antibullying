# crowd_detector.py
import os
from ultralytics import YOLO
import cv2
import numpy as np

class CrowdDetector:
    def __init__(self):

        model_path = os.path.join(os.getcwd(), "models", "yolov8n.pt")
        print(f"🔍 Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)

    def detect(self, frame):

        results = self.model(frame, conf=0.4, classes=[0], verbose=False)
        alerts = []

        boxes = []
        person_count = 0

        for r in results:
            for box in r.boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                boxes.append((x1, y1, x2, y2))
                person_count += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0,255,0), 2)

                cv2.putText(frame,
                            f"Person {conf:.2f}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0,255,0),
                            2)

        # Check clustering (possible bullying)
        if person_count >= 3:
            centers = [((x1+x2)//2, (y1+y2)//2) for (x1,y1,x2,y2) in boxes]

            if self._are_clustered(centers):
                alerts.append(f"⚠️ {person_count} people closely grouped")

        return frame, alerts, person_count


    def _are_clustered(self, centers, threshold=200):

        if len(centers) < 2:
            return False

        for i in range(len(centers)):
            for j in range(i+1, len(centers)):

                dist = ((centers[i][0]-centers[j][0])**2 +
                        (centers[i][1]-centers[j][1])**2) ** 0.5

                if dist < threshold:
                    return True

        return False