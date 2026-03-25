import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import os
from collections import deque, Counter


class EmotionDetector:
    def __init__(self, model_path=None):

        # Haar cascade face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Load TFLite model
        if model_path is None:
            model_path = os.path.join(os.getcwd(), "models", "emotion_model.tflite")

        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Emotion labels
        self.labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

        # ===== IMPROVEMENTS =====

        # Prediction confidence threshold
        self.confidence_threshold = 0.6

        # Minimum face size to reduce false detections
        self.min_face_size = 80

        # Temporal smoothing buffer
        self.emotion_history = deque(maxlen=5)

    def detect_faces(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=7,
            minSize=(self.min_face_size, self.min_face_size)
        )

        alerts = []

        for (x, y, w, h) in faces:

            face_img = gray[y:y+h, x:x+w]

            # ===== Resize to model input =====
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

            # ===== Run inference =====
            self.interpreter.set_tensor(self.input_details[0]['index'], face_input)
            self.interpreter.invoke()

            output = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

            emotion_idx = np.argmax(output)
            confidence = output[emotion_idx]

            # Ignore low confidence predictions
            if confidence < self.confidence_threshold:
                continue

            emotion_label = self.labels[emotion_idx]

            # Save emotion history for smoothing
            self.emotion_history.append(emotion_label)

            # Majority vote smoothing
            smoothed_emotion = Counter(self.emotion_history).most_common(1)[0][0]

            # Draw face box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Show emotion + confidence
            label_text = f"{smoothed_emotion} ({confidence:.2f})"

            cv2.putText(frame, label_text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            # ===== Alert only if strong negative emotion =====
            if smoothed_emotion in ["angry", "fear", "sad", "disgust"] and confidence > 0.75:
                alerts.append(f"Detected emotion: {smoothed_emotion}")

        return frame, alerts