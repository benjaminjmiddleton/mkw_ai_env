import sys

from dolphin import event, gui

sys.path.append("C:\\code\\dolphin_env\\Scripts") # path to the folder this file is in
import MKW_Pointers
import MKW_core

red = 0xffff0000
frame_counter = 0
while True:
    (width, height, data) = await event.framedrawn()
    frame_counter += 1
    game_id = MKW_Pointers.GetGameID()
    prevPosPointer = MKW_Pointers.getPrevPositionPointer(0x0)
    posPointer = MKW_Pointers.getPositionPointer(0x0)
    prevPos = MKW_core.getPrevPos()
    pos = MKW_core.getPos()
    speed = MKW_core.getXYZSpd()

    # draw on screen
    gui.draw_text((10, 10), red, f"frame_counter: {frame_counter}")
    gui.draw_text((10, 30), red, f"game_id: {game_id}")
    gui.draw_text((10, 50), red, f"XYZ Speed: {speed}")
    gui.draw_text((10, 70), red, f"prevPosPointer: {hex(prevPosPointer)}")
    gui.draw_text((10, 90), red, f"posPointer: {hex(posPointer)}")
    gui.draw_text((10, 110), red, f"prevPos: {prevPos['X']}\t{prevPos['Y']}\t{prevPos['Z']}")
    gui.draw_text((10, 130), red, f"pos: {pos['X']}\t{pos['Y']}\t{pos['Z']}")
