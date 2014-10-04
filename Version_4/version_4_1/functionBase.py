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

def loadCDT(fileLocation):
    f = open(fileLocation,'r')
    fileDict=json.load(f)
    print fileDict['details']['fileName']
    return fileDict
loadCDT('C:/Users/Ryan/Documents/repositories/Climatewatch-Data-Toolbox/Version_4/version_4_1/cracticus_tibicen_112013-042014.json')

def findFile(flag):
    if flag=='import':
        fileLocation=tkFileDialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if fileLocation != "":
            x=importFile(fileLocation)
            return x
