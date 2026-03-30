import paho.mqtt.client as mqtt
import json
import cv2
import time
from datetime import datetime

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

# Open camera (Camera Module 3)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Create unique filename (VERY IMPORTANT)
    timestamp = int(time.time())
    filename = f"alert_{timestamp}.jpg"

    save_path = f"/home/pi5/.node-red/public/image/{filename}"

    # Save image
    cv2.imwrite(save_path, frame)

    # Prepare MQTT data
    data = {
        "event": "Bullying Detected",
        "confidence": 0.91,
        "camera": "cam_1",
        "image": f"/image/{filename}",   # URL path (NOT full path)
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    client.publish("school/alert", json.dumps(data))

    time.sleep(2)  # adjust interval (e.g., every 2 seconds)

cap.release()
client.disconnect()