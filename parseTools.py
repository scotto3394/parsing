import datetime
import re
import matplotlib as plt

class parseLine(object):

    def __init__(self,time,source,target, ability , actionType, action, actionDetails, threat):
        self.time = time
        self.source = source
        self.target = target
        self.ability = ability
        self.actionType = actionType
        self.action = action
        self.actionDetails = actionDetails
        self.threat = threat

class gameObject(object):

    def __init__(self, name, ID = 'none'):
        self.name = name
        self.ID = ID

class damage(object):

    def __init__(self,magnitude = 'none', dType = 'none', crit = False):
        self.magnitude = magnitude
        self.type = dType
        self.crit= crit


def clean(string):
    try:
        if string[0] == '@':
            string = string[1:]
        if string[-1] == ')':
            string = string[:-1]
        if string[-1] == '\n':
            string = string[:-3]
        if string[-1] == '>':
            string = string[:-1]
        return string.split(' {')[0]
    except IndexError:
        return

def readLog(fileName):
    combatLogs = []
    regEx = '|'.join(map(re.escape, ['] [', '] (', ') <']))
    with open(fileName, 'r') as parseLog:
        print 'Parsing...'
        inCombat = False
        for line in parseLog:
            lineList = re.split(regEx, line)
            # Pull out and clean each entry in the list

            # Time -----------------------------------------------------------
            timeStr = lineList[0][1:]
            timeObj = datetime.datetime.strptime(timeStr, '%H:%M:%S.%f')
            # -----------------------------------------------------------------

            # Source / Target ------------------------------------------------
            try:
                sourceVec = lineList[1].split(': ')
                source = gameObject(clean(sourceVec[0]), int(sourceVec[1]))
            except:
                if lineList[1] == '':
                    source = gameObject('none')
                else:
                    source = gameObject(clean(lineList[1]))

            try:
                targetVec = lineList[2].split(': ')
                target = gameObject(clean(targetVec[0]), int(targetVec[1]))
            except:
                if lineList[2] == '':
                    target = gameObject('none')
                else:
                    target = gameObject(clean(lineList[2]))

            # -----------------------------------------------------------------

            # Ability ---------------------------------------------------------
            if lineList[3] == '': # gameObject class
                ability = gameObject('none')
            else:
                temp = lineList[3].split(' {')
                ability = gameObject(temp[0], temp[1])
            # -----------------------------------------------------------------

            # Action ----------------------------------------------------------
            actionList = lineList[4].split(': ')
            tempType = actionList[0].split(' {')
            actionType = gameObject(tempType[0], tempType[1])
            tempAction = ': '.join(actionList[1:]).split(' {')
            action = gameObject(tempAction[0], tempAction[1])
            # -----------------------------------------------------------------

            # Damage / Threat -------------------------------------------------
            if lineList[5] == ')\r\n' or lineList[5] == '':
                actionDetails = damage()
            else:
                tempDetails = clean(lineList[5])

                try:
                    tempDetailsList = tempDetails.split(' ')
                    mag = tempDetailsList[0]
                    dType = tempDetailsList[1]
                    crit = False
                    if '*' in mag:
                        crit = True
                        mag = mag[:-1]
                    actionDetails = damage(int(mag), dType, crit)
                except:
                    mag = tempDetails
                    crit = False
                    if '*' in mag:
                        crit = True
                        mag = mag[:-1]
                    actionDetails = damage(int(mag), crit = crit)



            try:
                threat = int(clean(lineList[6]))
            except IndexError:
                threat = 'none'
            # -----------------------------------------------------------------

            # Combat Filter
            actionClean = clean(action.name)

            if actionClean == 'EnterCombat':
                inCombat = True
                print 'Writing...'

            if inCombat:
                combatLine = parseLine(timeObj, source, target, ability, actionType, action, actionDetails,threat)
                combatLogs.append(combatLine)

            if actionClean == 'ExitCombat':
                inCombat = False
                print 'Skipping...'

    print 'Uploaded!'
    return combatLogs

def printLogs(combatLogs):

    for line in combatLogs:
        if line.action.name == 'EnterCombat':
            startTime = line.time

        try:
            currentTime = line.time
            delta = str(currentTime - startTime)
            sourceTarget =  line.source.name + '->' +line.target.name

            actionType = line.actionType.name + ':'

            print '{}| {}| {}| {} {} | {}'.format(str(delta).ljust(14), sourceTarget.ljust(30),line.ability.name.ljust(22), actionType.rjust(15), line.action.name.ljust(40), str(line.actionDetails.magnitude).ljust(15))
        except:
            print line.target.__dict__.values()
            break

        if line.action.name == 'ExitCombat':
            print '\n'
            continuePrompt = raw_input('Would you like to print next combat log? (y/n): ')
            if continuePrompt == 'y':
                continue
            else:
                break

def buildRotation(combatLogs):
    pass
def printRotation(combatLogs):
    pass

def dpsCalc(combatLogs):
    pass
    
combatLog = readLog('combatTest.txt')
printLogs(combatLog)
