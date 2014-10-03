#!/usr/bin/env python2

import urllib
import csv
import os
from sys import platform as SYS_PLATFORM
import shutil
import ttk
import Tkinter as tk
import thread
import time
import tkFileDialog

# The code we actually wrote...
import ImageEngine
import GUI

def escape(x):
    res = ""
    for i in x:
        if i == "\\": # If it equals a single backslash.
            res += "\\\\" # Add two backslashes
        else:
            res += i # Add whatever the character was
    return res

if "windows" in SYS_PLATFORM.lower():
    file_delimeter = "\\"
else:
    file_delimeter = "/"

def GlobalVars():
    global PBPercentage
    PBPercentage = 0
    global FileLoc
    FileLoc="No CSV File Selected"
    global CurrentOp
    CurrentOp="Idle"
    global Entries
    Entries = 0
    global Entry
    Entry = 0
    global Action
    Action = ""
    global Stop
    Stop = 0
    global End
    End=0
        

tkin=tk.Tk()
tkin.geometry('640x480')
gui = GUI.GUI(tkin)
gui.mainloop()
