# 🖱️ AI Virtual Mouse (Gesture Control)

![Python](https://img.shields.io/badge/Python-3.x-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Computer%20Vision-green)
![Status](https://img.shields.io/badge/Status-Working-success)

## 📖 Overview
This project allows you to control your computer mouse using **hand gestures** via the webcam. No external hardware is needed! It uses **Google MediaPipe** for hand tracking and **OpenCV** for image processing.

It is a perfect example of **HCI (Human-Computer Interaction)** using Computer Vision.

### ✨ Features
* **Move Mouse:** Point with your **Index Finger** to move the cursor.
* **Left Click:** Bring your **Index and Middle Finger** together to click.
* **Smooth Movement:** Includes a smoothing algorithm to prevent cursor shaking.

---

## 🛠️ How It Works
The system tracks 21 hand landmarks using MediaPipe.
1.  **Movement:** It maps the coordinates of the *Index Finger Tip (Landmark 8)* to the screen resolution.
2.  **Clicking:** It calculates the distance between *Index Finger (8)* and *Middle Finger (12)*. If the distance is short, it triggers a click.

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/han5858/AI-Virtual-Mouse.git](https://github.com/han5858/AI-Virtual-Mouse.git)
cd AI-Virtual-Mouse
