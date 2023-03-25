import sys
import time
import json
import socket

sys.path.append("C:\\code\\dolphin_env\\venv\\Lib\\site-packages") # your python installation path
from PIL import Image
from pynput.keyboard import Controller, Key

from dolphin import event, gui, controller, savestate

sys.path.append("C:\\code\\dolphin_env\\Scripts") # path to the folder this file is in
import MKW_core

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

##### INITIALIZATIONS #####

# Initialize all our possible GCInputs.
# https://github.com/Felk/dolphin/blob/master/python-stubs/dolphin/controller.pyi
wheelie_forward = {'Left': False,
                    'Right': False,
                    'Down': False,
                    'Up': False, # We want to mash wheelie, not hold it, so leave it as False for now
                    'Z': False,
                    'R': False,
                    'L': False,
                    'A': True,
                    'B': False,
                    'X': False,
                    'Y': False,
                    'Start': False,
                    'StickX': 128,  # 0-255, 128 is neutral
                    'StickY': 128,  # 0-255, 128 is neutral
                    'CStickX': 128,  # 0-255, 128 is neutral
                    'CStickY': 128,  # 0-255, 128 is neutral
                    'TriggerLeft': 0,  # 0-255
                    'TriggerRight': 0,  # 0-255
                    'AnalogA': 0,  # 0-255
                    'AnalogB': 0,  # 0-255
                    'Connected': True}

wheelie_left = wheelie_forward.copy()
wheelie_left['StickX'] = 0

wheelie_right = wheelie_forward.copy()
wheelie_right['StickX'] = 255

drift_left = wheelie_forward.copy()
drift_left['B'] = True
drift_left['StickX'] = 0

drift_right = wheelie_forward.copy()
drift_right['B'] = True
drift_right['StickX'] = 255

drift_forward = wheelie_forward.copy()
drift_forward['B'] = True

# controller
keyboard = Controller()

# logging
log = open("C:\\code\\dolphin_env\\agent_script.log", 'w')
logging = False # set to true for debugging
if not logging:
    log.close()

# frame counter
red = 0xffff0000
frame_counter = 0

# socket
host = socket.gethostname()
port = 5555
sock = socket.socket()
sock.connect((host, port))

##### END INITIALIZATIONS #####
if logging:
    log.write("loading save state\n")
savestate.load_from_slot(1)

##### MAIN TRAINING LOOP #####
just_reset = False
while True:
    (width, height, data) = await event.framedrawn()
    
    # frame counter
    frame_counter += 1
    
    # mash wheelie (don't hold it)
    wheelie_forward['Up'] = not wheelie_forward['Up']
    wheelie_left['Up'] = wheelie_forward['Up']
    wheelie_right['Up'] = wheelie_forward['Up']

    # get game data
    speed = MKW_core.getXYZSpd()
    race_completion = MKW_core.getRaceCompletion()
    im = Image.frombytes('RGBA', (width, height), data).convert("L").resize((84, 84))
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
    
    # draw on screen
    gui.draw_text((10, 10), red, f"Frame: {frame_counter}")
    gui.draw_text((10, 30), red, f"Speed: {speed}")
    gui.draw_text((10, 50), red, f"Race Completion: {race_completion}")

    # get response from previous frame
    if not just_reset:
        if frame_counter == 1 or frame_counter % 8 == 0:
            message = json.loads(sock.recv(4096).decode('utf-8'))
            action = message[0]
            reset_requested = message[1]
        else:
            reset_requested = False
        
        if reset_requested:
            if logging:
                log.write("resetting\n")
            frame_counter = 0
            # workaround for save state load issue https://github.com/Felk/dolphin/issues/32
            keyboard.press(Key.f1)
            time.sleep(0.1)
            keyboard.release(Key.f1)
            just_reset = True
            continue
    else:
        just_reset = False

    # episode is done if speed falls below threshold or race is complete
    reward_set = False
    if speed < 37:
        reward = -10
        reward_set = True
        done = True
    elif race_completion == 4:
        reward = 10
        done = True
    else:
        done = False
    if frame_counter == 1 or frame_counter % 8 == 0:
        # send current frame's data and reward
        if not reward_set:
            reward = translate(speed, 0, 120, -1, 1)
        sock.send( ( json.dumps( (pixels, reward, done, frame_counter) ).encode("utf-8") ) )

    # send inputs
    if frame_counter == 1:
        controller.set_gc_buttons(0, wheelie_forward)
    elif action == -2:
        controller.set_gc_buttons(0, drift_left)
    elif action == -1:
        controller.set_gc_buttons(0, wheelie_left)
    elif action == 0:
        controller.set_gc_buttons(0, wheelie_forward)
    elif action == 1:
        controller.set_gc_buttons(0, wheelie_right)
    elif action == 2:
        controller.set_gc_buttons(0, drift_right)
    elif action == 3:
        controller.set_gc_buttons(0, drift_forward)