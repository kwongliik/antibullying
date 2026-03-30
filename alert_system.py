# alert_system.py
# alert system using node-red for dashboard and telegram notifications. 
# This version focuses on MQTT communication and image handling, without Telegram integration.

import time
import os
import cv2
import json
import paho.mqtt.client as mqtt

# ================= CONFIG =================
MQTT_TOPIC_ALERT  = "school/alert"
MQTT_TOPIC_STATUS = "school/status"
SNAPSHOT_DIR      = "/home/pi5/.node-red/public/image"
# =========================================

mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


class AlertSystem:
    def __init__(self, cooldown=10):
        self.cooldown = cooldown
        self.last_alert_time = 0

    # ================= STATUS =================
    def startup_notify(self, frame=None, camera="cam_1"):
        filename = None

        if frame is not None:
            filename = f"startup_{int(time.time())}.jpg"
            path = f"{SNAPSHOT_DIR}/{filename}"
            cv2.imwrite(path, frame)

        data = {
            "event": "SYSTEM_START",
            "message": "🟢 Camera started monitoring",
            "camera": camera,
            "image": f"/image/{filename}" if filename else None,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        mqtt_client.publish(MQTT_TOPIC_STATUS, json.dumps(data))

    def shutdown_notify(self, frame=None, camera="cam_1"):
        filename = None

        if frame is not None:
            filename = f"shutdown_{int(time.time())}.jpg"
            path = f"{SNAPSHOT_DIR}/{filename}"
            cv2.imwrite(path, frame)

        data = {
            "event": "SYSTEM_STOP",
            "message": "🔴 Camera stopped monitoring",
            "camera": camera,
            "image": f"/image/{filename}" if filename else None,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        mqtt_client.publish(MQTT_TOPIC_STATUS, json.dumps(data))

    # ================= ALERT =================
    def trigger_alert(self, frame, confidence=0.9, camera="cam_1"):
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
            "confidence": confidence,
            "camera": camera,
            "image": f"/image/{filename}",
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        mqtt_client.publish(MQTT_TOPIC_ALERT, json.dumps(data))

        print("🚨 Alert sent via MQTT")

# ================= MAIN LOOP =================

cap = cv2.VideoCapture(0)
alert = AlertSystem()

ret, frame = cap.read()
if ret:
    alert.startup_notify(frame)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # 🔥 Replace with real AI later
        bullying_detected = True
        confidence = 0.91

        if bullying_detected:
            alert.trigger_alert(frame, confidence)

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping system...")

    ret, frame = cap.read()
    if ret:
        alert.shutdown_notify(frame)

cap.release()
mqtt_client.loop_stop()
mqtt_client.disconnect()