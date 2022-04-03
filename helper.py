import log

def generateWeightedTempList(season):
    log.printDebug("entering generateWeightedTempList")

    tempSource = open("csv/temps.csv")
    tempList = []

    for line in iter(tempSource.readline, ''):
        if not line.startswith(season):
            continue

        lineList = line.strip().split(',')
        log.printDebug(lineList)

        for i in range(1, len(lineList), 2):
            conditionName = lineList[i]
            i += 1
            conditionWeight = lineList[i]
            log.printDebug("read: " + conditionName + ", " + conditionWeight)
            for j in range(int(conditionWeight)):
                tempList.append(conditionName.strip())

        break

    log.printDebug(tempList)
    log.printDebug("exiting generateWeightedTempList")
    return tempList


def getTempModifierMap():
    log.printDebug("entering getTempModifierMap")

    source = open("csv/temps.csv")
    tempMap = {}

    tempList = source.readline().strip().split(',')

    for i in range(1, len(tempList), 2):
        tempMap[tempList[i]] = int(tempList[i + 1])

    log.printDebug(tempMap)
    log.printDebug("exiting getTempModifierMap")
    return tempMap


def generateWeightedSkiesList(isCold):
    log.printDebug("entering generateWeightedSkiesList")

    source = open("csv/skies.csv")
    skyList = []

    if isCold:
        source.readline()

    lineList = source.readline().strip().split(',')

    for i in range(1, len(lineList), 3):
        weatherName = lineList[i]
        weatherMod = lineList[i + 1]
        weatherWeight = lineList[i + 2]
        log.printDebug("read: " + weatherName + ", " + weatherMod + ", " +
                   weatherWeight)
        for j in range(int(weatherWeight)):
            skyList.append((weatherName, int(weatherMod)))

    log.printDebug(skyList)
    log.printDebug("exiting generateWeightedSkiesList")
    return skyList


def generateWeightedWindSpeedList():
    log.printDebug("entering generateWeightedWindSpeedList")

    source = open("csv/wind.csv")
    windList = []

    lineList = source.readline().strip().split(',')

    for i in range(1, len(lineList), 2):
        windSpeed = lineList[i]
        i += 1
        windWeight = lineList[i]
        log.printDebug("read: " + windSpeed + ", " + windWeight)
        for j in range(int(windWeight)):
            windList.append(int(windSpeed))

    log.printDebug(windList)
    log.printDebug("exiting generateWeightedWindSpeedList")
    return windList


def getWindDirectionList():
    log.printDebug("entering getWindDirectionList")

    source = open("csv/wind.csv")
    dirList = []

    source.readline()
    dirList = source.readline().strip().split(',')
    dirList.pop(0)

    log.printDebug(dirList)
    log.printDebug("exiting getWindDirectionList")
    return dirList


def checkCold(temp):
  log.printDebug("entering checkCold")

  tempName = temp[0]
  if tempName == "bitter" or tempName == "cold":
    result = True
  else :
    result = False

  log.printDebug(result)
  log.printDebug("exiting checkCold")
  return result

def getSeasonMessage(season):
  log.printDebug("entering getSeasonMessage")

  source = open("csv/seasons.csv")

  for line in iter(source.readline, ''):
      if not line.startswith(season):
          continue  

      lineList = line.strip().split(',')
      result = lineList[1]

  log.printDebug(result)
  log.printDebug("exiting getSeasonMessage")
  return result