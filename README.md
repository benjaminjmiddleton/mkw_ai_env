This repository contains scripts used to interface between Mario Kart Wii and a reinforcement learning agent in real-time (the Scripts folder),
as well as an example agent (the Rainbow-master folder, which was adapted from this repo https://github.com/Kaixhin/Rainbow).
It needs to be used with Felk's Dolphin with Python Scripting Support (https://github.com/Felk/dolphin)
and with Python version 3.8 (as per Felk's repository).

A few functions have been reimplemented from the Dolphin-Lua-Core (https://github.com/SwareJonge/Dolphin-Lua-Core) to work with the Python repo. The files Scripts/MKW_Pointers.py and Scripts/MKW_core.py contain these functions and a few others, and may be useful for translating the rest of the scripts that come with Dolphin-Lua-Core for MKW.

# Notes for Setting This Up

Because these scripts are run in the dolphin executable, you need to append the true path of the scripts you want to import using sys.path.append().

In:
- agent_script.py
- frame_count.py
- MKW_core.py

the line "sys.path.append("C:\\\\code\\\\dolphin_env\\\\Scripts")" will need to be updated to whatever path you are using.

For similar reasons, the path to your venv or python installation will also need to be appended in any script you include a package in.
- In agent_script.py, the line "sys.path.append("C:\\\\code\\\\dolphin_env\\\\venv\\\\Lib\\\\site-packages")" will need to be updated to your personal venv or python installation path.

Then, agent_script.py will be able to be run from the executable for Dolphin with Python Scripting Support (https://github.com/Felk/dolphin)

Before running agent_script.py, you should first start running the Rainbow agent in a terminal. It will wait for the connection from dolphin to begin.