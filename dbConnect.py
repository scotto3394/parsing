import sys
import os.path
import parseTools as pt
from pymongo import MongoClient

client = MongoClient()
db = client.SWTORLogs

def insertLog(pathName, collectionName):
    encounters = pt.parsing(pathName)
    collection = db[collectionName]

    # Look into automatic mapping of methods -> fields
    # For now this is manually specified based on the Enounter Class Structure
    for encounter in encounters:
        try:
            document = {key: encounter.__dict__[key] for key in encounter.__dict__.keys() if key != "rotation" and key != "duration" }
            document['fileName'] = os.path.basename(pathName)
            collection.insert_one(document)
        except:
            raise

insertLog('combatTest.txt','Test')
print(db.Test.count())
