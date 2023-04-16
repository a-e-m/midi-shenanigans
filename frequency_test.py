import math
import threading
import queue
import time
import sys

import pydirectinput
import pyautogui
import mido

start = time.time()
count = 0
with mido.open_input() as inport:
    for msg in inport:
        elapsed = time.time() - start
        if elapsed > 500:
            break
        print(msg)
        match msg.type:
            case 'control_change':
                count += 1

print(count, elapsed, count / elapsed)
