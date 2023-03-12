from dolphin import memory

def GetGameID():
    # 6-byte string at address 0x80000000
    id = hex(memory.read_u64(0x80000000))[2:14]
    id = bytes.fromhex(id).decode('utf-8')
    return id

def getPointer(pointer, offsets):
    for offset in offsets:
        pointer = memory.read_u32(pointer) + offset
        if pointer == 0 or pointer == offset:
            pointer = 0
            break
    return pointer

def getPrevPositionPointer(Offset):
    pointer = 0x80000000
    if GetGameID() == "RMCP01":
        pointer += 0x9C18F8
    elif GetGameID() == "RMCE01":
        pointer += 0x9BD110
    elif GetGameID() == "RMCJ01":
        pointer += 0x9C0958
    elif GetGameID() == "RMCK01":
        pointer += 0x9AFF38

    return getPointer(pointer, [0xC, 0x10, Offset, 0x0, 0x8, 0x90, 0x0])

def getPositionPointer(Offset):
    pointer = 0x80000000
    if GetGameID() == "RMCP01":
        pointer += 0x9C18F8
    elif GetGameID() == "RMCE01":
        pointer += 0x9BD110
    elif GetGameID() == "RMCJ01":
        pointer += 0x9C0958
    elif GetGameID() == "RMCK01":
        pointer += 0x9AFF38

    return getPointer(pointer, [0xC, 0x10, Offset, 0x0, 0x8, 0x90, 0x4, 0x0])