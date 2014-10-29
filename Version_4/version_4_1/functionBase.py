import os
import csv
import tkFileDialog
import tkMessageBox
import json
from sys import platform as SYS_PLATFORM

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

#fileLocation in the format of C:/Users/Name/Desktop/cracticus_tibicen.csv
def importFile(fileLocation):
    

    #import csv entries, save to dictionary, delete imported table
    fileDict={'entries':{}}
    with open(fileLocation, 'rb') as f:
        table = list(csv.reader(f))
    headers = table[0]
    del table[0]
    n=0
    for item in table:
        fileDict['entries'][str(n)] = {}
        h=0
        for item in headers:
            fileDict['entries'][str(n)][str(item)]=table[n][h]
            h+=1
        n+=1
    fileDict['details']={}
    #put file details here
    fileDict['details']['totEntries']=n
    
    #put file details here
    fileDict['headers']=headers
    fileDict['options']={}
    #put default options here

    #put default options here
    del table

    #Get file name and original format
    fileName = (fileLocation.split("/")[-1]).split('.')[0]
    fileFormat=(fileLocation.split("/")[-1]).split('.')[-1]
    fileDict['details']['fileName']=fileName
    fileDict['details']['fileFormat']=fileFormat
    for i in range(fileDict['details']['totEntries']):
        if "__isCorrect__" not in fileDict['entries'][str(i)].keys():
            fileDict['entries'][str(i)]["__isCorrect__"] = "yes"
    #save dictionary to file
    target = open(fileName+'.json', 'w')
    #target.write(json.dump(fileDict))
    json.dump(fileDict,target,indent=4,separators=(',',':'))
    
    #return final dictionary
    return fileDict

def loadJSON(fileLocation):
    f = open(fileLocation,'r')
    fileDict=json.load(f)
    for i in range(fileDict['details']['totEntries']):
        if "__isCorrect__" not in fileDict['entries'][str(i)].keys():
            fileDict['entries'][str(i)]["__isCorrect__"] = "yes"
    fileDict['details']['saveLocation']=fileLocation
    f.close()
    #print fileDict['details']['fileName']
    return fileDict


def readFile(flag):
    if flag=='import':
        fileLocation=tkFileDialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if fileLocation != "":
            x=importFile(fileLocation)
            return x
        else:
            return "nope"
    if flag=='load':
        fileLocation=tkFileDialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if fileLocation != "":
            x=loadJSON(fileLocation)
            return x
        else:
            return "nope"

def writeFile(flag, fileDict):
    if flag=='saveAs':
        fileLocation=tkFileDialog.asksaveasfilename(filetypes=[('JSON Files','*.json')],initialfile=(fileDict['details']['fileName']))
        if fileLocation != "":
            x=fileLocation.split('.')[-1]
            if x!='json':
                fileLocation=fileLocation+'.json'
            fileDict['details']['saveLocation']=fileLocation
            target = open(fileLocation,'w')
            json.dump(fileDict,target,indent=4,separators=(',',':'))
            return fileLocation
            
    if flag=='save':
        try:
            target = open(fileDict['details']['saveLocation'],'w')
            json.dump(fileDict,target,indent=4,separators=(',',':'))
        except KeyError:
            #popup of you need to save as first
            writeFile('saveAs', fileDict)

def exportFile(fileDict):
    headers = fileDict['headers']
    nestedCorrectList=[]
    nestedWrongList=[]
    nestedCorrectList.append(headers)
    nestedWrongList.append(headers)
    for i in range(fileDict['details']['totEntries']):
        tempList=[]
        for head in headers:
            tempList.append(fileDict['entries'][str(i)][head])
        if fileDict['entries'][str(i)]["__isCorrect__"] == "yes":
            nestedCorrectList.append(tempList)
        else:
            nestedWrongList.append(tempList)
    #print tempList[1]
    ####
    fileDirectory=tkFileDialog.askdirectory(initialdir=(fileDict['details']['fileName']))
    if fileDirectory != "":
        try:
            if not os.path.isdir(fileDirectory):
                os.mkdir(fileDirectory)
            with open(fileDirectory+file_delimeter+fileDict['details']['fileName']+"-correct.csv", 'wb') as correctFile:
                writer = csv.writer(correctFile)
                writer.writerows(nestedCorrectList)
            with open(fileDirectory+file_delimeter+fileDict['details']['fileName']+"-wrong.csv", 'wb') as wrongFile:
                writer = csv.writer(wrongFile)
                writer.writerows(nestedWrongList)
            tkMessageBox.showinfo("Export", "File successfully exported to: "+fileDirectory)
        except:
            tkMessageBox.showwarning("Export", "Something went wrong! Make sure to double check your file path. Your supplied the following directory: "+fileDirectory)
