import sys
import math

from dolphin import memory

sys.path.append("C:\\code\\dolphin_env\\Scripts") # path to the folder this file is in
import MKW_Pointers as Pointers

def getRaceCompletion():
    return memory.read_u16(Pointers.getRaceCompletionPointer(0x0))

def getPos():
    address = Pointers.getPositionPointer(0x0) # 0x0 first player in the array, to get the most accurate, read playerindex first
    if address == 0:
        return {'X': 0, 'Y': 0, 'Z': 0}
    return {'X': memory.read_f32(address+0x68), 'Y': memory.read_f32(address+0x6C), 'Z': memory.read_f32(address+0x70)}

def getPrevPos():
    address = Pointers.getPrevPositionPointer(0x0)
    if address == 0:
        return {'X': 0, 'Y': 0, 'Z': 0}
    return {'X': memory.read_f32(address+0x18), 'Y': memory.read_f32(address+0x1C), 'Z': memory.read_f32(address+0x20)}

def getSpd():
    prevPos = getPrevPos()
    pos = getPos()
    xdiff = pos['X'] - prevPos['X']
    ydiff = pos['Y'] - prevPos['Y']
    zdiff = pos['Z'] - prevPos['Z']
    return {'X': xdiff, 'Y': ydiff, 'Z': zdiff, 'XZ': math.sqrt(xdiff**2 + zdiff**2), 'XYZ': math.sqrt(xdiff**2 + ydiff**2 + zdiff**2)}

def getXYZSpd(): # avoid additional calculations from running getSpd() when we only want XYZ speed in particular
    prevPos = getPrevPos()
    pos = getPos()
    return math.sqrt(((pos['X'] - prevPos['X'])**2) + ((pos['Y'] - prevPos['Y'])**2) + (pos['Z'] - prevPos['Z'])**2)
