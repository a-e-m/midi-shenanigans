import math

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

# pydirectinput.press('enter')

LOW = 21
HIGH = 108

box = get_box()
current_notes = set()
with mido.open_input() as inport:
    for msg in inport:
        match msg.type:
            case 'control_change':
                if msg.value > 64:
                    pydirectinput.click()
            case 'note_on':
                if msg.velocity > 10:
                    current_notes.add(msg.note)
                    fraction = sum((n - LOW) / (HIGH - LOW) for n in current_notes)
                    fraction /= len(current_notes)
                    print(fraction * 180)
                    go_to_angle(fraction * 180, box)
                else:
                    current_notes.remove(msg.note)



