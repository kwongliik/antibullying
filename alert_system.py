# alert_system.py

import time
import os
import cv2
import json
import paho.mqtt.client as mqtt

MQTT_TOPIC_ALERT  = "school/alert"
MQTT_TOPIC_STATUS = "school/status"
SNAPSHOT_DIR      = "/home/pi5/.node-red/public/image"

mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


class AlertSystem:
    def __init__(self, buzzer_pin=None, cooldown=10):
        self.cooldown = cooldown
        self.last_alert_time = 0
        self.buzzer_pin = buzzer_pin

        # GPIO setup
        if buzzer_pin is not None:
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(buzzer_pin, GPIO.OUT)
                print("🔔 Buzzer initialized")
            except:
                self.GPIO = None
                print("⚠️ GPIO not available")

    # ================= STATUS =================
    def startup_notify(self, frame=None, camera="cam_1"):
        self._send_status("SYSTEM_START", "🟢 Camera started monitoring", frame, camera)

    def shutdown_notify(self, frame=None, camera="cam_1"):
        self._send_status("SYSTEM_STOP", "🔴 Camera stopped monitoring", frame, camera)

    def _send_status(self, event, message, frame, camera):
        filename = None

        if frame is not None:
            filename = f"{event.lower()}_{int(time.time())}.jpg"
            path = f"{SNAPSHOT_DIR}/{filename}"
            cv2.imwrite(path, frame)

        data = {
            "event": event,
            "message": message,
            "camera": camera,
            "image": f"/image/{filename}" if filename else None,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        mqtt_client.publish(MQTT_TOPIC_STATUS, json.dumps(data))

    # ================= ALERT =================
    def trigger_alert(self, alerts, frame, camera="cam_1"):
        now = time.time()

        if now - self.last_alert_time < self.cooldown:
            return

        self.last_alert_time = now

        filename = f"alert_{int(time.time())}.jpg"
        path = f"{SNAPSHOT_DIR}/{filename}"
        cv2.imwrite(path, frame)

        data = {
            "event": "ALERT",
            "message": "🚨 Bullying Detected!",
            "details": alerts,
            "camera": camera,
            "image": f"/image/{filename}",
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        mqtt_client.publish(MQTT_TOPIC_ALERT, json.dumps(data))

        print("🚨 Alert sent via MQTT")

        # 🔔 buzzer
        if self.buzzer_pin and hasattr(self, "GPIO") and self.GPIO:
            self.GPIO.output(self.buzzer_pin, 1)
            time.sleep(0.2)
            self.GPIO.output(self.buzzer_pin, 0)