import sys
import os
import parseTools as pt
from pymongo import MongoClient

client = MongoClient()
# db = client.SWTORLogs
db = client.learn

def insertLog(pathName, collectionName):
    fileLog = db.fileLog
    if fileLog.find({"filePath": {"$exists": "true", "$eq": pathName}}).count() > 0:
        print("File already in the database")
        return
    else:
        fileLog.insert_one({"filePath": pathName})

    encounters = pt.parsing(pathName)
    collection = db[collectionName]

    #Add in a check to see if file already exists in there.
    for encounter in encounters:
        try:
            document = {key: encounter.__dict__[key] for key in encounter.__dict__.keys() if key != "rotation" and key != "duration" }
            document['fileName'] = os.path.basename(pathName)
            collection.insert_one(document)
        except:
            raise

# insertLog('combatTest.txt','Test')
# print(db.Test.count())
path = 'C:\\Users\\Scott\\Documents\\Star Wars - The Old Republic\\CombatLogs'
for fileName in os.listdir(path):
    print('Adding {} to the database...'.format(fileName))
    insertLog(path + '\\' + fileName,'Test')
