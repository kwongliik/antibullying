# telegram_alert.py
import requests
import cv2
import time

class TelegramAlert:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text):
        """Send a text message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print("  ✅ Telegram message sent!")
            else:
                print(f"  ❌ Telegram error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Network error: {e}")

    def send_photo(self, frame, caption=""):
        """Send a photo snapshot to Telegram"""
        url = f"{self.base_url}/sendPhoto"
        
        # Encode frame as JPEG in memory
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        try:
            response = requests.post(
                url,
                data={"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"},
                files={"photo": ("alert.jpg", img_bytes, "image/jpeg")},
                timeout=15
            )
            if response.status_code == 200:
                print("  ✅ Telegram photo sent!")
            else:
                print(f"  ❌ Telegram photo error: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Network error: {e}")

    def trigger_alert(self, alert_messages, frame=None):
        """Main alert trigger with cooldown"""
        #current_time = time.time()
        #if current_time - self.last_alert_time < self.cooldown:
        #    return  # Prevent spam

        #self.last_alert_time = current_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Build message
        message = (
            f"🚨 *ANTI-BULLYING ALERT*\n"
            f"🕐 Time: `{timestamp}`\n"
            f"📍 Location: *Main Hallway Cam*\n\n"
            f"⚠️ *Detected:*\n"
        )
        for alert in alert_messages:
            message += f"  • {alert}\n"

        # Send photo with caption if frame available, else text only
        if frame is not None:
            self.send_photo(frame, caption=message)
        else:
            self.send_message(message)
