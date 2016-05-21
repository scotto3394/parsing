import datetime
import re
from sys import version_info
import matplotlib as mpl

import matplotlib.rcsetup as rcsetup

mpl.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt


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

class encounter(object):
	pass

def takeInput(string):
	if version_info[0] < 3:
		output = raw_input(string)
	else:
		output = input(string)
		
	return output

def clean(string):
	try:
		if string[0] == '@':
			string = string[1:]
		if string[-1] == ')':
			string = string[:-1]
		if string[-1] == '\n':
			string = string[:-3]
			# changes between 2 & 3 it seems. depending on ')\r\n' and ')\n'
		if string[-1] == '>':
			string = string[:-1]
		return string.split(' {')[0]
	except IndexError:
		return

def readLog(fileName):
	combatLogs = []
	regEx = '|'.join(map(re.escape, ['] [', '] (', ') <']))
	with open(fileName, 'r') as parseLog:#, encoding='utf-8', errors='ignore') as parseLog:
		print('Parsing...')
		inCombat = False
		waiting = -1
		print('Skipping...')
		for line in parseLog:
			lineList = re.split(regEx, line)
			
			# Check if in combat
		# Action ----------------------------------------------------------
			actionList = lineList[4].split(': ')
			tempType = actionList[0].split(' {')
			actionType = gameObject(tempType[0], tempType[1])
			tempAction = ': '.join(actionList[1:]).split(' {')
			action = gameObject(tempAction[0], tempAction[1])
		# ----------------------------------------------------------------

			actionClean = clean(action.name)

			if actionClean == 'EnterCombat':
				if waiting <= 0:
					inCombat = True
					print('Writing...')
				else:
					waiting = -1

			if inCombat:

		# Pull out and clean each entry in the list


		# Time -----------------------------------------------------------
				timeStr = lineList[0][1:]
				timeObj = datetime.datetime.strptime(timeStr, '%H:%M:%S.%f')
		# -----------------------------------------------------------------
			
		# Source / Target ------------------------------------------------
				try:
					sourceVec = lineList[1].split(':')
					source = gameObject(clean(sourceVec[0]), int(sourceVec[1]))
				except:
					if lineList[1] == '':
						source = gameObject('none')
					else:
						source = gameObject(clean(lineList[1]))

				try:
					targetVec = lineList[2].split(':')
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
				
		# Damage / Threat -------------------------------------------------
				if lineList[5] == ')\r\n' or lineList[5] == '' or lineList[5] == ')\n':
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
		
		# Append to file
				combatLine = parseLine(timeObj, source, target, ability, actionType, action, actionDetails,threat)

				combatLogs.append(combatLine)

			if actionClean == 'ExitCombat':
				waiting = 10

			waiting -= 1
			if waiting == 0:
				inCombat = False
				print('Skipping...')

	print('Uploaded!')
	return combatLogs

def printLogs(combatLogs):
	waiting = -1
	for line in combatLogs:
		if line.action.name == 'EnterCombat':
			if waiting <= 0:
				startTime = line.time
			else:
				waiting = -1

		try:
			currentTime = line.time
			delta = str(currentTime - startTime)
			sourceTarget = line.source.name + '->' +line.target.name

			actionType = line.actionType.name + ':'

			print('{}| {}| {}| {} {} | {}'.format(str(delta).ljust(14), sourceTarget.ljust(30),line.ability.name.ljust(22), actionType.rjust(15), line.action.name.ljust(40), str(line.actionDetails.magnitude).ljust(15)))
		except:
			print(line.target.__dict__.values())
			break

		if line.action.name == 'ExitCombat':
			waiting = 10

		waiting -= 1
		if waiting == 0:
			print('\n')
			continuePrompt = takeInput('Would you like to print next combat log? (y/n): ')
			if continuePrompt == 'y':
				continue
			else:
				break

def buildRotation(combatLogs):
	pass
def printRotation(combatLogs):
	pass

def dpsOutput(combatLogs, playerName):
	waiting = -1
	for line in combatLogs:
		if line.action.name == 'EnterCombat':
			if waiting <= 0:
				startTime = line.time
				cumDamage = 0
				hits = 0
				crits = 0

				damageList = []
				DPS = []
				timeList = []
				targetNames = []
				targetIDs = {}
				threat = []
			else:
				waiting = -1

		try:
			currentTime = line.time
			deltaDiff = currentTime - startTime
			delta = deltaDiff.seconds + deltaDiff.microseconds / 1000000.

			if delta < 1:
				continue

			# damage stats
			if line.action.name.lower() == 'damage' and line.source.name.lower() == playerName.lower():
				[hits, crits, cumDamage] = dpsCalc(line, hits, crits, cumDamage, damageList, DPS, timeList, targetIDs, targetNames, delta,threat)

		except:
			pass

		if line.action.name == 'ExitCombat':
			waiting = 10

		waiting -= 1
		if waiting == 0:
			# plotting subroutine
			p = plt.figure(1)
			p.suptitle(', '.join(targetNames))
			plt.subplot(2,1,1)
			plt.plot(timeList, DPS, 'b-') #DPS plot
			plt.title('DPS')
			plt.subplot(2,1,2)
			plt.plot(timeList,damageList,'r-') #Damage plot
			plt.title('Damage')

			#plt.show(block = False)
			plt.show()
			print('Number of Hits: {:,}'.format(hits))
			print('Crit Percentage: {:.2f}%'.format((100.*crits)/(hits)))
			print('Total Damage Done: {:,}'.format(cumDamage))

			print('\n')
			damageBreakdown = takeInput('Would you like a damage breakdown? (y/n): ')
			if damageBreakdown == 'y':
				printDamage(targetIDs)
			else:
				pass

			print('\n')
			continuePrompt = takeInput('Would you like to print next combat log? (y/n): ')
			plt.close()
			if continuePrompt == 'y':
				continue
			else:
				break

def dpsCalc(damageInfo, hits, crits, cumDamage, damageList, DPS, timeList, targetIDs, targetNames, delta, threat):
	# DPS stats
	details = damageInfo.actionDetails
	cumDamage += details.magnitude
	hits += 1
	if details.crit:
		crits += 1
	damageList.append(details.magnitude)
	DPS.append(cumDamage / delta)
	timeList.append(delta)

	# target identification (+ ability breakdown)
	tar = damageInfo.target
	if tar.ID != 'none':
		if tar.ID in targetIDs.keys():
			if damageInfo.ability.name in targetIDs[tar.ID][1].keys():
				targetIDs[tar.ID][1][damageInfo.ability.name][0] += details.magnitude
				targetIDs[tar.ID][1][damageInfo.ability.name][1] += 1
			else:
				targetIDs[tar.ID][1][damageInfo.ability.name] = [details.magnitude,0]
		else:
			targetIDs[tar.ID] = [tar.name,{damageInfo.ability.name: [details.magnitude,0]}]
			targetNames.append(tar.name)
			print(tar.name)

	return hits, crits, cumDamage

def printDamage(targetIDs):
	for ID in targetIDs.keys():
		print('{}: '.format(targetIDs[ID][0]))

		for names,numbers in sorted(targetIDs[ID][1].items(), key = lambda pair: pair[1][0], reverse = True):
			print('\t {}: {}'.format(names, numbers[0]))

combatLog = readLog('combatTest.txt')
#printLogs(combatLog)
dpsOutput(combatLog, 'emixan')