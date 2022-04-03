import helper
import log
import random

def generate(season):
  log.printDebug("entering generate")
  
  temp = generateTemp(season)
  sky = generateSky(helper.checkCold(temp))
  wind = generateWind()

  log.printDebug("exiting generate")

  return printConditions(season, temp, sky, wind)

def generateTemp(season):
  log.printDebug("entering generateTemp")
  
  temp = random.choice(helper.generateWeightedTempList(season))
  tempMod = helper.getTempModifierMap()[temp]
  result = (temp, tempMod)
  
  log.printDebug(result)
  log.printDebug("exiting generateTemp")
  return result

def generateSky(isCold):
  log.printDebug("entering generateSky")

  result = random.choice(helper.generateWeightedSkiesList(isCold))

  log.printDebug("exiting generateSky")
  return result

def generateWind():
  log.printDebug("entering generateWind")

  windSpeed = random.choice(helper.generateWeightedWindSpeedList())
  windDir = random.choice(helper.getWindDirectionList())
  result = (windDir, windSpeed)

  log.printDebug("exiting generateWind")
  return result

def printConditions(season, temp, sky, wind):
  # temp version, will prettyPrint later
  # check for extra rules for cold/hot/wind and print here
  seasonMessage = helper.getSeasonMessage(season)
  windMod = int((wind[1] / 2))
  shelterMod = temp[1] + sky[1] + windMod

  conditions = seasonMessage + "\n" + \
  f"Today's temperature: {temp[0]}, +{temp[1]}" + "\n" + \
  f"Today's weather: {sky[0]}, +{sky[1]}" + "\n" + \
  f"Today's wind: {wind[0]} {wind[1]}kts, +{windMod}" + "\n" + \
  f"Shelter DC: {shelterMod}" + "\n"

  print(conditions)

  return conditions
  

def testRun():
  #helper.generateWeightedTempList("heatWave")
  #helper.generateWeightedTempList("summer")
  #helper.generateWeightedTempList("springFall")
  #helper.generateWeightedTempList("winter")
  #helper.generateWeightedTempList("coldSnap")
  #helper.getTempModifierMap()
  #helper.generateWeightedSkiesList(True)
  #helper.generateWeightedSkiesList(False)
  #helper.generateWeightedWindSpeedList()
  #helper.getWindDirectionList()
  pass