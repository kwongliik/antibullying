import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import os
from collections import deque, Counter


class EmotionDetector:

    def __init__(self, model_path=None):

        # Face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        if model_path is None:
            model_path = os.path.join(os.getcwd(), "models", "emotion_model.tflite")

        # Load TFLite model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Emotion labels
        self.labels = ["angry","disgust","fear","happy","sad","surprise","neutral"]

        # Detection parameters
        self.confidence_threshold = 0.65
        self.min_face_size = 90

        # Temporal smoothing buffer
        self.history_size = 10
        self.emotion_history = deque(maxlen=self.history_size)


    def detect_faces(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=6,
            minSize=(self.min_face_size, self.min_face_size)
        )

        alerts = []

        for (x, y, w, h) in faces:

            face_img = gray[y:y+h, x:x+w]

            # ===== Reject very dark faces =====
            brightness = np.mean(face_img)
            if brightness < 40:
                continue

            # ===== Reject distorted faces =====
            ratio = w / float(h)
            if ratio < 0.6 or ratio > 1.4:
                continue

            # Resize to model input
            input_shape = self.input_details[0]['shape']
            target_height, target_width = input_shape[1], input_shape[2]

            face_img = cv2.resize(face_img, (target_width, target_height))

            # Channel handling
            if input_shape[3] == 3:
                face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2RGB)
            else:
                face_img = np.expand_dims(face_img, axis=-1)

            # Normalize
            if self.input_details[0]['dtype'] == np.float32:
                face_img = face_img.astype(np.float32) / 255.0
            else:
                face_img = face_img.astype(np.uint8)

            face_input = np.expand_dims(face_img, axis=0)

            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], face_input)
            self.interpreter.invoke()

            output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

            emotion_idx = np.argmax(output)
            confidence = float(output[emotion_idx])

            if confidence < self.confidence_threshold:
                continue

            emotion_label = self.labels[emotion_idx]

            # Add to history buffer
            self.emotion_history.append(emotion_label)

            # Temporal smoothing
            smoothed_emotion = Counter(self.emotion_history).most_common(1)[0][0]

            # Draw face box
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

            label_text = f"{smoothed_emotion} ({confidence:.2f})"

            cv2.putText(frame,label_text,(x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)

            # Negative emotion detection
            negative_emotions = ["angry","fear","sad"]

            negative_count = sum(
                1 for e in self.emotion_history if e in negative_emotions
            )

            # Require persistence before alert
            if negative_count >= 6 and confidence > 0.75:
                alerts.append(f"Negative emotion detected: {smoothed_emotion}")

        return frame, alerts