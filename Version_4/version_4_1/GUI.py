import urllib
import csv
import os
from sys import platform as SYS_PLATFORM
import ttk
import Tkinter as tk
import thread
import time
import tkFileDialog
import tkMessageBox
import json

# The code we actually wrote...
import functionBase
from DisplayedEntry import DisplayedEntry
from ConsoleUI import ConsoleUI
from AskSave import AskSave

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
        

class GUI(tk.Frame):    
    def __init__(self, parent):
        print ""
        print "GUI thread created"
        self.fileDict = {}
        self.displayedEntryList = []
        self.displayedAllList = []
        self.pageNum = 0
        self.modified = False
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # This DOES NOT WORK. At all. No idea why. No errors or anything. It just ignores the line completely...
        self.parent.wm_protocol("WM_CLOSE_WINDOW", self.onClose)
        
        # Load global config settings
        try:
            fp = open("resources/global_config.json", "r")
            self.global_config = json.load(fp)
            fp.close()
        except IOError:
            fp = open("resources/global_config.json", "w")
            # Any permanent options go in this dictionary
            self.global_config = {"displayedEntries":30}
            json.dump(self.global_config, fp)
            fp.close()
        
        self.loadUI()

    def loadUI(self):
        value_progress = 300

        self.parent.title("Climatewatch Data Toolbox")
        self.config(bg='#F0F0F0')
        self.pack(fill = tk.BOTH, expand = 1)
        
        self.menubar = tk.Menu(self)
        self.parent.config(menu=self.menubar)
        
        self.fileMenu = tk.Menu(self.menubar)
        self.fileMenu.add_command(label="Import", command=self.fileI)
        self.fileMenu.add_command(label="Load", command=self.fileL)
        self.fileMenu.add_command(label="Save", command=self.fileS, state=tk.DISABLED)
        self.fileMenu.add_command(label="Save As", command=self.fileSA, state=tk.DISABLED)
        self.fileMenu.add_command(label="Export As")
        self.fileMenu.add_command(label="Close", command=self.onClose, state=tk.DISABLED)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        
        self.viewMenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="View", menu=self.viewMenu)
        
        self.filtersMenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Filters", menu=self.filtersMenu)
        
        self.automationMenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Automation", menu=self.automationMenu)
        
        self.editMenu = tk.Menu(self.menubar)
        self.editMenu.add_command(label="Console", command=self.console)
        self.editMenu.add_command(label="GUI Console", command=self.guiConsole)
        self.menubar.add_cascade(label="Edit", menu=self.editMenu)

        self.CurrentOperation = tk.Label(self, text=CurrentOp)
        self.CurrentOperation.grid(row=4, column=0, sticky=tk.NW)
        
        self.tabsFrame = tk.Frame(self)
        self.tabsFrame.grid(row=1, sticky=tk.NE)
        self.partsFrame = tk.Frame(self, height=21, width=180)
        self.partsFrame.pack_propagate(False)
        
        self.prevButton = tk.Button(self.partsFrame, text="Prev", command=self.loadPrev)
        self.nextButton = tk.Button(self.partsFrame, text="Next", command=self.loadNext)
        self.partLabel = tk.Label(self.partsFrame, text="Part ?/?")
        self.prevButton.pack(side=tk.LEFT, padx=5)
        self.partLabel.pack(side=tk.LEFT)
        self.nextButton.pack(side=tk.LEFT, padx=5)
        
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
        canvas.grid(column=0, row=999, sticky=tk.NW, columnspan=200)


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
        
    def pageNumUpdate(self):
        self.prevButton.config(state=tk.NORMAL)
        self.nextButton.config(state=tk.NORMAL)
        if self.pageNum < 2:
            self.prevButton.config(state=tk.DISABLED)
        elif self.pageNum >= int(self.fileDict["details"]["totEntries"]/float(self.global_config["displayedEntries"])+1):
            self.nextButton.config(state=tk.DISABLED)
        self.partLabel.config(text = "Part "+str(self.pageNum)+"/"+str(int(self.fileDict["details"]["totEntries"]/float(self.global_config["displayedEntries"]))+1))

    def fileI(self):
        self.fileDict = functionBase.readFile('import')
        self.fileMenu.entryconfig("Save", state=tk.NORMAL)
        self.fileMenu.entryconfig("Save As", state=tk.NORMAL)
        self.fileMenu.entryconfig("Load", state=tk.DISABLED)
        self.fileMenu.entryconfig("Import", state=tk.DISABLED)
        self.fileMenu.entryconfig("Close", state=tk.NORMAL)
        self.pageNum = 0
        self.loadNext()
        self.partsFrame.grid(row=1, sticky=tk.W)
        
    def fileL(self):
        self.fileDict = functionBase.readFile('load')
        self.fileMenu.entryconfig("Save", state=tk.NORMAL)
        self.fileMenu.entryconfig("Save As", state=tk.NORMAL)
        self.fileMenu.entryconfig("Load", state=tk.DISABLED)
        self.fileMenu.entryconfig("Import", state=tk.DISABLED)
        self.fileMenu.entryconfig("Close", state=tk.NORMAL)
        self.pageNum = 0
        self.loadNext()
        self.partsFrame.grid(row=1, sticky=tk.W)
        

    def fileSA(self):
        self.fileDict['details']['saveLocation']=functionBase.writeFile('saveAs', self.fileDict)
        functionBase.writeFile('save', self.fileDict)
        self.modified = False

    def fileS(self):
        functionBase.writeFile('save', self.fileDict)
        self.modified = False

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
        
    def addEntry(self, uid):
        try:
            if self.fileDict["entries"][str(uid)]["__isCorrect__"] == "yes":
                isCorrect = True
            else:
                isCorrect = False
        except KeyError:
            print "Loaded entry "+str(uid)
            self.fileDict["entries"][str(uid)]["__isCorrect__"] = "yes"
            isCorrect = True
            
        if isCorrect:
            self.displayedEntryList.append(DisplayedEntry(self.DataCanvasCorrect, self.entryFrameCorrect, self.dataFrameCorrect, len(self.displayedEntryList), "#81F781", uid))
            self.displayedAllList.append(DisplayedEntry(self.DataCanvasAll, self.entryFrameAll, self.dataFrameAll, len(self.displayedAllList), "#81F781", uid))
            
        else:
            self.displayedEntryList.append(DisplayedEntry(self.DataCanvasIncorrect, self.entryFrameIncorrect, self.dataFrameIncorrect, len(self.displayedEntryList), "#F5A9A9", uid))
            self.displayedAllList.append(DisplayedEntry(self.DataCanvasAll, self.entryFrameAll, self.dataFrameAll, len(self.displayedAllList), "#F5A9A9", uid))
    
    def deleteEntry(self, uid):
        indexEntry = -1
        for i in range(len(self.displayedEntryList)):
            if self.displayedEntryList[i].uid == uid:
                indexEntry = i
                print "indexEntry == "+str(indexEntry)
                
        if indexEntry == -1:
            return
            
        indexAll = -1
        for i in range(len(self.displayedAllList)):
            if self.displayedAllList[i].uid == uid:
                indexAll = i
                print "indexAll == "+str(indexAll)
                
        if indexAll == -1:
            return
            
        self.displayedEntryList[indexEntry].destroy()
        self.displayedAllList[indexAll].destroy()
        
    def move(self, uid):
        indexEntry = -1
        for i in range(len(self.displayedEntryList)):
            if self.displayedEntryList[i].uid == uid:
                indexEntry = i
                
        if indexEntry == -1:
            return
            
        indexAll = -1
        for i in range(len(self.displayedAllList)):
            if self.displayedAllList[i].uid == uid:
                indexAll = i
                
        if indexAll == -1:
            return
            
        self.modified = True
            
        if self.fileDict["entries"][str(uid)]["__isCorrect__"] == "yes":
            self.fileDict["entries"][str(uid)]["__isCorrect__"] = "no"
        elif self.fileDict["entries"][str(uid)]["__isCorrect__"] == "no":
            self.fileDict["entries"][str(uid)]["__isCorrect__"] = "yes"
            
        if self.displayedEntryList[indexEntry].rootFrame == self.entryFrameCorrect:
            self.displayedEntryList.append(DisplayedEntry(self.DataCanvasIncorrect, self.entryFrameIncorrect, self.dataFrameIncorrect, len(self.displayedEntryList), "#F5A9A9", self.displayedEntryList[indexEntry].uid))
            self.displayedAllList[indexAll].entryCanvas.itemconfigure(self.displayedAllList[indexAll].flagRect, fill="#F5A9A9")
            self.displayedEntryList[indexEntry].destroy()
            
        elif self.displayedEntryList[indexEntry].rootFrame == self.entryFrameIncorrect:
            self.displayedEntryList.append(DisplayedEntry(self.DataCanvasCorrect, self.entryFrameCorrect, self.dataFrameCorrect, len(self.displayedEntryList), "#81F781", self.displayedEntryList[indexEntry].uid))
            self.displayedAllList[indexAll].entryCanvas.itemconfigure(self.displayedAllList[indexAll].flagRect, fill="#81F781")
            self.displayedEntryList[indexEntry].destroy()
            
    def loadNext(self):
        self.pageNum += 1
        for i in self.displayedAllList:
            i.destroy()
        for i in self.displayedEntryList:
            i.destroy()
        for i in range( (self.pageNum-1)*self.global_config["displayedEntries"], self.pageNum*self.global_config["displayedEntries"] ):
            try:
                self.addEntry(i)
            except KeyError:
                break
        self.pageNumUpdate()
        
    def loadPrev(self):
        self.pageNum -= 1
        for i in self.displayedAllList:
            i.destroy()
        for i in self.displayedEntryList:
            i.destroy()
        for i in range( (self.pageNum-1)*self.global_config["displayedEntries"], self.pageNum*self.global_config["displayedEntries"] ):
            try:
                self.addEntry(i)
            except KeyError:
                break
        self.pageNumUpdate()
    
    def onClose(self):
        if self.modified:
            AskSave(self)
        else:
            for i in self.displayedAllList:
                i.destroy()
            for i in self.displayedEntryList:
                i.destroy()
            self.fileDict = {}
            self.modified = False
            self.fileMenu.entryconfig("Save", state=tk.DISABLED)
            self.fileMenu.entryconfig("Save As", state=tk.DISABLED)
            self.fileMenu.entryconfig("Load", state=tk.NORMAL)
            self.fileMenu.entryconfig("Import", state=tk.NORMAL)
            self.fileMenu.entryconfig("Close", state=tk.DISABLED)
            self.partsFrame.grid_forget()
