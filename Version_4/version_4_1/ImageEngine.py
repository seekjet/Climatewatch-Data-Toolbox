import urllib
import csv
import os
from sys import platform as SYS_PLATFORM
from shutil import move as shmove

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
                        shmove(str(CatNum)+".jpg",MoveToDir)
                    except:
                        os.remove(MoveToDir+file_delimeter+str(CatNum)+".jpg")
                        shmove(str(CatNum)+".jpg",MoveToDir)
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
    

