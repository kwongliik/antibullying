# 🛡️ VisionGuardian: AI-Based Anti-Bullying Detection System

## 📌 Overview
VisionGuardian is an AI-powered surveillance system designed to detect potential bullying incidents in real-time using computer vision and machine learning. The system runs on a Raspberry Pi and uses camera modules to monitor human behavior, identify aggressive actions, and trigger alerts.

---

## 🎯 Objectives
- Detect bullying-related actions using pose and motion analysis
- Reduce false alarms with improved AI detection logic
- Provide real-time alerts for early intervention
- Create a safer environment in schools and public spaces

---

## 🧠 Features
- 👁️ Real-time human detection using computer vision
- 🧍 Pose estimation to analyze body movements
- ⚠️ Aggressive behavior detection
- 😊 Emotion recognition
- 📩 Alert system (e.g., Telegram notifications)
- 📷 Support for single or dual camera setup

---

## 🛠️ Technologies Used
- Python
- OpenCV
- MediaPipe
- NumPy
- TensorFlow Lite (for emotion detection)
- Raspberry Pi 5
- Raspberry Pi Camera Module 3 (Wide / IR)

---

## 🧩 System Architecture
1. Camera captures video feed  
2. Frame processing using OpenCV  
3. Pose detection using MediaPipe  
4. Behavior analysis (movement + posture)  
5. Emotion detection  
6. Decision logic (bullying or not)  
7. Alert triggered if necessary  

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/kwongliik/antibullying.git
cd antibullying