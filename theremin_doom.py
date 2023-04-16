import math
import time
import sys
import itertools

import pydirectinput
import pyautogui
import mido


def get_number(current_14_bit):
    return (current_14_bit[0] << 7) | current_14_bit[1]

def get_action(number, sections, actions, debug=False):
    for index, (start, end) in enumerate(itertools.pairwise(sections)):
        if debug:
            print(index, (start, end), number)
        if start <= number < end:
            return actions[index]


SHIFT = 4
MAX = (2**14 - 1) >> SHIFT

current_14_bit = [0, 0]
count = 0

VOLUME_ACTIONS = ['forward', 'neutral', 'shoot', 'neutral']
VOLUME_SECTIONS = [0, 40, 100, 127, 130]

PITCH_ACTIONS = ['left', 'neutral', 'right']
PITCH_SECTIONS = [0.0, 0.45, 0.55, 1.1]


time.sleep(2)
print('starting')
paused = False
last_pause = time.time()
pitch_keys_pressed = set()
volume_keys_pressed = set()

with mido.open_input() as inport:
    for msg in inport:
        count += 1
        match msg.type:
            case 'control_change':
                if msg.control == 2:
                    action = get_action(msg.value, VOLUME_SECTIONS, VOLUME_ACTIONS)
                    if action != 'shoot' and 'click' in volume_keys_pressed:
                        pydirectinput.mouseUp()
                        volume_keys_pressed.remove('click')
                        pydirectinput.keyUp('space')
                    
                    if action == 'shoot' and 'click' not in volume_keys_pressed:
                        pydirectinput.mouseDown()
                        pydirectinput.keyDown('space')
                        volume_keys_pressed.add('click')
                        print('shoot')
                    elif action == 'forward' and 'up' not in volume_keys_pressed:
                        pydirectinput.keyDown('up')
                        volume_keys_pressed.add('up')
                        print('up pressed')
                    elif action == 'back' and 'down' not in volume_keys_pressed:
                        pydirectinput.keyDown('down')
                        volume_keys_pressed.add('down')
                        print('down pressed')
                    elif action == 'neutral':
                        print('neutral')
                        for key in volume_keys_pressed.copy():
                            pydirectinput.keyUp(key)
                            volume_keys_pressed.remove(key)
                            print(key, 'released')
                        
                elif msg.control > 32:
                    # "coarse" / high bits
                    current_14_bit[1] = msg.value
                else:
                    # "fine" / low bits
                    current_14_bit[0] = msg.value
                fraction = 1 - ((get_number(current_14_bit) >> SHIFT) / MAX)

                action = get_action(fraction, PITCH_SECTIONS, PITCH_ACTIONS)
                if action == 'left' and 'left' not in pitch_keys_pressed:
                    pitch_keys_pressed.add('left')
                    pydirectinput.keyDown('left')
                elif action == 'right' and 'right' not in pitch_keys_pressed:
                    pitch_keys_pressed.add('right')
                    pydirectinput.keyDown('right')
                elif action == 'neutral':
                    for key in pitch_keys_pressed.copy():
                        pydirectinput.keyUp(key)
                        pitch_keys_pressed.remove(key)
                            




