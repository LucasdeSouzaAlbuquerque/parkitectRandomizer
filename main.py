import os
import gzip
import shutil
import random
import json

def getListOfFiles(dirName):
	listOfFile = os.listdir(dirName)
	allFiles = list()
	for entry in listOfFile:
		fullPath = os.path.join(dirName, entry)
		if os.path.isdir(fullPath):
			allFiles = allFiles + getListOfFiles(fullPath)
		else:
			allFiles.append({"entry": entry, "fullPath": fullPath})        
	return allFiles

def getLevel(levelPool, usedLevels):
	repeat = True
	while repeat:
		repeat = False
		newLevel = levelPool[random.randint(0, len(levelPool)-1)]
		if(newLevel["entry"] in usedLevels):
			repeat = True
		else:
			return newLevel

def ungzip(elem):
	with gzip.open(elem["fullPath"], 'rb') as f_in:
		with open("Temp/"+elem["entry"]+".txt", 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)

def switchGuids(oldLevel, newLevel):
	with open("Temp/"+oldLevel["entry"]+".txt") as old_file:
		old_data = old_file.read()
		guid_index = old_data.find("guid")
		old_guid_forward = old_data[guid_index+7:len(old_data)]
		end_guid_index = old_guid_forward.find('",')
		guid = old_guid_forward[:end_guid_index]      
		with open("Temp/"+newLevel["entry"]+".txt") as new_file:
			newData = new_file.read()
			return replaceWithValue('"guid"', newData, guid, ",")

def writeToFile(newLevel, data):
	f_out = gzip.open('New Campaign/Campaign/'+newLevel["entry"], 'wb')
	byteData = bytes(data, 'utf-8')
	f_out.write(byteData)
	f_out.close()

def printLevel(officialLevel, newLevel):
	print(officialLevel["entry"] + " -> " + newLevel["entry"])

def randRangeStep(start, stop, step=0):
	if(step == 0):
		return random.uniform(start, stop)
	else:
		return random.randint(0, int((stop-start)/step)) * step + start

def replaceSimpleRandom(field, newData, start, stop, step=0, separator=","):
	newValue = randRangeStep(start, stop, step)
	return replaceWithValue(field, newData, newValue, separator)

def getOffset(field):
	return 2+len(field)

def replaceWithValue(field, newData, newValue, separator=",", offset=0):
	newData2 = newData[:]
	if(offset == 0):
		offset = getOffset(field)
	index = newData2.find(field)
	forward = newData2[index+offset:len(newData2)]
	end_index = forward.find(separator)
	newData_modified = newData2[:index+offset] + str(newValue) + newData2[index+offset+end_index:]
	#print(newData_modified[index-offset:index+offset+end_index+offset])
	return newData_modified

def replaceWithBoolean(field, newData, percentageThreshold=50, separator=","):
	value = random.randint(1,100)
	newBool = "false"
	if(value > percentageThreshold):
		newBool = "true"
	return replaceWithValue(field, newData, newBool, separator)

def whatToCharge(newData, percentageThreshold=50, separator=","):
	value = random.randint(1,100)
	if(value > percentageThreshold):
		newData = replaceWithValue("cantChangeParkEntranceFee", newData[:], "true", separator)
		newData = replaceWithValue("freeRideEntranceFees", newData[:], "false", separator)
	elif(value <= 100 - percentageThreshold):
		newData = replaceWithValue("cantChangeParkEntranceFee", newData[:], "false", separator)
		newData = replaceWithValue("freeRideEntranceFees", newData[:], "true", separator)
	else:
		newData = replaceWithValue("cantChangeParkEntranceFee", newData[:], "false", separator)
		newData = replaceWithValue("freeRideEntranceFees", newData[:], "false", separator)
	return newData

def replaceResearch(newData):
	return replaceWithValue('rules', newData, randomizeResearch(), "],", offset=getOffset("rules"))

def randomizeResearch():
	result = "["
	with open("Data/researchableObjects.txt", 'r') as f_in:
		researchableObjects = f_in.readlines()
		length = len(researchableObjects)
		ratesOfObjectsUnlocked = random.randint(3, 9)
		ratesOfObjectsToUnlock = random.randint(2, 8)
		for i in range(0,len(researchableObjects)):
			x = researchableObjects[i]
			x = x.strip()
			isUnlocked = False
			toBeUnlocked = False
			value = random.randint(0, len(researchableObjects))
			if(value < len(researchableObjects)/ratesOfObjectsUnlocked):
				isUnlocked = True
			if(not isUnlocked):
				value = random.randint(0, len(researchableObjects))
				if(value > len(researchableObjects)/ratesOfObjectsToUnlock):
					toBeUnlocked = True
			line = ''
			if(i != 0):
				line += ','
			line += '{"@type":"ResearchRule","canUnlock":'
			if(toBeUnlocked):
				line += "true"
			else:
				line += "false"
			line += ',"isUnlocked":'
			if(isUnlocked):
				line += "true"
			else:
				line += "false"
			line += ',"name":"' + x + '"}'
			result += line
	return result

def replaceGoals(newData):
	return replaceWithValue('goals":[', newData, randomizeGoals(), "],", offset=getOffset("goals"))

def randomizeGoals():
	result = "["
	nonOptionalGoals = random.randint(1, 4)
	optionalGoals = random.randint(1, 4)
	baseGoals = generateGoals()
	actualGoals = []
	for i in range(0, nonOptionalGoals+optionalGoals):
		goalType = baseGoals[random.randint(0,len(baseGoals)-1)]
		if(goalType["type"] == "NoLoanDebtsGoal"):
			actualGoals.append({"type": goalType["type"]})
		elif(goalType["type"] == "CoastersGoal"):
			coasterCount = random.randint(goalType["coasterCountStart"], goalType["coasterCountEnd"])
			value = randRangeStep(goalType["start"],goalType["stop"])
			actualGoals.append({"type": goalType["type"], "coasterCount": coasterCount, "value": value, "ratingType": goalType["ratingType"]})
		elif(not "step" in goalType):
			value = randRangeStep(goalType["start"],goalType["stop"])
			actualGoals.append({"type": goalType["type"], "value": value})
		else:
			value = randRangeStep(goalType["start"],goalType["stop"],goalType["step"])
			actualGoals.append({"type": goalType["type"], "value": value})

	#REWARDS FOR SOME GOALS
	#REWARDS FOR GOALS THAT HAVE A HIGHER GOAL ELSEWHERE IN THE LIST
	#ADD LOAN DEBT FOR NOLOANDEBTS
	#CHECK CURRENT NUMBER OF GUESTS FOR GUESTGOAL
	#CHECK CURRENT MONEY FOR MONEY
	#CHECK CURRENT RATINGS FOR RATING GOALS
	#DIFFICULTY CURVE

	for i in range(0, nonOptionalGoals+optionalGoals):
		line = ""
		if(i != 0):
			line += ","
		line += '{"@type":"' + actualGoals[i]["type"] + '",'
		if(actualGoals[i]["type"] == "CoastersGoal"):
			line += '"coasterCount":' + str(actualGoals[i]["coasterCount"]) + ','
			line += '"ratingType":"' + str(actualGoals[i]["ratingType"]) + '",'
		if(not actualGoals[i]["type"] == "NoLoanDebtsGoal"):
			line += '"value":' + str(actualGoals[i]["value"]) + ',"isOptional":'
		if(i < nonOptionalGoals):
			line += "false"
		else:
			line += "true"
		line += ',"rewards":[]}'
		result += line

	value = randRangeStep(3300, 17700, 300)
	line = ',{"@type":"TimeGoal","value":' + str(value) + ',"isOptional":true,"rewards":[]}'
	result += line
	return result

def generateGoals():
	goals = [{"type": "ParkExperiencesGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "ParkCleanlinessGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "ParkDecorationGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "ParkHappinessGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "ParkPricesGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "ParkOverallRatingGoal", "start":0.7,"stop":0.95,"step":0.05},
			{"type": "CoastersGoal", "ratingType":"Excitement", "coasterCountStart": 3, "coasterCountEnd": 10, "start":0.5,"stop":0.8,"step":0.05},
			{"type": "CoastersGoal", "ratingType":"Intensity", "coasterCountStart": 3, "coasterCountEnd": 10, "start":0.5,"stop":0.8,"step":0.05},
			{"type": "GuestsInParkGoal", "start":200,"stop":2000,"step":50},
			{"type": "ShopProfitGoal", "start":500,"stop":2000,"step":100},
			{"type": "RideProfitGoal", "start":1000,"stop":5000,"step":250},
			{"type": "OperatingProfitGoal", "start":2000,"stop":8000, "step":500},
			{"type": "MoneyGoal", "start":50000,"stop":150000, "step": 10000},
			{"type": "ParkTicketsGoal", "start":400,"stop":10000, "step":50},
			{"type": "NoLoanDebtsGoal"}]
	return goals

def main():
	baseDirName = os.path.dirname(os.path.abspath(__file__))
	oldDirName = baseDirName + "\\Official Campaign\\Campaign"
	newDirName = baseDirName + "\\Level Pool"
	officialCampaign = getListOfFiles(oldDirName)
	levelPool = getListOfFiles(newDirName)
	usedLevels = {}
			
	for officialLevel in officialCampaign:
		newLevel = getLevel(levelPool, usedLevels)
		printLevel(officialLevel, newLevel)
		usedLevels[newLevel["entry"]] = True
		ungzip(officialLevel)
		ungzip(newLevel)
		newData = switchGuids(officialLevel, newLevel)
		newData = replaceResearch(newData)
		newData = replaceWithValue("isScenario", newData, "true")
		newData = replaceSimpleRandom("maxGuestMultiplicator", newData, 0, 1)
		newData = replaceSimpleRandom("moneyRangeMin", newData, 0, 0.5)
		newData = replaceSimpleRandom("moneyRangeMax", newData, 0.5, 1)
		newData = replaceSimpleRandom("intensityMean", newData, 0, 1)
		newData = replaceSimpleRandom("happinessMultiplicator", newData, 0, 1)
		newData = replaceSimpleRandom("hungerMultiplicator", newData, 0, 1)
		newData = replaceSimpleRandom("thirstMultiplicator", newData, 0, 1)
		newData = replaceSimpleRandom("tirednessMultiplicator", newData, 0, 1)
		newData = replaceSimpleRandom("nauseaMultiplicator", newData, 0, 1)
		newData = replaceWithBoolean("disallowTerraforming", newData, percentageThreshold=75)
		newData = replaceWithBoolean("freeShopProducts", newData, percentageThreshold=90)
		newData = whatToCharge(newData, percentageThreshold=75)
		newData = replaceSimpleRandom("money", newData, 10000, 30000, step=1000)
		newData = replaceSimpleRandom("landTilePrice", newData, 15, 90, step=5)
		newData = replaceSimpleRandom("__timeRestraint", newData, 300, 3600, step=300, separator="}")
		newData = replaceGoals(newData)
		writeToFile(newLevel, newData)

### REFACTOR ###
### CHANGE MONEY SANDBOX POTENTIALLY TO UNLIMITED ###

if __name__ == '__main__':
	main()
