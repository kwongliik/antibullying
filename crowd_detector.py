# crowd_detector.py

import os
from ultralytics import YOLO
import cv2
import numpy as np


class CrowdDetector:

    def __init__(self):

        model_path = os.path.join(os.getcwd(), "models", "yolov8n.pt")
        print(f"🔍 Loading YOLO model: {model_path}")

        # Load YOLOv8n
        self.model = YOLO(model_path)

        # Detection parameters
        self.conf_threshold = 0.65
        self.min_box_area = 5000   # ignore tiny detections


    def detect(self, frame):

        results = self.model(
            frame,
            conf=self.conf_threshold,
            classes=[0],     # only detect person
            verbose=False
        )

        alerts = []
        boxes = []
        person_count = 0

        for r in results:

            if r.boxes is None:
                continue

            for box in r.boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                width = x2 - x1
                height = y2 - y1
                area = width * height

                # Ignore tiny detections (often false)
                if area < self.min_box_area:
                    continue

                boxes.append((x1, y1, x2, y2))
                person_count += 1

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0,255,0), 2)

                cv2.putText(frame,
                            f"Person {conf:.2f}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0,255,0),
                            2)

        # Improved clustering detection
        if person_count >= 3:

            centers = [
                ((x1+x2)//2, (y1+y2)//2)
                for (x1,y1,x2,y2) in boxes
            ]

            cluster_pairs = self._count_close_pairs(centers)

            # Require multiple close pairs to reduce false alarms
            if cluster_pairs >= 3:
                alerts.append(f"⚠️ {person_count} people tightly grouped")

        return frame, alerts, person_count


    def _count_close_pairs(self, centers, threshold=150):

        pair_count = 0

        for i in range(len(centers)):
            for j in range(i+1, len(centers)):

                dist = np.linalg.norm(
                    np.array(centers[i]) - np.array(centers[j])
                )

                if dist < threshold:
                    pair_count += 1

        return pair_count