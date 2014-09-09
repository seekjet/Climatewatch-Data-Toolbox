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



def Engine():
    

    print "Engine thread created"

    
    OrigFileName=FileLoc.split(file_delimeter)[-1]
    OrigFileName=OrigFileName.split(".")[0]
    with open(FileLoc, 'rb') as f:
        BirdFile = list(csv.reader(f))
    

    FileDir = os.path.dirname(os.path.realpath(__file__))
    print "Program running from "+FileDir
    
    if os.path.isdir(FileDir+file_delimeter+OrigFileName)!=True:
        os.mkdir(FileDir+file_delimeter+OrigFileName)
        print ""
        print "Created Directory "+FileDir+file_delimeter+OrigFileName+"."
        print ""
    else:
        print ""
        print "Directory "+FileDir+file_delimeter+OrigFileName+" already exists, and will be used for this session."
        print ""

    global Entries
    Entries = len(BirdFile)-1
    print str(Entries)+" Entries Found"
    
    global Action
    Action = "Processing"

    MoveToDir=FileDir+file_delimeter+OrigFileName

    #finding headers
    ColCheck = 0
    MediaColFound = 0
    while MediaColFound == 0:
        if BirdFile[0][ColCheck]=="associatedMedia":
            MedColNum=ColCheck
            print "associatedMedia Column found as column number " + str(MedColNum)
            MediaColFound = 1
        else:
            ColCheck=ColCheck+1

    ColCheck = 0
    CatColFound = 0
    while CatColFound == 0:
        if BirdFile[0][ColCheck]=="catalogueNumber":
            CatColNum=ColCheck
            print "catalogueNumber Column found as column number " + str(CatColNum)
            CatColFound = 1
        else:
            ColCheck=ColCheck+1

    


    #finding and downloading files
    FileEnd=0
    Line=1
    global Entry
    Entry = Line
    while FileEnd==0:
        if End==1:
            global End
            End=2
            thread.exit()
            

        elif Stop==0:
            global CurrentOp
            CurrentOp="Processing entry "+str(Line)+" out of "+str(Entries)+"."
            global Entry
            Entry = Line
            try:
                CatNum=BirdFile[Line][CatColNum]
                MedFile=BirdFile[Line][MedColNum]
                if MedFile=="":
                    print "No associated media found for catalogue number " + str(CatNum)
                else:
                    print ""
                    print " - Media for catalogue number " + str(CatNum) + " found."
                    MedFileName=MedFile.split("/")
                    MedFileName=MedFileName[7]
                    Download=0
                    while Download==0:
                        try:
                            print "Downloading File "+str(MedFileName)+"..."
                            global CurrentOp
                            CurrentOp="Downloading image from entry "+str(Line)+" out of "+str(Entries)+"."
                            urllib.urlretrieve(str(MedFile),str(MedFileName))
                            Download=1
                        except IOError:
                            print "!!!ERROR!!! The file could not be downloaded. Please check your internet connection. Press the Enter key to retry download."
                            raw_input()
                    print "Renaming "+str(MedFileName)+" to "+str(CatNum)+".jpg"
                    global CurrentOp
                    CurrentOp="Renaming image from entry "+str(Line)+" out of "+str(Entries)+"."
                    #renaming file
                    try:
                        os.rename(str(MedFileName), str(CatNum)+".jpg")
                    except WindowsError:
                        print ""
                        print "Overiding file"+str(CatNum)+".jpg"
                        print ""
                        os.remove(CatNum+".jpg")
                        os.rename(str(MedFileName), str(CatNum)+".jpg")

                    #moving file to directory
                    global CurrentOp
                    CurrentOp="Moving image from entry "+str(Line)+" out of "+str(Entries)+" to "+MoveToDir

                    try:
                        shutil.move(str(CatNum)+".jpg",MoveToDir)
                    except:
                        os.remove(MoveToDir+file_delimeter+str(CatNum)+".jpg")
                        shutil.move(str(CatNum)+".jpg",MoveToDir)
                    print ""
                    print "done"
                    print ""
                
            except IndexError:
                FileEnd=1
            Line=Line+1

        elif Stop == 1:
            global CurrentOp
            CurrentOp = "Download Paused"
            time.sleep(3)

        

    global CurrentOp
    CurrentOp="Idle"
    global Entry
    Entry = 0
    

class GUI(tk.Frame):
    
    def __init__(self, parent):
        GlobalVars()
        #thread.start_new_thread(Engine,())
        print ""
        print "GUI thread created"
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.Init()

    def Init(self):
        value_progress =300

        self.parent.title("No-Name File Program")
        self.config(bg='#F0F0F0')
        self.pack(fill = tk.BOTH, expand = 1)

        self.SelectCSV = ttk.Button(self, text="Select CSV File to Process",command=self.FindFile)
        self.SelectCSV.grid(column=0,row=0,sticky=tk.NW)

        self.DeselectCSV = ttk.Button(self, text="Deselect CSV File",command=self.FileDeselect)
        self.DeselectCSV.grid(column=1,row=0,sticky=tk.NW)

        self.PrepareImages = ttk.Button(self, text="Prepare Images", command=self.PreImages)
        self.PrepareImages.grid(column=2,row=0,sticky=tk.NW)

        self.StopDLoad = ttk.Button(self, text="Pause Download", command=self.StopDL)
        self.StopDLoad.grid(column=3,row=0,sticky=tk.NW,)
        self.StopDLoad["state"]=tk.DISABLED

        self.ExitDload = ttk.Button(self, text="Stop Download", command=self.ExitDL)
        self.ExitDload.grid(column=4,row=0,sticky=tk.NW,columnspan=100)
        self.ExitDload["state"]=tk.DISABLED

        self.DataScroll = tk.Scrollbar(self)
        self.DataScroll.grid(column=50, row=2, sticky=tk.NW+tk.S)

        self.DataCanvas = tk.Canvas(self, yscrollcommand=self.DataScroll.set, relief=tk.FLAT, background = "#D2D2D2", width=620, height=380)
        self.DataCanvas.grid(column=0, row=2, sticky=tk.NW, columnspan=50)

        self.DataScroll.config(command=self.DataCanvas.yview)

        

        self.Console=ttk.Button(self,text="Console",command=self.Console)
        self.Console.grid(column=0,row=700,sticky=tk.NW)

        self.SelectedCSV = ttk.Label(self, text=FileLoc)
        self.SelectedCSV.grid(column=0,row=1,sticky=tk.NW,columnspan=200)

        self.CurrentOperation = ttk.Label(self, text=CurrentOp)
        self.CurrentOperation.grid(column=0,row=998,sticky=tk.NW,columnspan=200)

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
            
        
        

    def FindFile(self):
        global CurrentOp
        CurrentOp="Selecting CSV File..."
        global FileLoc
        FileLoc = tkFileDialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if FileLoc!="":
            global FileLoc
            """
            If this runs on a Windows machine, this will automatically escape '\' to '\\'. On Linux/MacOSX, it will do nothing.
            The way it was previously meant that ALL file delimeters were translated to '\\', which simply does not work on Linux
            (and possibly OSX as well). This solution does require the application to keep track of the file delimeter used, which
            is implemented through a variable called file_delimeter.
            """
            # So hopefully doing this myself will stop the type issue. The function escape() can be found at line 15 
            FileLoc = escape(FileLoc)
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
            
        
            thread.start_new_thread(Engine,())

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
            

    def Console(self):
        print "Enter a command..."
        exec raw_input(">>> ")
            
        

tkin=tk.Tk()
tkin.geometry('641x480')
GUI = GUI(tkin)
GUI.mainloop()
