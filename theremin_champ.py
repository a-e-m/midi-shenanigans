import math
import threading
import queue
import time
import sys

import pydirectinput
import pyautogui
import mido

def get_box():
    window = pyautogui.getWindowsWithTitle('Trombone')[0]
    print(window)
    return window.box

def clamp(x, y, box):
    if box:
        x = min(max(x, box.left), box.left + box.width)
        y = min(max(y, box.top), box.top + box.height)
    return x, y



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
        position, count, mode = q.get()
        if count > highest_count and position != previous:
            highest_count = count
            if mode == 'move':
                x = box.left + (box.width // 2)
                y = box.top + (box.height * position)
            pydirectinput.moveTo(int(x), int(y))
        q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

time.sleep(2)
print('starting')
paused = False
last_pause = time.time()
mouse_down = False
with mido.open_input() as inport:
    for msg in inport:
        count += 1
        match msg.type:
            case 'control_change':
                if msg.control == 2:
                    if msg.value > 60:
                        if not mouse_down:
                            pydirectinput.mouseDown()
                            mouse_down = True
                    elif mouse_down:
                        pydirectinput.mouseUp()
                        mouse_down = False
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
                if not paused:
                    q.put((fraction, count, 'move'))




