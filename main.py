

import cv2
import mediapipe as mp
import pyautogui
import time
import math

def is_fist(landmarks, w, h):
    tips = [8, 12, 16, 20]
    wrist = landmarks[0]
    wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
    closed = 0
    for tip_id in tips:
        tip = landmarks[tip_id]
        tip_x, tip_y = int(tip.x * w), int(tip.y * h)
        distance = math.hypot(tip_x - wrist_x, tip_y - wrist_y)
        if distance < 60:
            closed += 1
    return closed >= 3 

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

prev_x, prev_y = 0, 0
gesture_delay = 0.0  
last_gesture_time = time.time()
game_started = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    h, w, _ = img.shape

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        lm_list = handLms.landmark

        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        if not game_started and is_fist(lm_list, w, h):
            print("✊ Fist detected! Starting game...")
            pyautogui.press('space') 
            game_started = True
            time.sleep(1)

        index_finger = lm_list[8]
        curr_x = int(index_finger.x * w)
        curr_y = int(index_finger.y * h)

        cv2.circle(img, (curr_x, curr_y), 10, (255, 0, 255), cv2.FILLED)

        dx = curr_x - prev_x
        dy = curr_y - prev_y

        threshold = 20
        current_time = time.time()

        if current_time - last_gesture_time > gesture_delay:
            if abs(dx) > abs(dy):
                if dx > threshold:
                    print("👉 Swipe Right")
                    pyautogui.press('right')
                    last_gesture_time = current_time
                elif dx < -threshold:
                    print("👈 Swipe Left")
                    pyautogui.press('left')
                    last_gesture_time = current_time
            else:
                if dy < -threshold:
                    print("👆 Swipe Up")
                    pyautogui.press('up')
                    last_gesture_time = current_time
                elif dy > threshold:
                    print("👇 Swipe Down")
                    pyautogui.press('down')
                    last_gesture_time = current_time

        prev_x, prev_y = curr_x, curr_y

    cv2.imshow("Index Finger Swipe Control + Fist Start", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
