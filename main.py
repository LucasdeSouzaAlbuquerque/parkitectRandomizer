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
            new_data = new_file.read()
            guid_index = new_data.find("guid")
            new_guid_forward = new_data[guid_index+7:len(new_data)]
            end_guid_index = new_guid_forward.find('",')
            new_data_modified = new_data[:guid_index+7] + guid + new_data[guid_index+7+end_guid_index:]
            return new_data_modified

def writeToFile(newLevel, data):
    f_out = gzip.open('New Campaign/Campaign/'+newLevel["entry"], 'wb')
    byteData = bytes(data, 'utf-8')
    f_out.write(byteData)
    f_out.close()

def printLevel(officialLevel, newLevel):
    print(officialLevel["entry"] + " -> " + newLevel["entry"])
    
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
        writeToFile(newLevel, newData)

def replaceResearch(new_data):
    newResearch = randomizeResearch()
    rules_index = new_data.find("rules")
    rules_forward = new_data[rules_index+8:len(new_data)]
    end_rules_index = rules_forward.find('],')
    new_data_modified = new_data[:rules_index+8] + newResearch + new_data[rules_index+8+end_rules_index:]
    return new_data_modified

def randomizeResearch():
    result = ""
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

'''
LINE 1

file["scenario"]["goals"]["goals"]: list

{"@type":"ParkExperiencesGoal","value":0.6684032,"isOptional":false,"rewards":[]},
{"@type":"ParkCleanlinessGoal","value":0.7517365,"isOptional":false,"rewards":[
{"@type":"CoastersGoal","coasterCount":2,"minimumRatingValue":0.81,"isOptional":false,"rewards":[],"ratingType":"Intensity"},
{"@type":"CoastersGoal","coasterCount":5,"minimumRatingValue":0.6,"isOptional":false,"rewards":[],"ratingType":"Excitement"},
{"@type":"ParkDecorationGoal","value":0.7934032,"isOptional":false,"rewards":[]},
{"@type":"GuestsInParkGoal","value":800,"isOptional":false,"rewards":[]},
{"@type":"NoLoanDebtsGoal","isOptional":false,"rewards":[]},
{"@type":"ShopProfitGoal","value":500.,"isOptional":false,"rewards":[]},
{"@type":"RideProfitGoal","value":1000.,"isOptional":false,"rewards":[]},
{"@type":"OperatingProfitGoal","value":2000.,"isOptional":false,"rewards":[]},
{"@type":"MoneyGoal","value":50000.,"isOptional":false,"rewards":[]},
{"@type":"ParkOverallRatingGoal","value":0.5,"isOptional":false,"rewards":[]},
{"@type":"ParkTicketsGoal","value":2000,"isOptional":false,"rewards":[]},
{"@type":"ParkPricesGoal","value":0.5,"isOptional":false,"rewards":[]},
{"@type":"ParkHappinessGoal","value":0.5,"isOptional":true,"rewards":[]},
{"@type":"TimeGoal","value":3300,"isOptional":true,"rewards":[]}],"__timeRestraint":3600}




file["isScenario"] -> true
file["parkSettings"]["maxGuestMultiplicator"]
file["parkSettings"]["moneyRangeMin"]
file["parkSettings"]["moneyRangeMax"]
file["parkSettings"]["intensityMean"]
file["parkSettings"]["happinessMultiplicator"]
file["parkSettings"]["hungerMultiplicator"]
file["parkSettings"]["thirstMultiplicator"]
file["parkSettings"]["tirednessMultiplicator"]
file["parkSettings"]["nauseaMultiplicator"]
file["parkSettings"]["disallowTerraforming"]
file["parkSettings"]["cantChangeParkEntranceFee"]
file["parkSettings"]["freeRideEntranceFees"]
file["parkSettings"]["freeShopProducts"]
file["parkSettings"]["globalHeightRestriction"]

file["parkInfo"]["money"]
file["parkInfo"]["parkEntranceFee"]
file["parkInfo"]["landTilePrice"]
file["parkInfo"]["loanController"]["loanPlans"]: list

{"@type":"LoanPlan","bankIndex":7,"amount":4000.,"interest":0.008,"months":22,"isActive":false,"paidAmount":0.,"appearedTime":0}

'''

if __name__ == '__main__':
    main()
