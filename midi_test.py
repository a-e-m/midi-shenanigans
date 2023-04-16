import pydirectinput
import pyautogui
import mido

def get_box():
    window = pyautogui.getWindowsWithTitle('Peggle')[0]
    return window.box
print(get_box())

ANGLE_DIST = 300

def clamp(x, y, box):
    if box:
        x = min(max(x, box.left), box.left + box.width)
        y = min(max(y, box.top), box.top + box.height)
    return x, y

def go_to_angle(degrees):
    angle = math.radians(90 - degrees + 90)
    x = box.left + (box.width // 2)
    y = box.top + int(box.height * 0.155)
    x += math.cos(angle) * ANGLE_DIST
    y += math.sin(angle) * ANGLE_DIST
    x, y = clamp(x, y, box)
    pydirectinput.moveTo(int(x), int(y))

# pydirectinput.press('enter')

LOW = 21
HIGH = 108
mapping = {
    48: 'left',
    50: 'down',
    52: 'up',
    53: 'right'
}

count = 0
with mido.open_input() as inport:
    for msg in inport:
        match msg.type:
            case 'control_change':
                if msg.value > 64:
                    print('pedal on')
                else:
                    print('pedal off')
            case 'note_on':
                print(msg)
                key = mapping.get(msg.note)
                if msg.velocity > 10:
                    pydirectinput.keyDown(key)
                else:
                    pydirectinput.keyUp(key)

