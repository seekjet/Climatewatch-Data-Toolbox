#needed modules: csv, tkFileDialog, json
import csv
import tkFileDialog
import json

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
    #save dictionary to file
    target = open(fileName+'.json', 'w')
    #target.write(json.dump(fileDict))
    json.dump(fileDict,target,indent=4,separators=(',',':'))
    
    #return final dictionary
    return fileDict

def loadJSON(fileLocation):
    f = open(fileLocation,'r')
    fileDict=json.load(f)
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
    if flag=='load':
        fileLocation=tkFileDialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if fileLocation != "":
            x=loadJSON(fileLocation)
            return x

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
