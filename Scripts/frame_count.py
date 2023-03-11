from dolphin import event, gui

red = 0xffff0000
frame_counter = 0
while True:
    (width, height, data) = await event.framedrawn()
    frame_counter += 1
    # draw on screen
    gui.draw_text((10, 10), red, f"Frame: {frame_counter}")
    # print to console
    if frame_counter % 60 == 0:
        print(f"The frame count has reached {frame_counter}")