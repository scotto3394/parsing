import re, os, time, datetime
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

	def __str__(self):
		return self.name

class damage(object):

	def __init__(self,magnitude = 'none', dType = 'none', crit = False):
		self.magnitude = magnitude
		self.type = dType
		self.crit= crit

class encounter(object):

	def __init__(self, startTime, number, toonName):
		self.startT = startTime
		self.endT = None
		self.ID = number
		self.player = toonName
		self.DPS = 0
		self.DTPS = 0
		self.HPS = 0
		self.TPS = 0
		self.targets = {}
		self.duration = 0
		self.hits = 0
		self.crits = 0

	def close(self, endTime):
		self.endT = endTime
		deltaDiff = endTime - self.startT
		delta = deltaDiff.seconds + deltaDiff.microseconds/1000000.
		self.duration = deltaDiff

		self.DPS = sum(self.damage)/(delta * 1.)
		self.TPS = sum(self.threat)/(delta * 1.)
		self.HPS = sum(self.healing)/(delta * 1.)
		self.DTPS = sum(self.taken)/(delta * 1.)

	def __str__(self):
		return "Encounter #{}".format(self.ID)

	def info(self):
		strRepr = "Encounter #{}, StartTime: {}, Current Duration: {}, Targets: {}".format(self.ID, self.startT.time(), self.duration, self.targets)
		return strRepr

	def printRotation(self):
		for entries in self.rotation:
			print("{}:\t {}".format(str(entries[0]).ljust(7), entries[1]))

	def update(self, time, source, target, ability, actionType, action, actionDetails, threat):
		deltaDiff = time - self.startT
		delta = deltaDiff.seconds + deltaDiff.microseconds/1000000.
		self.duration = deltaDiff

		if ability.name != 'none' and source.name == self.player:
			self.rotation.append((time, ability.name))

		# If there is threat, something interesting happened.
		if threat != 'none':
			self.threat.append((time,threat))
			self.TPS = sum(map(lambda x: x[1], self.threat))/(delta * 1.)

			if source.name == self.player:
			# Either you did something
				if target.ID != 'player':
				# You did damage
					if type(actionDetails.magnitude) == type(1):
						self.damage.append((time,actionDetails.magnitude))
						self.DPS = sum(map(lambda x: x[1], self.damage))/(delta * 1.)
				else:
				# You healed
					if type(actionDetails.magnitude) == type(1):
						self.healing.append((time, actionDetails.magnitude))
						self.HPS = sum(map(lambda x: x[1], self.healing))/(delta * 1.)

			else:
			# Or something was done to you
				if source.ID != 'player':
				# You took damage
					if type(actionDetails.magnitude) == type(1):
						self.taken.append((time, actionDetails.magnitude))
						self.DTPS = sum(map(lambda x: x[1], self.taken))/(delta * 1.)
				else:
				# You were healed
					pass

	def plotData(self):
		pass

#======================================================================
def takeInput(string):
	if version_info[0] < 3:
		output = raw_input(string)
	else:
		output = input(string)

	return output

def clean(string):
	try:
		string = string.lstrip('@').rstrip('\r\n>)')
		return string.split(' {')[0]
	except IndexError:
		return

def parsingLocal(pathName):
	combatLogs = []
	regEx = '|'.join(map(re.escape, ['] [', '] (', ') <']))
	with open(pathName,'r',encoding='latin1') as file:
		inCombat = False
		waiting = -1

		# This is indicative of an empty file
		try:
			toonName = re.split(regEx, file.readline())[1][1:]
		except:
			return
		encounterNumber = 0

		for line in file:
			lineList = re.split(regEx, line)

			# Check if in combat
		# Action ----------------------------------------------------------
			actionList = lineList[4].split(': ')
			tempType = actionList[0].split(' {')
			actionType = gameObject(tempType[0], tempType[1])
			tempAction = ': '.join(actionList[1:]).split(' {')
			action = gameObject(tempAction[0], tempAction[1])
		# -----------------------------------------------------------------

			actionClean = clean(action.name)

			if actionClean == 'EnterCombat':
				if waiting <= 0:
					inCombat = True
					encounterNumber += 1
					startTime = datetime.datetime.strptime(lineList[0][1:], '%H:%M:%S.%f')
					fight = encounter(startTime,encounterNumber,toonName)
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
						source = gameObject(clean(lineList[1]), 'player')

				try:
					targetVec = lineList[2].split(':')
					target = gameObject(clean(targetVec[0]), int(targetVec[1]))
				except:
					if lineList[2] == '':
						target = gameObject('none')
					else:
						target = gameObject(clean(lineList[2]), 'player')

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

		# Add to encounter ------------------------------------------------
				try:
					if waiting < 0:
						fight.update(timeObj, source, target, ability, actionType, action, actionDetails, threat)
				except:
					print(lineList)
					break
		# -----------------------------------------------------------------

			if actionClean == 'ExitCombat':
				try:
					waiting = 10
					fight.close(timeObj)
				except:
					pass

			waiting -= 1
			if waiting == 0:
				inCombat = False
				try:
					combatLogs.append(fight)
				except:
					pass

	return combatLogs

def parsingWeb(data):
	combatLogs = []

	# Manage time
	time = data[0]
	timeObj = datetime.datetime.strptime(timeStr, '%H:%M:%S.%f')

	# Manage source/target
	if data[1][0] == '@':
		source = gameObject(data[1].lstrip('@'), 'player')
	else:
		source = gameObject(data[1])
	if data[2][0] == '@':
		target = gameObject(data[2].lstrip('@'), 'player')
	else:
		target = gameObject(data[2])

	# Manage ability used
	if data[3] == '':
		ability = gameObject('none')
	else:
		ability = gameObject(data[3])

	# Manage effects/actions

		# Including magnitudes/crits/threat/etc.

	fight.update(timeObj, source, target, ability, actionType, action, actionDetails, threat)
	return combatLogs


if __name__ == '__main__':
	combatLog = parsingLocal('combatTest.txt')
	document = {key: combatLog[0].__dict__[key] for key in combatLog[0].__dict__.keys() if key != "rotation" and key != "duration"}
	print(document.keys())
