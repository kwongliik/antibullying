# emotion_detector.py
import cv2

class EmotionDetector:
    def __init__(self):
        # Use OpenCV's Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # For full emotion detection, use a TFLite model:
        # https://tfhub.dev/google/lite-model/imagenet/mobilenet_v3_small_100_224/classification/5/default/1

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return frame, len(faces)
