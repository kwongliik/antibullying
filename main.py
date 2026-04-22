# main.py
import cv2
import time
from camera_module import CameraModule
from pose_detector import PoseDetector
from crowd_detector import CrowdDetector
from emotion_detector import EmotionDetector
from alert_system import AlertSystem   # ← handles everything

# ============================================
# ⚙️ SETTINGS
# ============================================

def draw_overlay(frame, all_alerts, person_count):
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    # Status
    if all_alerts:
        cv2.putText(frame, "WARNING: ALERT DETECTED", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "MONITORING", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Bottom info bar
    info = f"{time.strftime('%Y-%m-%d %H:%M:%S')}   |   Persons: {person_count}"
    cv2.putText(frame, info, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    # Alert messages on screen
    for i, msg in enumerate(all_alerts[:4]):
        cv2.putText(frame, msg, (10, 90 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)

    return frame

def main():
    print("🛡️  Starting Anti-Bullying Detection System...")

    # ── Initialize modules ───────────────────────────────────
    camera        = CameraModule(width=1280, height=720)
    pose          = PoseDetector()
    crowd         = CrowdDetector()
    emotion       = EmotionDetector()
    alert_system  = AlertSystem(buzzer_pin=17, cooldown=30)  # ← one object does all

    print("✅  All modules ready.")
    alert_system.startup_notify()   # 📲 Telegram: system started
    print("🎥  Monitoring started. Press 'q' or Ctrl+C to quit.\n")

    frame_count = 0
    confidence = 0.0
    alert_counter = 0
    ALERT_CONFIRM_FRAMES = 3 # initially set to 3 for more robustness, but can be reduced for demo/testing purposes

    try:
        while True:
            frame        = camera.get_frame()
            all_alerts   = []
            person_count = 0

            # ── Run detections every 2nd frame ───────────────────
            if frame_count % 2 == 0:
                frame, pose_alerts = pose.detect(frame)
                frame, crowd_alerts, person_count, confidence = crowd.detect(frame)
                frame, emotion_alerts = emotion.detect_faces(frame)                  
                
                if person_count == 0:
                    pose_alerts = []
                    emotion_alerts = []
                    crowd_alerts = []
                
                pose_flag = len(pose_alerts) > 0
                crowd_flag = len(crowd_alerts) > 0
                emotion_flag = len(emotion_alerts) > 0

                all_alerts = pose_alerts + crowd_alerts + emotion_alerts

                # Only trust detections if at least 1 person detected
                valid_detection = (person_count > 0 and confidence > 0.65)

                # Default
                trigger = False

                # if valid_detection:
                # Strong case: physical aggression
                    # if pose_flag:
                    #     trigger = True

                    # # Medium case: crowd + negative emotion
                    # elif crowd_flag and emotion_flag and person_count >= 2:
                    #     trigger = True            

                DEMO_MODE = False

                threshold = 2 if DEMO_MODE else 4 # in demo mode, we want to see alerts more easily, so we lower the threshold

                score = 0

                if pose_flag:
                    score += 2

                if emotion_flag:
                    score += 1

                if crowd_flag:
                    score += 1

                if person_count >= 2:
                    score += 1

                # validity control
                if not DEMO_MODE and not valid_detection:
                    score = 0

                trigger = score >= threshold
                
            # ── Draw overlay and show frame ───────────────────────
            frame = draw_overlay(frame, all_alerts, person_count)
            cv2.imshow("Anti-Bullying Monitor", frame)
            frame_count += 1

            if trigger:
                alert_counter += 1
            else:
                alert_counter = max(0, alert_counter - 0.5) # decay counter if no alert, but don't let it go negative

            print(f"[DEBUG_1] Pose={pose_flag} | Emotion={emotion_flag} | Crowd={crowd_flag} | Persons={person_count}")
            print(f"[DEBUG_2] Score={score} | Threshold={threshold} | Trigger={trigger} | Counter={alert_counter}")
            
            if alert_counter >= ALERT_CONFIRM_FRAMES:
                print("🚨 ALERT TRIGGERED!")
                alert_system.trigger_alert(all_alerts, frame, confidence)
                alert_counter = 0            

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n🔴 Keyboard interrupt received. Shutting down...")

    finally:
        # ── Clean shutdown ─────────────────────────────
        alert_system.shutdown_notify()  # 📲 Telegram: system stopped
        camera.release()
        cv2.destroyAllWindows()
        print("✅  Done.")    

if __name__ == "__main__":
    main()
