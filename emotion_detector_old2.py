# emotion_detector.py
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import os

class EmotionDetector:
    def __init__(self, model_path=None):
        # Haar cascade for face detection (to crop faces)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load TFLite model
        if model_path is None:
            model_path = os.path.join(os.getcwd(), "models", "emotion_model.tflite")
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        # Get input/output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Labels (update according to your model)
        self.labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48)
        )
        alerts = []

        for (x, y, w, h) in faces:
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Crop face
            face_img = gray[y:y+h, x:x+w]

            # ===== RESIZE TO MODEL INPUT =====
            input_shape = self.input_details[0]['shape']  # e.g., [1, 64, 64, 1] or [1, 64, 64, 3]
            target_height, target_width = input_shape[1], input_shape[2]

            # Resize face to model input size
            face_img_resized = cv2.resize(face_img, (target_width, target_height))

            # Convert grayscale to match channels
            if input_shape[3] == 3:  # model expects RGB
                face_img_resized = cv2.cvtColor(face_img_resized, cv2.COLOR_GRAY2RGB)
            else:
                face_img_resized = np.expand_dims(face_img_resized, axis=-1)

            # Normalize if float32 model
            if self.input_details[0]['dtype'] == np.float32:
                face_img_resized = face_img_resized.astype(np.float32) / 255.0
            else:
                face_img_resized = face_img_resized.astype(np.uint8)

            # Add batch dimension
            face_input = np.expand_dims(face_img_resized, axis=0)

            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], face_input)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            emotion_idx = np.argmax(output)
            emotion_label = self.labels[emotion_idx]

            # Optional: Alert on negative emotions
            if emotion_label in ["angry", "fear", "sad", "disgust"]:
                alerts.append(f"Detected emotion: {emotion_label}")

            # Overlay emotion on frame
            cv2.putText(frame, emotion_label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        return frame, alerts
