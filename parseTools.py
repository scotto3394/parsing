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
		self.taken = []
		self.threat = []
		self.damage = []
		self.healing = []
		self.rotation = []
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
				if target.ID != 'none':
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
				if source.ID != 'none':
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

def follow(thefile):
	#thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			#time.sleep(0.1)
			#continue
			raise StopIteration
		yield line

def parsing(pathName):
	combatLogs = []
	regEx = '|'.join(map(re.escape, ['] [', '] (', ') <']))
	#path = '/cygdrive/c/Users/Scott/Documents/Star Wars - The Old Republic/CombatLogs'
	#fileName = sorted(os.listdir(path), reverse = True)[0]
	#file = open(path+ '/' + fileName, 'r')
	file = open(pathName,'r',encoding='latin1')
	# print('Parsing...')
	inCombat = False
	waiting = -1
	# This is indicative of an empty file
	try:
		toonName = re.split(regEx, file.readline())[1][1:]
	except:
		return
	# print('Skipping...')
	encounterNumber = 0

	for line in follow(file):
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
				# print("Writing...")
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
			# print('Skipping...')

	# print('Uploaded!')
	return combatLogs

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

if __name__ == '__main__':
	combatLog = parsing('combatTest.txt')
	document = {key: combatLog[0].__dict__[key] for key in combatLog[0].__dict__.keys() if key != "rotation" and key != "duration"}
	print(document.keys())
