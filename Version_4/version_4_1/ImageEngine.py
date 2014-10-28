from sys import platform as SYS_PLATFORM
import os
import urllib
from shutil import move as shmove
import thread

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
    
def Engine(guiObject):
    global shutoff
    shutoff = False
    global wait
    wait = False
    for i in range(0, guiObject.fileDict["details"]["totEntries"]):
        if shutoff:
            print "Image thread shutting down."
            wait = True
            thread.exit()
        if guiObject.fileDict["entries"][str(i)]["associatedMedia"] != "":    
            if not os.path.isfile("resources"+file_delimeter+guiObject.fileDict["entries"][str(i)]["catalogueNumber"]):
                urllib.urlretrieve(guiObject.fileDict["entries"][str(i)]["associatedMedia"], "resources"+file_delimeter+guiObject.fileDict["entries"][str(i)]["catalogueNumber"])
                if i in range( (guiObject.pageNum-1)*guiObject.global_config["displayedEntries"], guiObject.pageNum*guiObject.global_config["displayedEntries"] ):
                     for j in guiObject.displayedAllList:
                        if j.uid == i:
                            j.picturePath = "resources"+file_delimeter+guiObject.fileDict["entries"][str(i)]["catalogueNumber"]
                            j.drawItems()
                            
                     for j in guiObject.displayedEntryList:
                         if j.uid == i:
                             j.picturePath = "resources"+file_delimeter+guiObject.fileDict["entries"][str(i)]["catalogueNumber"]
                             j.drawItems()
    
    wait = True
    thread.exit()
        
