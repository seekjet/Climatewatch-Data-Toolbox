#needed modules: csv, 
import csv

#fileLocation in the format of C:/Users/Name/Desktop/cracticus_tibicen.csv
def importCSV(fileLocation):
    #import csv, save to dictionary
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
    #delete table variable
    del table
    #save headers and dictionary to file
    fileName = (fileLocation.split("/")[-1]).split('.')[0]
    target = open(fileName+'.cdt', 'w')
    target.write(str(fileDict))

def loadCDT(fileLocation):
    f = open(fileLocation,'r').read()
    fileDict=eval(f)
