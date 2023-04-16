import math
import threading
import queue
import time
import sys

import pydirectinput
import pyautogui
import mido

def get_box():
    window = pyautogui.getWindowsWithTitle('Peggle Deluxe')[0]
    print(window)
    return window.box

def clamp(x, y, box):
    if box:
        x = min(max(x, box.left), box.left + box.width)
        y = min(max(y, box.top), box.top + box.height)
    return x, y

def go_to_angle(degrees, box):
    angle = math.radians(180 - degrees)
    x = box.left + (box.width // 2)
    y = box.top + int(box.height * 0.155)
    angle_dist = box.width // 5
    x += math.cos(angle) * angle_dist
    y += math.sin(angle) * angle_dist
    x, y = clamp(x, y, box)
    pydirectinput.moveTo(int(x), int(y))

def get_number(current_14_bit):
    return (current_14_bit[0] << 7) | current_14_bit[1]

SHIFT = 4
MAX = (2**14 - 1) >> SHIFT

box = get_box()
current_14_bit = [0, 0]
count = 0

q = queue.LifoQueue()

def worker():
    highest_count = -1
    previous = None
    while True:
        angle, count, mode = q.get()
        if count > highest_count and (angle != previous or mode == 'menu'):
            highest_count = count
            if mode == 'game':
                go_to_angle(angle, box)
            else:
                x = box.left + (box.width // 2)
                y = box.top + (box.height * angle)
                pydirectinput.moveTo(int(x), int(y))
        q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

time.sleep(2)
print('starting')
paused = False
last_pause = time.time()
with mido.open_input() as inport:
    for msg in inport:
        count += 1
        match msg.type:
            case 'control_change':
                angle_change = False
                if msg.control == 2:
                    # volume control on theremin
                    if msg.value == 0:
                        pyautogui.moveTo(box.left + (box.width // 2), box.top + int(box.height * 0.7))
                        pyautogui.click()
                    elif msg.value < 90:
                        pydirectinput.click()
                elif msg.control > 32:
                    # "coarse" / high bits
                    current_14_bit[1] = msg.value
                else:
                    # "fine" / low bits
                    current_14_bit[0] = msg.value
                fraction = 1 - ((get_number(current_14_bit) >> SHIFT) / MAX)
                if fraction == 0 and (time.time() - last_pause) > 1:
                    last_pause = time.time()
                    paused = not paused
                    print('pause state:', paused)
                if paused:
                    q.put((fraction, count, 'menu'))
                else:
                    q.put((fraction * 180, count, 'game'))




