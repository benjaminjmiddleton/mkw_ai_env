import sys
sys.path.append("C:\\code\\dolphin_env\\venv\\Lib\\site-packages")
from dolphin import event, gui, controller
from PIL import Image

red = 0xffff0000
frame_counter = 0

# Initialize all our possible inputs.
wheelie_forward = {'Left': False,
                    'Right': False,
                    'Down': False,
                    'Up': False,
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

while True:
    (width, height, data) = await event.framedrawn()
    
    # mash wheelie (don't hold it)
    wheelie_forward['Up'] = not wheelie_forward['Up']
    wheelie_left['Up'] = wheelie_forward['Up']
    wheelie_right['Up'] = wheelie_forward['Up']

    # reset if speed falls below threshold
    # if speed < 37:
    #     reset()
    #     frame_counter = 0
    #     continue

    # get image data
    im = Image.frombytes('RGBA', (width, height), data).convert("L").resize((188, 102))
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    # send inputs
    if frame_counter >= 150 and frame_counter < 200:
        controller.set_gc_buttons(0, drift_right)
    else:
        controller.set_gc_buttons(0, wheelie_forward)

    # frame counter
    frame_counter += 1
    # draw on screen
    gui.draw_text((10, 10), red, f"Frame: {frame_counter}")
    # print to console
    if frame_counter % 60 == 0:
        print(f"The frame count has reached {frame_counter}")