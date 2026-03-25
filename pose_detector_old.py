# pose_detector.py
import mediapipe as mp
import cv2
import numpy as np

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        alerts = []

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

            # Check for raised arms (aggressive gesture)
            left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            if (left_wrist.y < left_shoulder.y - 0.1 or
                right_wrist.y < right_shoulder.y - 0.1):
                alerts.append("⚠️ Raised arm/aggressive gesture detected")

        return frame, alerts
