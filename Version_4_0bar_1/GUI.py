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

# Global vars
PBPercentage = 0
FileLoc="No CSV File Selected"
CurrentOp="Idle"
Entries = 0
Entry = 0
Action = ""
Stop = 0
End=0

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

class ConsoleUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.parent.title("Console")
        self.config(bg="#F0F0F0")
        self.instruction = tk.Label(self.parent, text="Enter your command (python code):")
        self.instruction.pack()
        
        self.filler1 = tk.Label(self.parent, text="")
        self.filler1.pack()
        
        self.entryField = tk.Entry(self.parent)
        self.entryField.pack()
        
        self.filler2 = tk.Label(self.parent, text="")
        self.filler2.pack()
        
        self.buttonFrame = tk.Frame(self.parent)
        self.buttonFrame.pack()
        
        self.okButton = tk.Button(self.buttonFrame, text="Execute", command=self.execute)
        self.cancelButton = tk.Button(self.buttonFrame, text="Cancel", command=self.cancel)
        self.okButton.pack(side=tk.LEFT)
        self.cancelButton.pack(side=tk.LEFT)
        
    def execute(self):
        exec self.entryField.get()
        self.parent.destroy()
        
    def cancel(self):
        self.parent.destroy()
        

class GUI(tk.Frame):
    def __init__(self, parent):
        GlobalVars()
        print ""
        print "GUI thread created"
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.Init()

    def Init(self):
        value_progress = 300
        
        # self.menuFrame = ttk.Frame(self)

        self.parent.title("No-Name File Program")
        self.config(bg='#F0F0F0')
        self.pack(fill = tk.BOTH, expand = 1)
        
        menubar = tk.Menu(self)
        self.parent.config(menu=menubar)
        
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Import")
        fileMenu.add_command(label="Load")
        fileMenu.add_command(label="Save")
        fileMenu.add_command(label="Save As")
        fileMenu.add_command(label="Export As")
        menubar.add_cascade(label="File", menu=fileMenu)
        
        viewMenu = tk.Menu(menubar)
        menubar.add_cascade(label="View", menu=viewMenu)
        
        filtersMenu = tk.Menu(menubar)
        menubar.add_cascade(label="Filters", menu=filtersMenu)
        
        automationMenu = tk.Menu(menubar)
        menubar.add_cascade(label="Automation", menu=automationMenu)
        
        editMenu = tk.Menu(menubar)
        editMenu.add_command(label="Console", command=self.Console)
        menubar.add_cascade(label="Edit", menu=editMenu)

        self.SelectedCSV = ttk.Label(self, text=FileLoc)
        self.SelectedCSV.grid(row=1, column=0, sticky=tk.NW)

        self.CurrentOperation = ttk.Label(self, text=CurrentOp)
        self.CurrentOperation.grid(row=4, column=0, sticky=tk.NW)
        
        self.correctFrame = ttk.Frame(self)
        self.incorrectFrame = ttk.Frame(self)
        self.allFrame = ttk.Frame(self)
        
        self.DataScrollCorrect = tk.Scrollbar(self.correctFrame)
        self.DataScrollCorrect.grid(column=50, row=5, sticky=tk.W)
        self.DataCanvasCorrect = tk.Canvas(self.correctFrame, yscrollcommand=self.DataScrollCorrect.set, relief=tk.FLAT, background = "#D2D2D2", width=620, height=430)
        self.DataCanvasCorrect.grid(column=0, row=5, sticky=tk.W, columnspan=50)
        self.DataScrollCorrect.config(command=self.DataCanvasCorrect.yview)

        self.DataScrollWrong = tk.Scrollbar(self.incorrectFrame)
        self.DataScrollWrong.grid(column=50, row=5, sticky=tk.W)
        self.DataCanvasWrong = tk.Canvas(self.incorrectFrame, yscrollcommand=self.DataScrollWrong.set, relief=tk.FLAT, background = "#D2D2D2", width=620, height=430)
        self.DataCanvasWrong.grid(column=0, row=5, sticky=tk.W, columnspan=50)
        self.DataScrollWrong.config(command=self.DataCanvasWrong.yview)
        
        self.DataScrollAll = tk.Scrollbar(self.allFrame)
        self.DataCanvasAll = tk.Canvas(self.allFrame, yscrollcommand=self.DataScrollAll.set, relief=tk.FLAT, background = "#D2D2D2", width=520, height=430)
        self.DataScrollAll.grid(column=999, row=0, sticky=tk.E+tk.N, columnspan=300)
        self.sideFrame = tk.Frame(self.allFrame)
        self.FileDescriptorWindow = tk.Canvas(self.sideFrame, height=100, width=100, background="#D2D2D2")
        self.IncorrectMiniWindow = tk.Canvas(self.sideFrame, height=325, width=100, background="#D2D2D2")
        self.DataCanvasAll.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=1, pady=1)
        self.DataScrollAll.config(command=self.DataCanvasAll.yview)
        self.FileDescriptorWindow.grid(column=0, row=0, sticky=tk.NW, padx=1, pady=1)
        self.IncorrectMiniWindow.grid(column=0, row=1, sticky=tk.NW, padx=1, pady=1)
        self.sideFrame.grid(column=0, row=0, sticky=tk.NW)
        
        self.allFrame.grid(row=2, column=0)
        
        # test entries. These are demonstrations only, which will work until I make something less shit.
        self.firstEntry = tk.Canvas(self.DataCanvasAll, height=100, width=500, background="#FFFFFF")
        self.firstEntry.grid(row=0, padx=10, pady=5)
        self.secondEntry = tk.Canvas(self.DataCanvasAll, height=100, width=500, background="#FFFFFF")
        self.secondEntry.grid(row=1, padx=10, pady=5)
        

        canvas = tk.Canvas(self, relief=tk.FLAT, background = "#D2D2D2", width=640, height=5)
        canvas.grid(column=0,row=999,sticky=tk.NW,columnspan=200)


        # WATCH OUT FOR PLACEMENT HERE
        self.rowconfigure('all', minsize = 1)
        self.columnconfigure('all', minsize = 1)

        self.ProgressBar = ttk.Progressbar(canvas, orient=tk.HORIZONTAL,
                                  length=640, mode="determinate")
        
        # The first 2 create window argvs control where the progress bar is placed
        canvas.create_window(1, 1, anchor=tk.W, window=self.ProgressBar)
        canvas.grid(column=0,row=999,sticky=tk.SW,columnspan=100)

        self.PBStart()
       

    def PBStart(self):
        self.ProgressBar["value"] = 0
        self.PBMax = 10000
        self.ProgressBar["maximum"] = self.PBMax
        global PBPercentage
        PBPercentage = 0
        self.PBChange()
        

    def PBChange(self):
        '''simulate reading 500 bytes; update progress bar'''
        global PBPercentage
        self.CurrentOperation["text"]=CurrentOp
        
        if Action == "Processing":
            self.ProgressBar["maximum"]=Entries
            self.ProgressBar["value"]=Entry
        if PBPercentage > self.PBMax or PBPercentage == self.PBMax:
            global PBPercentage
            PBPercentage = 0
            self.after(100, self.PBChange)
        else:
            self.after(100, self.PBChange)
            
    def loadEntries(self):    
        # Load tabs here
        with open(FileLoc, 'rb') as f:
            BirdFile = list(csv.reader(f))

    def FindFile(self):
        global CurrentOp
        CurrentOp="Selecting CSV File..."
        global FileLoc
        FileLoc = tkFileDialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if FileLoc!="":
            global FileLoc 
            FileLoc = escape(FileLoc)
            self.loadEntries()
        else:
            global FileLoc
            FileLoc = "No CSV File Selected"
        self.SelectedCSV["text"]=FileLoc
        print "Selected file "+FileLoc
        CurrentOp="Idle"

    def FileDeselect(self):
        global CurrentOp
        CurrentOp="Deselecting CSV File..."
        global FileLoc
        FileLoc="No CSV File Selected"
        self.SelectedCSV["text"]=FileLoc
        print "File Deselected"
        CurrentOp="Idle"

    def PreImages(self):
        if FileLoc!="No CSV File Selected":
            global Stop
            Stop = 0
            self.StopDLoad["text"]="Pause Download"
            global CurrentOp
            CurrentOp="Preparing to process..."
            self.PrepareImages["state"]=tk.DISABLED
            self.SelectCSV["state"]=tk.DISABLED
            self.DeselectCSV["state"]=tk.DISABLED
            self.StopDLoad["state"]=tk.ACTIVE
            self.ExitDload["state"]=tk.ACTIVE
            global End
            End = -1
            
        
            thread.start_new_thread(ImageEngine.Engine,())

    def StopDL(self):
        if Stop==0:
            global Stop
            Stop = 1
            self.StopDLoad["text"]="Resume Download"
        else:
            global Stop
            Stop = 0
            self.StopDLoad["text"]="Pause Download"

    def ExitDL(self):
        if End==-1:
            global End
            End=1
            global CurrentOp
            CurrentOp="Stopping..."
            while End!=2:
                time.sleep(1)
            
            #other shit here
            global Entry
            Entry = 0
            
            self.StopDLoad["state"]=tk.DISABLED
            self.ExitDload["state"]=tk.DISABLED
            self.PrepareImages["state"]=tk.ACTIVE
            self.SelectCSV["state"]=tk.ACTIVE
            self.DeselectCSV["state"]=tk.ACTIVE
            CurrentOp="Idle"
            
    def showAllEntries(self):
        self.correctFrame.grid_forget()
        self.incorrectFrame.grid_forget()
        self.allFrame.grid(row=2, column=0)
        
    def showCorrectEntries(self):
        self.allFrame.grid_forget()
        self.incorrectFrame.grid_forget()
        self.correctFrame.grid(row=2, column=0)
        
    def showInorrectEntries(self):
        self.allFrame.grid_forget()
        self.correctFrame.grid_forget()
        self.incorrectFrame.grid(row=2, column=0)
            

    def Console(self):
        consoleUItk = tk.Tk()
        consoleUItk.geometry('250x150')
        consoleUI = ConsoleUI(consoleUItk)
        thread.start_new_thread(consoleUI.mainloop, ())
        
        
    def displayEntry(self, frame):
        self.test = tk.Canvas(frame, width=300)
        self.test2 = tk.Label(self.test, text="Hello, world")
        self.test.pack()
        self.test2.pack()
