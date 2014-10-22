import urllib
import csv
import os
from sys import platform as SYS_PLATFORM
import ttk
import Tkinter as tk
import thread
import time
import tkFileDialog
from PIL import Image, ImageTk

import functionBase

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
    global fileDict
    fileDict={}

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
        
class ExpandImage(tk.Frame):
    def __init__(self, parent, picturePath):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.parent.title("Climatewatch Data Toolbox - "+self.stripFileName(picturePath))
        
        self.picturePath = picturePath
        self.original = Image.open(self.picturePath)
        self.aspectRatio = float(self.original.size[0])/float(self.original.size[1])
        photo = ImageTk.PhotoImage(self.original)
        self.image = tk.Label(self, image=photo, bg="#000000")
        self.image.photo = photo
        self.image.pack(fill = tk.BOTH, expand = True)
        self.pack(fill = tk.BOTH, expand = True)
        
        self.image.bind("<Configure>", self.updateDimens)
        
    def updateDimens(self, event):
        self.parent.geometry(str(event.width)+"x"+str(event.height))
        if self.aspectRatio < float(event.width)/float(event.height):
            photo = ImageTk.PhotoImage(self.original.resize((int(event.height*self.aspectRatio), event.height)))
        else:
            photo = ImageTk.PhotoImage(self.original.resize((event.width, int(event.width/self.aspectRatio))))
        self.image.config(image=photo)
        self.image.photo = photo
        
    def stripFileName(self, fileName):
        temp = ""
        for i in reversed(fileName):
            if i == file_delimeter:
                break
            else:
                temp = i + temp
        return temp
        
    def __del__(self):
        self.image.destroy()
        
        
class DisplayedEntry:
    def __init__(self, rootCanvas, rootFrame, innerFrame, row, flagcolor, uid):
        self.rootCanvas = rootCanvas
        self.row = row
        self.rootFrame = rootFrame
        self.innerFrame = innerFrame
        self.uid = uid
        self.entryCanvas = tk.Canvas(self.innerFrame, height=64, width=502)
        self.entryCanvas.grid(row=self.row*2, pady=1, padx=1, sticky=tk.NW)
        self.rootCanvas.configure(scrollregion=self.rootCanvas.bbox(tk.ALL),width=510,height=430)
        self.picturePath = "resources/default.png"
        
        self.drawItems(flagcolor)
        
    def drawItems(self, flagcolor):
        self.flagRect = self.entryCanvas.create_rectangle(1,1,16,64, fill=flagcolor, outline="#D9D9D9")
        photo = Image.open(self.picturePath)
        aspectRatio = float(photo.size[0])/float(photo.size[1])
        if aspectRatio < 96.0/64.0:
            photo = photo.resize((int(aspectRatio*64), 64), Image.ANTIALIAS)
        else:
            photo = photo.resize((96, int(96/aspectRatio)), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(photo)
        self.picture = tk.Label(self.entryCanvas, image=photo, width=96, height=64, bg="#000000")
        self.picture.bind("<Button-1>", self.expandImage)
        self.picture.photo = photo
        self.entryCanvas.create_window(20, 0, window=self.picture, anchor=tk.NW)
        self.displayedData = tk.Listbox(self.entryCanvas)
        self.entryCanvas.create_window(120, 0, window=self.displayedData, anchor=tk.NW)
        
    def loadData(self, data, keyList):
        self.displayedData.delete(0, tk.END)
        for i in keyList:
            self.displayedData.insert(tk.END, data[i])
        
    def expandImage(self, event):
        imageRoot = tk.Toplevel()
        imageFrame = ExpandImage(imageRoot, self.picturePath)
        imageRoot.mainloop()
    
    def destroy(self):
        #self.entryCanvas.delete(tk.ALL)
        self.entryCanvas.destroy()
        del self
        

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
        menubar.add_cascade(label="Edit", menu=editMenu)

        self.CurrentOperation = ttk.Label(self, text=CurrentOp)
        self.CurrentOperation.grid(row=4, column=0, sticky=tk.NW)
        
        self.tabsFrame = tk.Frame(self)
        self.tabsFrame.grid(row=1, padx=50)
        
        #self.SelectedCSV = ttk.Label(self.tabsFrame, text=FileLoc)
        #self.SelectedCSV.grid(row=0, column=1)
        
        self.displayAllButton = tk.Button(self.tabsFrame, text="All Entries", command=self.showAllEntries)
        self.displayCorrectButton = tk.Button(self.tabsFrame, text="Correct Entries", command=self.showCorrectEntries)
        self.displayIncorrectButton = tk.Button(self.tabsFrame, text="Incorrect Entries", command=self.showIncorrectEntries)
        self.displayAllButton.pack(side=tk.LEFT)
        self.displayCorrectButton.pack(side=tk.LEFT)
        self.displayIncorrectButton.pack(side=tk.LEFT)
        
        self.correctFrame = tk.Frame(self)
        self.incorrectFrame = tk.Frame(self)
        self.allFrame = tk.Frame(self)
        
        # AllFrame
        self.entryFrameAll = tk.Frame(self.allFrame, width=520, height=430,bd=1)
        self.entryFrameAll.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasAll=tk.Canvas(self.entryFrameAll, background="#D2D2D2", highlightthickness=0)
        self.dataFrameAll=tk.Frame(self.DataCanvasAll, background="#D2D2D2", borderwidth=1)
        self.scrollBarAll=tk.Scrollbar(self.entryFrameAll,orient = tk.VERTICAL,command=self.DataCanvasAll.yview)
        self.DataCanvasAll.configure(yscrollcommand=self.scrollBarAll.set)

        self.scrollBarAll.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasAll.pack(side=tk.LEFT)
        self.DataCanvasAll.create_window(0, 0, window=self.dataFrameAll,anchor=tk.NW)
        self.DataCanvasAll.configure(scrollregion=self.DataCanvasAll.bbox(tk.ALL),width=510,height=430)
        
        self.dataFrameAll.bind("<Configure>", self.configScrollRegion)
        
        #CorrectFrame
        self.entryFrameCorrect = tk.Frame(self.correctFrame, width=640, height=430,bd=1)
        self.entryFrameCorrect.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasCorrect=tk.Canvas(self.entryFrameCorrect, background="#D2D2D2", highlightthickness=0)
        self.dataFrameCorrect=tk.Frame(self.DataCanvasCorrect, background="#D2D2D2", borderwidth=1)
        self.scrollBarCorrect=tk.Scrollbar(self.entryFrameCorrect,orient = tk.VERTICAL,command=self.DataCanvasAll.yview)
        self.DataCanvasCorrect.configure(yscrollcommand=self.scrollBarCorrect.set)

        self.scrollBarCorrect.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasCorrect.pack(side=tk.LEFT)
        self.DataCanvasCorrect.create_window(0, 0, window=self.dataFrameCorrect,anchor=tk.NW)
        self.DataCanvasCorrect.configure(scrollregion=self.DataCanvasAll.bbox(tk.ALL),width=510,height=430)
        
        self.dataFrameCorrect.bind("<Configure>", self.configScrollRegion)
        
        # IncorrectFrame
        self.entryFrameIncorrect = tk.Frame(self.incorrectFrame, width=640, height=430,bd=1)
        self.entryFrameIncorrect.grid(column=1, row=0, sticky=tk.NW, columnspan=405, padx=4, pady=0)
        
        self.DataCanvasIncorrect=tk.Canvas(self.entryFrameIncorrect, background="#D2D2D2", highlightthickness=0)
        self.dataFrameIncorrect=tk.Frame(self.DataCanvasIncorrect, background="#D2D2D2", borderwidth=1)
        self.scrollBarIncorrect=tk.Scrollbar(self.entryFrameIncorrect,orient = tk.VERTICAL,command=self.DataCanvasAll.yview)
        self.DataCanvasIncorrect.configure(yscrollcommand=self.scrollBarIncorrect.set)

        self.scrollBarIncorrect.pack(side=tk.RIGHT,fill=tk.Y)
        self.DataCanvasIncorrect.pack(side=tk.LEFT)
        self.DataCanvasIncorrect.create_window(0, 0, window=self.dataFrameIncorrect,anchor=tk.NW)
        self.DataCanvasIncorrect.configure(scrollregion=self.DataCanvasAll.bbox(tk.ALL),width=510,height=430)
        
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
        self.correctFrame.grid(row=2, column=0, padx=50)
        
    def showIncorrectEntries(self):
        self.allFrame.grid_forget()
        self.correctFrame.grid_forget()
        self.incorrectFrame.grid(row=2, column=0, padx=50)

    def console(self):
        exec raw_input("Enter your command:\n>>>")
        """
        consoleUItk = tk.Toplevel()
        consoleUItk.geometry('250x150')
        consoleUI = ConsoleUI(consoleUItk)
        thread.start_new_thread(consoleUI.mainloop, ())
        """       
        
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
            
        else:
            print "We dun fukked up"
