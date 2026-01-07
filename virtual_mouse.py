import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import time

# --- SAFE LIBRARY IMPORT ---
try:
    mpHands = mp.solutions.hands
    mpDraw = mp.solutions.drawing_utils
except AttributeError:
    import mediapipe.python.solutions.hands as mp_hands
    import mediapipe.python.solutions.drawing_utils as mp_drawing
    mpHands = mp_hands
    mpDraw = mp_drawing

# --- SETTINGS ---
wCam, hCam = 640, 480       # Camera Width & Height
frameR = 100                # Frame Reduction (Margin)
smoothening = 5             # Smoothing Factor

pTime = 0
plocX, plocY = 0, 0         # Previous Location
clocX, clocY = 0, 0         # Current Location

# --- SMART CAMERA FINDER FUNCTION 🕵️‍♂️ ---
def start_camera():
    # Try all camera ports from 0 to 3
    for i in range(3):
        print(f"[TESTING] Camera Port: {i}...")
        # cv2.CAP_DSHOW enables faster startup on Windows
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ SUCCESS! Camera found on port {i}.")
                cap.set(3, wCam)
                cap.set(4, hCam)
                return cap
            else:
                cap.release()
    return None

# Start the Camera
cap = start_camera()

if cap is None:
    print("\n❌ CRITICAL ERROR: No camera could be opened!")
    print("Please check the following:")
    print("1. Allow desktop apps in Windows 'Camera Privacy Settings'.")
    print("2. Check if your antivirus is blocking the camera.")
    print("3. Are Zoom/Discord/Teams closed?")
    exit() # Stop the program

# Initialize Hand Tracking Model
hands = mpHands.Hands(max_num_hands=1, 
                      min_detection_confidence=0.7,
                      min_tracking_confidence=0.7)

wScr, hScr = pyautogui.size() # Get Screen Size

print("\n[INFO] Virtual Mouse Active! Press 'q' to exit. ✋")

while True:
    # 1. Get the Frame
    success, img = cap.read()
    
    if not success or img is None:
        print("Frame lost, retrying...")
        continue

    img = cv2.flip(img, 1) # Mirror the image (Right hand appears on the right)
    
    # 2. Detect Hand Landmarks
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    # Is a hand detected?
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            # 3. Get Finger Tips
            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]  # Index Finger Tip
                x2, y2 = lmList[12][1:] # Middle Finger Tip
                
                # 4. Which Fingers are Up?
                fingers = []
                # Thumb
                if lmList[4][0] > lmList[3][0]: fingers.append(1)
                else: fingers.append(0)
                
                # Other 4 fingers
                tipsIds = [8, 12, 16, 20]
                for id in tipsIds:
                    if lmList[id][2] < lmList[id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                # 5. Moving Mode: Only Index Finger Up
                if fingers[1] == 1 and fingers[2] == 0:
                    # Convert Coordinates (Camera -> Screen)
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                    
                    # Smoothing
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening
                    
                    try:
                        pyautogui.moveTo(clocX, clocY)
                    except:
                        pass
                        
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY
                    
                # 6. Clicking Mode: Both Index and Middle Fingers Up
                if fingers[1] == 1 and fingers[2] == 1:
                    # Calculate distance between fingers
                    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    
                    # If fingers are close, CLICK
                    if length < 40:
                        cv2.circle(img, ((x1+x2)//2, (y1+y2)//2), 15, (0, 255, 0), cv2.FILLED)
                        pyautogui.click()
                        print("🖱️ Clicked!")

    # 7. Display on Screen
    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
