import cv2
import numpy as np
import pydirectinput
import mss
import time
import keyboard
import random

THRESHOLD_VALUE = 180 
BAN_OFFSET_Y = 50 
BAN_OFFSET_X = 70 

sct = mss.mss()
W, H = pydirectinput.size()
active = False
last_anti_idle = time.time()
last_ui_interaction = time.time()


pydirectinput.PAUSE = 0.001

print("---  ABA Macro  ---")
print("Press F1 to Start/Pause")
print("Press ESC to Kill Script")

def screen_capture():
    monitor = {"top": 0, "left": 0, "width": W, "height": H}
    img = np.array(sct.grab(monitor))
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def find_all_images(needle_image, haystack_image):
    result = cv2.matchTemplate(haystack_image, needle_image, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= 0.8)
    points = []
    h, w = needle_image.shape[:2]
    for pt in zip(*loc[::-1]):
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        is_new = True
        for p in points:
            if abs(p[0] - center_x) < 20 and abs(p[1] - center_y) < 20:
                is_new = False
                break
        if is_new:
            points.append((center_x, center_y))
    return points

def find_text_shape(needle_image, haystack_image):
    needle_gray = cv2.cvtColor(needle_image, cv2.COLOR_BGR2GRAY)
    haystack_gray = cv2.cvtColor(haystack_image, cv2.COLOR_BGR2GRAY)
    _, needle_mask = cv2.threshold(needle_gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    _, haystack_mask = cv2.threshold(haystack_gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    result = cv2.matchTemplate(haystack_mask, needle_mask, cv2.TM_CCORR_NORMED)
    loc = np.where(result >= 0.85) 
    points = []
    h, w = needle_image.shape[:2]
    for pt in zip(*loc[::-1]):
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        is_new = True
        for p in points:
            if abs(p[0] - center_x) < 20 and abs(p[1] - center_y) < 20:
                is_new = False
                break
        if is_new:
            points.append((center_x, center_y))
    return points

def move_with_hover(x, y):
    """Moves to x,y then wiggles 1 pixel around to trigger hover state."""
    pydirectinput.moveTo(x, y)
    time.sleep(0.01)
    
   
    
    pydirectinput.moveRel(0, -1) 
    time.sleep(0.005)
    
    pydirectinput.moveRel(-1, 0)
    time.sleep(0.005)
    
    pydirectinput.moveRel(0, 1)
    time.sleep(0.005)
    
    pydirectinput.moveRel(1, 0) 
    time.sleep(0.005)

def unlock_and_click(x, y):
    move_with_hover(x, y)
    
    for _ in range(3):
        pydirectinput.click()
        time.sleep(0.01)
    pydirectinput.press('k')
    time.sleep(0.05) 
    for _ in range(3):
        pydirectinput.click()
        time.sleep(0.01)

def reset_lives_combo():
    pydirectinput.press('esc')
    time.sleep(0.05)
    pydirectinput.press('r')
    time.sleep(0.05)
    pydirectinput.press('enter')

def perform_random_wiggle():
    print("Waiting for Lives... Wiggling Mouse.")
    x_move = random.randint(-100, 100)
    y_move = random.randint(-100, 100)
    
    current_x, current_y = pydirectinput.position()
    move_with_hover(current_x + x_move, current_y + y_move)
    time.sleep(0.1)

try:
    img_rematch = cv2.imread('rematch.png')
    img_map_ban = cv2.imread('map_ban.png')
    img_select  = cv2.imread('select.png')
    img_pass    = cv2.imread('pass_ban.png')
    img_lives   = cv2.imread('lives.png')
except:
    print("ERROR: Images missing nitter")

while True:
    if keyboard.is_pressed('esc'):
        print("Script Terminated.")
        break

    if keyboard.is_pressed('f1'):
        active = not active
        print(f"Macro Active: {active}")
        last_ui_interaction = time.time()
        time.sleep(0.5)

    if not active:
        time.sleep(0.1)
        continue

    screen = screen_capture()


    rematches = find_all_images(img_rematch, screen)
    if rematches:
        print(f"Action: Rematch")
        for pt in rematches:
            unlock_and_click(pt[0], pt[1])
        last_ui_interaction = time.time()
        time.sleep(0.5)
        continue

 
    bans = find_all_images(img_map_ban, screen)
    if bans:
        print("Action: Map Ban")
        for pt in bans:
            # The wiggle happens inside unlock_and_click
            unlock_and_click(pt[0] - BAN_OFFSET_X, pt[1] + BAN_OFFSET_Y)
            unlock_and_click(pt[0] + BAN_OFFSET_X, pt[1] + BAN_OFFSET_Y)
        last_ui_interaction = time.time()
        continue


    passes = find_all_images(img_pass, screen)
    if passes:
        print("Action: Pass Ban")
        for pt in passes:
            unlock_and_click(pt[0], pt[1])
        last_ui_interaction = time.time()
        continue

  
    selects = find_all_images(img_select, screen)
    if selects:
        print("Action: Select")
        for pt in selects:
            unlock_and_click(pt[0], pt[1])
        last_ui_interaction = time.time()
        continue


    lives = find_text_shape(img_lives, screen)
    if lives:
        print("Action: Resetting Lives...")
        target_x = int(W * 0.75)
        target_y = int(H / 2)
        unlock_and_click(target_x, target_y)
        reset_lives_combo()
        last_ui_interaction = time.time()
        time.sleep(1.5) 
        continue


    if time.time() - last_ui_interaction > 18:
        perform_random_wiggle()


    if time.time() - last_anti_idle > 5:
        pydirectinput.click(button='right')
        time.sleep(0.05)
        pydirectinput.click(button='right')
        last_anti_idle = time.time()

    time.sleep(0.05)