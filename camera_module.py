# camera_module.py
from picamera2 import Picamera2
import cv2

class CameraModule:
    def __init__(self, width=1280, height=720):
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()

    def get_frame(self):
        frame = self.picam2.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def release(self):
        self.picam2.stop()
