import time
import threading
import queue

import pydirectinput
import pyautogui
import mido

def get_box():
    window = pyautogui.getWindowsWithTitle('Stella')[0]
    print(window)
    return window.box

def get_number(current_14_bit):
    return (current_14_bit[0] << 7) | current_14_bit[1]

q = queue.LifoQueue()

def worker():
    highest_count = -1
    previous = None
    while True:
        fraction, count = q.get()
        if count > highest_count and fraction != previous:
            highest_count = count
            x = box.left + box.width * ((fraction + 0.2) / 2.0)
            y = box.top + box.height // 2
            previous = fraction
            pydirectinput.moveTo(int(x), int(y))
        q.task_done()

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

SHIFT = 8
MAX = (2**14 - 1) >> SHIFT

time.sleep(2)
print('starting')
box = get_box()
current_14_bit = [0, 0]
paused = False
last_pause = time.time()
count = 0
last_space = time.time()
with mido.open_input() as inport:
    for msg in inport:
        count += 1
        if msg.control == 2:
            # volume antenna
            if msg.value < 50 and (time.time() - last_space) > 1:
                pydirectinput.press('space')
                last_space = time.time()
                print('space', last_space)
                continue
        elif msg.control > 32:
            # "fine" / low bits
            current_14_bit[1] = msg.value
            pos_changed = True
        else:
            # "coarse" / high bits
            current_14_bit[0] = msg.value
        fraction = (get_number(current_14_bit) >> SHIFT) / MAX
        if fraction == 1.0 and (time.time() - last_pause) > 1:
            last_pause = time.time()
            paused = not paused
            print('pause state:', paused)
        elif not paused:
            q.put((fraction, count))
