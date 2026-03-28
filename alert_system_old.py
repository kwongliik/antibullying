# alert_system.py
import time
import os
import cv2
from telegram_alert import TelegramAlert

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - buzzer disabled")

# ============================================
# 🔐 TELEGRAM CREDENTIALS - UPDATE THESE!
# ============================================
BOT_TOKEN = "8665422111:AAGHGCtHebUa42qw03ZEixF2A2b3m4g3E40"
CHAT_ID   = "-1003832162300"

SNAPSHOT_DIR = "/home/pi/antibullying/alerts"

class AlertSystem:
    def __init__(self, buzzer_pin=17, cooldown=30):
        self.cooldown         = cooldown
        self.last_alert_time  = 0
        self.telegram         = TelegramAlert(BOT_TOKEN, CHAT_ID)

        # Setup buzzer
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(buzzer_pin, GPIO.OUT)
            self.buzzer_pin = buzzer_pin

        os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    def startup_notify(self):
        """Send Telegram message when system starts"""
        print("📲  Sending startup notification...")
        self.telegram.send_message(
            "🟢 *Anti-Bullying System Started*\n"
            f"🕐 Time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            "📷 Camera is now monitoring."
        )

    def shutdown_notify(self):
        """Send Telegram message when system stops"""
        print("📲  Sending shutdown notification...")
        self.telegram.send_message(
            "🔴 *Anti-Bullying System Stopped*\n"
            f"🕐 Time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`"
        )

    def trigger_alert(self, alert_messages, frame=None):
        """Main alert trigger — buzzer + snapshot + Telegram"""
        current_time = time.time()
        if current_time - self.last_alert_time < self.cooldown:
            return  # still in cooldown, skip

        self.last_alert_time = current_time
        print("\n🚨 ALERT TRIGGERED!")
        for msg in alert_messages:
            print(f"   {msg}")

        # 1️⃣ Sound buzzer
        self._sound_buzzer()

        # 2️⃣ Save snapshot locally
        if frame is not None:
            timestamp     = time.strftime("%Y%m%d_%H%M%S")
            snapshot_path = f"{SNAPSHOT_DIR}/alert_{timestamp}.jpg"
            cv2.imwrite(snapshot_path, frame)
            print(f"   📸 Snapshot saved: {snapshot_path}")

        # 3️⃣ Send Telegram alert with photo
        self.telegram.trigger_alert(alert_messages, frame)

    def _sound_buzzer(self, duration=2):
        if GPIO_AVAILABLE:
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
