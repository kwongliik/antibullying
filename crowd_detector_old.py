# crowd_detector.py
import cv2

class CrowdDetector:
    def __init__(self):
        # Use HOG person detector built into OpenCV
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes, weights = self.hog.detectMultiScale(
            gray, winStride=(8, 8), padding=(4, 4), scale=1.05
        )

        alerts = []
        person_count = len(boxes)

        for (x, y, w, h) in boxes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Flag if 3+ people closely grouped (potential bullying scenario)
        if person_count >= 3:
            centers = [(x + w//2, y + h//2) for (x, y, w, h) in boxes]
            if self._are_clustered(centers):
                alerts.append(f"⚠️ Group of {person_count} people closely clustered")

        return frame, alerts, person_count

    def _are_clustered(self, centers, threshold=150):
        """Check if people are within threshold pixels of each other"""
        if len(centers) < 2:
            return False
        for i in range(len(centers)):
            for j in range(i+1, len(centers)):
                dist = ((centers[i][0]-centers[j][0])**2 +
                        (centers[i][1]-centers[j][1])**2) ** 0.5
                if dist < threshold:
                    return True
        return False
