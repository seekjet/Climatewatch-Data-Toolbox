import urllib
import csv
import os
from sys import platform as SYS_PLATFORM
import ttk
import Tkinter as tk
import thread
import time
import tkFileDialog

# The code we actually wrote...
import functionBase
from DisplayedEntry import DisplayedEntry
from ConsoleUI import ConsoleUI

# Global vars
PBPercentage = 0
FileLoc="No CSV File Selected"
CurrentOp="Idle"
Entries = 0
Entry = 0
Action = ""
Stop = 0
End=0
displayedEntryList = []
displayedAllList = []
fileDict = {}

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
        

class GUI(tk.Frame):    
    def __init__(self, parent):
        print ""
        print "GUI thread created"
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.Init()

    def Init(self):
        value_progress = 300

        self.parent.title("Climatewatch Data Toolbox")
        self.config(bg='#F0F0F0')
        self.pack(fill = tk.BOTH, expand = 1)
        
        menubar = tk.Menu(self)
        self.parent.config(menu=menubar)
        
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Import",command=self.fileI)
        fileMenu.add_command(label="Load",command=self.fileL)
        fileMenu.add_command(label="Save",command=self.fileS)
        fileMenu.add_command(label="Save As",command=self.fileSA)
        fileMenu.add_command(label="Export As")
        menubar.add_cascade(label="File", menu=fileMenu)
        
        viewMenu = tk.Menu(menubar)
        menubar.add_cascade(label="View", menu=viewMenu)
        
        filtersMenu = tk.Menu(menubar)
        menubar.add_cascade(label="Filters", menu=filtersMenu)
        
        automationMenu = tk.Menu(menubar)
        menubar.add_cascade(label="Automation", menu=automationMenu)
        
        editMenu = tk.Menu(menubar)
        editMenu.add_command(label="Console", command=self.console)
        editMenu.add_command(label="GUI Console", command=self.guiConsole)
        menubar.add_cascade(label="Edit", menu=editMenu)

        self.CurrentOperation = tk.Label(self, text=CurrentOp)
        self.CurrentOperation.grid(row=4, column=0, sticky=tk.NW)
        
        self.tabsFrame = tk.Frame(self)
        self.tabsFrame.grid(row=1, sticky=tk.NE)
        
        # Not quite useless. It controls the state of the radiobuttons. However, since we change displays using callbacks, this is its only use.
        self.useless = tk.StringVar()
        self.useless.set("all")
        
        self.displayAllButton = tk.Radiobutton(self.tabsFrame, text="All Entries", variable=self.useless, value="all", command=self.showAllEntries)
        self.displayCorrectButton = tk.Radiobutton(self.tabsFrame, text="Correct Entries", variable=self.useless, value="correct", command=self.showCorrectEntries)
        self.displayIncorrectButton = tk.Radiobutton(self.tabsFrame, text="Incorrect Entries", variable=self.useless, value="incorrect", command=self.showIncorrectEntries)
        self.displayAllButton.pack(side=tk.LEFT)
        self.displayCorrectButton.pack(side=tk.LEFT)
        self.displayIncorrectButton.pack(side=tk.LEFT)
        
        self.correctFrame = tk.Frame(self)
        self.incorrectFrame = tk.Frame(self)
        self.allFrame = tk.Frame(self)
        
        # AllFrame
        self.entryFrameAll = tk.Frame(self.allFrame, width=520, height=430, bd=1)
        self.entryFrameAll.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasAll=tk.Canvas(self.entryFrameAll, background="#D2D2D2", highlightthickness=0,)
        self.dataFrameAll=tk.Frame(self.DataCanvasAll, background="#D2D2D2", borderwidth=1)
        self.scrollBarAll=tk.Scrollbar(self.entryFrameAll,orient = tk.VERTICAL,command=self.DataCanvasAll.yview)
        self.DataCanvasAll.configure(yscrollcommand=self.scrollBarAll.set)

        self.scrollBarAll.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasAll.pack(side=tk.LEFT)
        self.DataCanvasAll.create_window(0, 0, window=self.dataFrameAll,anchor=tk.NW)
        self.DataCanvasAll.configure(scrollregion=self.DataCanvasAll.bbox(tk.ALL),width=510,height=430)
        
        self.dataFrameAll.bind("<Configure>", self.configScrollRegion)
        
        #CorrectFrame
        self.entryFrameCorrect = tk.Frame(self.correctFrame, width=612, height=430, bd=1)
        self.entryFrameCorrect.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasCorrect=tk.Canvas(self.entryFrameCorrect, background="#D2D2D2", highlightthickness=0, width=612, height=430)
        self.dataFrameCorrect=tk.Frame(self.DataCanvasCorrect, background="#D2D2D2", borderwidth=1)
        self.scrollBarCorrect=tk.Scrollbar(self.entryFrameCorrect,orient = tk.VERTICAL,command=self.DataCanvasCorrect.yview)
        self.DataCanvasCorrect.configure(yscrollcommand=self.scrollBarCorrect.set)

        self.scrollBarCorrect.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasCorrect.pack(side=tk.LEFT)
        self.DataCanvasCorrect.create_window(0, 0, window=self.dataFrameCorrect,anchor=tk.NW)
        self.DataCanvasCorrect.configure(scrollregion=self.DataCanvasCorrect.bbox(tk.ALL),width=612,height=430)
        
        self.dataFrameCorrect.bind("<Configure>", self.configScrollRegion)
        
        # IncorrectFrame
        self.entryFrameIncorrect = tk.Frame(self.incorrectFrame, width=612, height=430,bd=1)
        self.entryFrameIncorrect.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasIncorrect=tk.Canvas(self.entryFrameIncorrect, background="#D2D2D2", highlightthickness=0, height=612, width=430)
        self.dataFrameIncorrect=tk.Frame(self.DataCanvasIncorrect, background="#D2D2D2", borderwidth=1)
        self.scrollBarIncorrect=tk.Scrollbar(self.entryFrameIncorrect,orient = tk.VERTICAL,command=self.DataCanvasIncorrect.yview)
        self.DataCanvasIncorrect.configure(yscrollcommand=self.scrollBarIncorrect.set)

        self.scrollBarIncorrect.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasIncorrect.pack(side=tk.LEFT)
        self.DataCanvasIncorrect.create_window(0, 0, window=self.dataFrameIncorrect,anchor=tk.NW)
        self.DataCanvasIncorrect.configure(scrollregion=self.DataCanvasIncorrect.bbox(tk.ALL),width=612,height=430)
        
        self.dataFrameIncorrect.bind("<Configure>", self.configScrollRegion)
        
        
        self.sideFrame = tk.Frame(self.allFrame, background = "#D2D2D2")
        self.FileDescriptorWindow = tk.Canvas(self.sideFrame, height=100, width=98,highlightthickness=0)
        self.IncorrectMiniWindow = tk.Canvas(self.sideFrame, height=324, width=98,highlightthickness=0)
        self.FileDescriptorWindow.grid(column=0, row=0, sticky=tk.NW, padx=2, pady=2)
        self.IncorrectMiniWindow.grid(column=0, row=1, sticky=tk.NW, padx=2, pady=0)
        self.sideFrame.grid(column=0, row=0, sticky=tk.NW,pady=1)
        
        self.allFrame.grid(row=2, column=0)

        canvas = tk.Canvas(self, relief=tk.FLAT, background = "#D2D2D2", width=640, height=5, highlightthickness=0)
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
        
    def configScrollRegion(self, event):
        self.DataCanvasAll.configure(scrollregion=self.DataCanvasAll.bbox(tk.ALL),width=510,height=430)
        self.DataCanvasCorrect.configure(scrollregion=self.DataCanvasCorrect.bbox(tk.ALL),width=612,height=430)
        self.DataCanvasIncorrect.configure(scrollregion=self.DataCanvasIncorrect.bbox(tk.ALL),width=612,height=430)

    def fileI(self):
        global fileDict
        fileDict = functionBase.readFile('import')
        #print fileDict['details']['totEntries']
        
    def fileL(self):
        global fileDict
        fileDict = functionBase.readFile('load')
        #print fileDict['details']['totEntries']

    def fileSA(self):
        fileDict['details']['saveLocation']=functionBase.writeFile('saveAs',fileDict)

    def fileS(self):
        functionBase.writeFile('save',fileDict)
        
       

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
        if PBPercentage >= self.PBMax:
            global PBPercentage
            PBPercentage = 0
            self.after(100, self.PBChange)
        else:
            self.after(100, self.PBChange)
            
    def loadEntries(self):    
        # Load tabs here
        with open(FileLoc, 'rb') as f:
            BirdFile = list(csv.reader(f))

    def FindFile(self,flag):
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
        
    def showIncorrectEntries(self):
        self.allFrame.grid_forget()
        self.correctFrame.grid_forget()
        self.incorrectFrame.grid(row=2, column=0)
        
    def execute(self, command):
        # executes a command within the scope of a GUI object
        exec command

    def console(self):
        self.execute( raw_input("Enter your command:\n>>>") )
        
    def guiConsole(self):
        consoleUItk = tk.Toplevel()
        consoleUItk.geometry('250x150')
        consoleUI = ConsoleUI(consoleUItk, self)
        consoleUI.mainloop()
        
    def addEntry(self):
        displayedEntryList.append(DisplayedEntry(self.DataCanvasCorrect, self.entryFrameCorrect, self.dataFrameCorrect, len(displayedEntryList), "#81F781", len(displayedEntryList)))
        displayedAllList.append(DisplayedEntry(self.DataCanvasAll, self.entryFrameAll, self.dataFrameAll, len(displayedAllList), "#81F781", len(displayedAllList)))
    
    def deleteEntry(self, uid):
        indexEntry = -1
        for i in range(len(displayedEntryList)):
            if displayedEntryList[i].uid == uid:
                indexEntry = i
                print "indexEntry == "+str(indexEntry)
                
        if indexEntry == -1:
            return
            
        indexAll = -1
        for i in range(len(displayedAllList)):
            if displayedAllList[i].uid == uid:
                indexAll = i
                print "indexAll == "+str(indexAll)
                
        if indexAll == -1:
            return
            
        displayedEntryList[indexEntry].destroy()
        displayedAllList[indexAll].destroy()
        
    def move(self, uid):
        indexEntry = -1
        for i in range(len(displayedEntryList)):
            if displayedEntryList[i].uid == uid:
                indexEntry = i
                
        if indexEntry == -1:
            return
            
        indexAll = -1
        for i in range(len(displayedAllList)):
            if displayedAllList[i].uid == uid:
                indexAll = i
                
        if indexAll == -1:
            return
            
        if displayedEntryList[indexEntry].rootFrame == self.entryFrameCorrect:
            displayedEntryList.append(DisplayedEntry(self.DataCanvasIncorrect, self.entryFrameIncorrect, self.dataFrameIncorrect, len(displayedEntryList), "#F5A9A9", displayedEntryList[indexEntry].uid))
            displayedAllList[indexAll].entryCanvas.itemconfigure(displayedAllList[indexAll].flagRect, fill="#F5A9A9")
            displayedEntryList[indexEntry].destroy()
            
        elif displayedEntryList[indexEntry].rootFrame == self.entryFrameIncorrect:
            displayedEntryList.append(DisplayedEntry(self.DataCanvasCorrect, self.entryFrameCorrect, self.dataFrameCorrect, len(displayedEntryList), "#81F781", displayedEntryList[indexEntry].uid))
            displayedAllList[indexAll].entryCanvas.itemconfigure(displayedAllList[indexAll].flagRect, fill="#81F781")
            displayedEntryList[indexEntry].destroy()
