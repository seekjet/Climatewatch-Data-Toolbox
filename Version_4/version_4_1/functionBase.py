#needed modules: csv, tkFileDialog
import csv
import tkFileDialog

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

    #save headers and dictionary to file
    fileName = (fileLocation.split("/")[-1]).split('.')[0]
    fileDict['details']['fileName']=fileName
    target = open(fileName+'.cdt', 'w')
    target.write(str(fileDict))

    #return final dictionary
    return fileDict

def loadCDT(fileLocation):
    f = open(fileLocation,'r').read()
    fileDict=eval(f)
    return fileDict

def findFile(flag):
    if flag=='import':
        fileLocation=tkFileDialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
        if fileLocation != "":
            x=importFile(fileLocation)
            return x
