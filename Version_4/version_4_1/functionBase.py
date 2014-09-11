#needed modules: csv, 
import csv
#fileLocation in the format of C:/Users/Name/Desktop/cracticus_tibicen.csv
def importCSV(fileLocation):
    fileDict={}
    with open(fileLocation, 'rb') as f:
        table = list(csv.reader(f))
    headers = table[0]
    del table[0]
    n=0
    for item in table:
        fileDict[str(n)] = {}
        h=0
        for item in headers:
            fileDict[str(n)][str(item)]=table[n][h]
            h+=1
        n+=1
    print fileDict["0"]
importCSV('C:/Users/Ryan/Desktop/cracticus_tibicen_112013-042014.csv')
