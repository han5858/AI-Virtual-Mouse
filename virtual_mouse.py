import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import time

# --- GÜVENLİ KÜTÜPHANE YÜKLEME ---
try:
    mpHands = mp.solutions.hands
    mpDraw = mp.solutions.drawing_utils
except AttributeError:
    import mediapipe.python.solutions.hands as mp_hands
    import mediapipe.python.solutions.drawing_utils as mp_drawing
    mpHands = mp_hands
    mpDraw = mp_drawing

# --- AYARLAR ---
wCam, hCam = 640, 480       
frameR = 100                
smoothening = 5             

pTime = 0
plocX, plocY = 0, 0         
clocX, clocY = 0, 0         

# --- AKILLI KAMERA BULUCU FONKSİYONU 🕵️‍♂️ ---
def start_camera():
    # 0'dan 3'e kadar tüm kamera portlarını dene
    for i in range(3):
        print(f"[DENENIYOR] Kamera Portu: {i}...")
        # cv2.CAP_DSHOW Windows için daha hızlı açılmasını sağlar
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ BAŞARILI! Kamera {i} portunda bulundu.")
                cap.set(3, wCam)
                cap.set(4, hCam)
                return cap
            else:
                cap.release()
    return None

# Kamerayı başlat
cap = start_camera()

if cap is None:
    print("\n❌ KRİTİK HATA: Hiçbir kamera açılamadı!")
    print("Lütfen şunları kontrol et:")
    print("1. 'Kamera Gizlilik Ayarları'ndan masaüstü uygulamalarına izin ver.")
    print("2. Antivirüs programın kamerayı engelliyor olabilir.")
    print("3. Zoom/Discord/Teams kapalı mı?")
    exit() # Programı durdur

# El Takip Modelini Başlat
hands = mpHands.Hands(max_num_hands=1, 
                      min_detection_confidence=0.7,
                      min_tracking_confidence=0.7)

wScr, hScr = pyautogui.size()

print("\n[BILGI] Sanal Mouse Aktif! Çıkmak için 'q' bas. ✋")

while True:
    # 1. Görüntüyü Al
    success, img = cap.read()
    
    if not success or img is None:
        print("Görüntü koptu, tekrar deneniyor...")
        continue

    img = cv2.flip(img, 1) # Aynalama (Sağ el sağda görünsün)
    
    # 2. El İşaretlerini Bul
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    # El görüldü mü?
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            # 3. Parmak Uçlarını Al
            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]  # İşaret Parmağı
                x2, y2 = lmList[12][1:] # Orta Parmak
                
                # 4. Hangi Parmaklar Havada?
                fingers = []
                # Başparmak
                if lmList[4][0] > lmList[3][0]: fingers.append(1)
                else: fingers.append(0)
                
                # Diğer 4 parmak
                tipsIds = [8, 12, 16, 20]
                for id in tipsIds:
                    if lmList[id][2] < lmList[id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                # 5. Hareket Modu: Sadece İşaret Parmağı Havadaysa
                if fingers[1] == 1 and fingers[2] == 0:
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                    
                    clocX = plocX + (x3 - plocX) / smoothening
                    clocY = plocY + (y3 - plocY) / smoothening
                    
                    try:
                        pyautogui.moveTo(clocX, clocY)
                    except:
                        pass
                        
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    plocX, plocY = clocX, clocY
                    
                # 6. Tıklama Modu: İşaret ve Orta Parmak Havadaysa
                if fingers[1] == 1 and fingers[2] == 1:
                    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    
                    if length < 40:
                        cv2.circle(img, ((x1+x2)//2, (y1+y2)//2), 15, (0, 255, 0), cv2.FILLED)
                        pyautogui.click()
                        print("🖱️ Tıklandı!")

    # 7. Ekranda Göster
    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()