# pose_detector.py

import mediapipe as mp
import cv2
import numpy as np
from collections import deque


class PoseDetector:

    def __init__(self):

        self.mp_pose = mp.solutions.pose

        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.mp_draw = mp.solutions.drawing_utils

        # Wrist history
        self.left_wrist_history = deque(maxlen=8)
        self.right_wrist_history = deque(maxlen=8)

        # Motion threshold (higher = less sensitive)
        self.motion_threshold = 0.05

        # Require repeated aggressive frames
        self.aggressive_counter = 0
        self.aggressive_frames_required = 4


    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        alerts = []

        if not results.pose_landmarks:
            self.left_wrist_history.clear()
            self.right_wrist_history.clear()
            self.aggressive_counter = 0
            return frame, []        

        landmarks = results.pose_landmarks.landmark

        # Visibility check
        def is_valid(lm):
            return lm.visibility > 0.6  # tune 0.5–0.7

        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]

        valid_wrist = is_valid(left_wrist) or is_valid(right_wrist)
        valid_head = is_valid(nose)

        if not (valid_wrist and valid_head):
            self.left_wrist_history.clear()
            self.right_wrist_history.clear()
            self.aggressive_counter = 0
            return frame, []

        left_pos = np.array([left_wrist.x, left_wrist.y])
        right_pos = np.array([right_wrist.x, right_wrist.y])
        head_pos = np.array([nose.x, nose.y])

        # Save history
        if is_valid(left_wrist):
            self.left_wrist_history.append(left_pos)
        if is_valid(right_wrist):
            self.right_wrist_history.append(right_pos)

        aggressive_motion = False

        # Detect punch-like motion
        if self._is_aggressive_motion(self.left_wrist_history, head_pos):
            aggressive_motion = True

        if self._is_aggressive_motion(self.right_wrist_history, head_pos):
            aggressive_motion = True

        # Temporal filtering
        if aggressive_motion:
            self.aggressive_counter += 1
        else:
            self.aggressive_counter = max(0, self.aggressive_counter - 1)

        if self.aggressive_counter >= self.aggressive_frames_required:
            alerts.append("🚨 Possible aggressive action detected")
            self.aggressive_counter = 0

        return frame, alerts


    def _is_aggressive_motion(self, history, head_pos):

        if len(history) < 6:
            return False

        total_motion = 0
        forward_motion = 0

        for i in range(1, len(history)):

            movement = history[i] - history[i-1]
            speed = np.linalg.norm(movement)

            total_motion += speed

            # Detect forward punching direction
            if speed > 0.02:
                forward_motion += 1

        avg_motion = total_motion / (len(history) - 1)

        # Check if wrist moved near head (simulated victim area)
        wrist_to_head = np.linalg.norm(history[-1] - head_pos)

        if (
            avg_motion > self.motion_threshold
            and forward_motion >= 3
            and wrist_to_head < 0.35
        ):
            return True

        return False