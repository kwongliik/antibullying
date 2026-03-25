# pose_detector.py

import mediapipe as mp
import cv2
import numpy as np
from collections import deque


class PoseDetector:

    def __init__(self):

        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.mp_draw = mp.solutions.drawing_utils

        # Store wrist history to detect motion
        self.left_wrist_history = deque(maxlen=6)
        self.right_wrist_history = deque(maxlen=6)

        # Motion threshold (tune if needed)
        self.motion_threshold = 0.08


    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        alerts = []

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            self.mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

            # Get wrist positions
            left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]

            left_pos = np.array([left_wrist.x, left_wrist.y])
            right_pos = np.array([right_wrist.x, right_wrist.y])

            # Save position history
            self.left_wrist_history.append(left_pos)
            self.right_wrist_history.append(right_pos)

            # Detect aggressive motion
            if self._is_fast_motion(self.left_wrist_history):
                alerts.append("⚠️ Fast arm movement detected")

            if self._is_fast_motion(self.right_wrist_history):
                alerts.append("⚠️ Fast arm movement detected")

        return frame, alerts


    def _is_fast_motion(self, history):

        if len(history) < 5:
            return False

        total_motion = 0

        for i in range(1, len(history)):
            movement = np.linalg.norm(history[i] - history[i-1])
            total_motion += movement

        avg_motion = total_motion / (len(history)-1)

        if avg_motion > self.motion_threshold:
            return True

        return False