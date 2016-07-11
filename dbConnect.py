import sys
import os
import parseTools as pt
from pymongo import MongoClient

# The current plan ?schema? is to have a main collection of the encounters, with base encounter summaries (DPS, Start/End time, Targets, Number of Hits, Number of Crits, Class/Subclass Identifier etc.). More detailed information, such as actions in the encounter will be kept in a separate table. E.g.
# {TimeStamp} {Ability Name} {Action Magnitude e.g. Healing: ####, Damage: ####} {Crit: Bool} {Encounter ID}

# There will also be a Dictionary file to identify abilities with their effects and class identifiers.
# db = client.SWTORLogs

def getDatabase(database):
    client = MongoClient()
    db = client[database]

    return db

def insertLog(pathName, collectionName, online = False, onlineData = None):
    db = getDatabase("learn")
    collection = db[collectionName]
    fileLog = db.fileLog

    #check if document is already in the database
    if fileLog.find({"filePath": {"$exists": "true", "$eq": pathName}}).count() > 0:
        print("File already in the database")
        return
    else:
        fileLog.insert_one({"filePath": pathName})

    #parse the documment
    if online:
        encounters = pt.parsingWeb(onlineData)
    else:
        encounters = pt.parsingLocal(pathName)
        if encounters == None:
            return

    #Loop through the encounters inserting them into collections
    for encounter in encounters:
        try:
            #Separate the single fields and the array fields
            encounterDoc = {key: encounter.__dict__[key] for key in encounter.__dict__.keys() if key not in ["duration", "rotation", "damage", "healing", "taken", "threat"] }
            encounterDoc['fileName'] = os.path.basename(pathName)

            # Put corresponding information in the right collection
            encounterID = collection.insert_one(encounterDoc).inserted_id

            for key in ["damage", "threat", "healing", "taken", "rotation"]:
                collectionName2 = key + "Log"
                collection2 = db[collectionName2]
                for number in encounter.__dict__[key]:
                    collection2.insert_one({"time": number[0], key: number[1], "encounterID": encounterID})

        except:
            raise

def insertAbility(document):
    pass
if __name__ == '__main__':
# insertLog('combatTest.txt','Test')
# print(db.Test.count())
    path = 'C:\\Users\\Scott\\Documents\\Star Wars - The Old Republic\\CombatLogs'
    for fileName in os.listdir(path):
        print('Adding {} to the database...'.format(fileName))
        insertLog(path + '\\' + fileName,'Test')
