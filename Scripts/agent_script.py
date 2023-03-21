import sys
import time
sys.path.append("C:\\code\\dolphin_env\\venv\\Lib\\site-packages") # your python installation path

from PIL import Image
from pynput.keyboard import Controller, Key

from dolphin import event, gui, controller, savestate

sys.path.append("C:\\code\\dolphin_env\\Scripts") # path to the folder this file is in
import MKW_core

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

# Misc initializations
keyboard = Controller()
log = open("C:\\code\\dolphin_env\\agent_script.log", 'w')
logging = False # set to true for debugging
if not logging:
    log.close()
red = 0xffff0000
frame_counter = 0

if logging:
    log.write("loading save state\n")
savestate.load_from_slot(1)

##### MAIN TRAINING LOOP #####
while True:
    (width, height, data) = await event.framedrawn()
    
    # frame counter
    frame_counter += 1
    
    # mash wheelie (don't hold it)
    wheelie_forward['Up'] = not wheelie_forward['Up']
    wheelie_left['Up'] = wheelie_forward['Up']
    wheelie_right['Up'] = wheelie_forward['Up']

    # reset if speed falls below threshold
    speed = MKW_core.getXYZSpd()
    if speed < 37:
        if logging:
            log.write("resetting\n")
        frame_counter = 0
        # workaround for save state load issue https://github.com/Felk/dolphin/issues/32
        keyboard.press(Key.f1)
        time.sleep(0.1)
        keyboard.release(Key.f1)
        continue

    # get image data
    im = Image.frombytes('RGBA', (width, height), data).convert("L").resize((188, 102))
    pixels = list(im.getdata())
    # width, height = im.size
    # pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    # send model data and reward, wait for response (inputs)

    # draw on screen
    gui.draw_text((10, 10), red, f"Frame: {frame_counter}")
    gui.draw_text((10, 30), red, f"Speed: {speed}")

    # send inputs
    if frame_counter >= 150 and frame_counter < 200:
        controller.set_gc_buttons(0, drift_right)
    else:
        controller.set_gc_buttons(0, wheelie_forward)
