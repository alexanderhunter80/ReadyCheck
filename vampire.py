import random
import math
import log

def validateDice(dice: int, hunger: int, difficulty: int):
    isValid = dice > 0 and hunger >= 0 and difficulty >= 0
    
    return isValid

def rollDice(dicePool: int, hunger: int):
  log.enterMethod(name="rollDice",dicePool=dicePool,hunger=hunger)

  diceRolled = []

  for i in range(0,dicePool):
    if i < hunger:
      diceRolled.append(rollSingleDie(True))
    else:
      diceRolled.append(rollSingleDie(False))

  diceRolled.sort()
  diceRolled.reverse()
  
  log.exitMethod(name="rollDice",diceRolled=diceRolled)
  return diceRolled

def rollSingleDie(isHunger: bool):
  log.enterMethod(name="rollSingleDie",isHunger=isHunger)
  
  roll = random.randint(1,10)
  die = (roll,isHunger)

  log.debug(die=die,isHungerDie=isHungerDie(die),isSuccess=isSuccess(die),
            isTen=isTen(die),isOne=isOne(die))
  
  log.exitMethod(name="rollSingleDie",result=die)
  return die

def isHungerDie(die: tuple):
  log.enterMethod(name="isHungerDie",die=die)

  isHungerDie = False
  if isinstance(die[1], bool):
    isHungerDie = die[1]

  log.exitMethod(name="isHungerDie",isHungerDie=isHungerDie)
  return isHungerDie

def isSuccess(die: tuple):
  log.enterMethod(name="isSuccess",die=die)

  isSuccess = True if die[0] > 5 else False

  log.exitMethod(name="isSuccess",die=die)
  return isSuccess  

def isTen(die: tuple):
  log.enterMethod(name="isTen",die=die)
  
  isTen = True if die[0] == 10 else False

  log.exitMethod(name="isTen",isTen=isTen)
  return isTen

def isOne(die: tuple):
  log.enterMethod(name="isOne",die=die)
  
  isTen = True if die[0] == 1 else False

  log.exitMethod(name="isOne",isOne=isOne)
  return isTen

def assembleResultsDict(diceRolled: list):
  log.enterMethod(name="assembleResultsDict",diceRolled=diceRolled)

  results = {}

  results["diceRolled"] = diceRolled

  rawSuccessCount = 0
  successCount = 0
  failCount = 0
  tenCount = 0
  oneCount = 0
  hungerTenCount = 0
  hungerOneCount = 0
  
  for d in diceRolled:
    if isSuccess(d):
      rawSuccessCount += 1
    else:
      failCount += 1
    if isTen(d):
      tenCount += 1
      if isHungerDie(d):
        hungerTenCount +=1
    if isOne(d):
      oneCount += 1
      if isHungerDie(d):
        hungerOneCount += 1

  successCount = rawSuccessCount + (2 * math.floor(tenCount/2))

  isBestialFailure = True if hungerOneCount > 0 else False
  isCritical = True if tenCount > 1 else False
  isMessyCritical = True if (hungerTenCount > 0 and tenCount > 1) else False

  results["rawSuccessCount"] = rawSuccessCount
  results["successCount"] = successCount
  results["failCount"] = failCount
  results["tenCount"] = tenCount
  results["oneCount"] = oneCount
  results["hungerTenCount"] = hungerTenCount
  results["hungerOneCount"] = hungerOneCount
  results["isBestialFailure"] = isBestialFailure
  results["isCritical"] = isCritical
  results["isMessyCritical"] = isMessyCritical

  log.exitMethod(name="assembleResultsDict",results=results)
  return results

def assembleRollMessage(results: dict, difficulty: int):
  log.enterMethod(name="assembleRollMessage",results=results,difficulty=difficulty)

  message = "Rolled "
  for d in results["diceRolled"]:
    message += str(d[0])
    if d[1]:
      message += "h"
    message += ", "
  message = message[:len(message)-2]
  message += "\n"
  
  message += f"{results['successCount']} hits against difficulty {difficulty}"
  message += "\n"

  margin = results["successCount"] - difficulty
  victory = True if margin > -1 else False
  message += "SUCCESS " if victory else "FAILURE "
  margin = abs(margin)
  message += f"by a margin of {margin}"

  if results["isMessyCritical"] and victory:
    message += "\n"
    message += "MESSY CRITICAL!"
  elif results["isBestialFailure"] and not victory:
    message += "\n"
    message += "BESTIAL FAILURE!"

  print(message)
  
  log.exitMethod(name="assembleRollMessage",message=message)
  return message

def assembleRouseCheckMessage(die: tuple):
  log.enterMethod(name="assembleRouseCheckMessage",die=die)

  value = die[0]

  victory = True if value > 5 else False

  message = "Rolled " + str(value) + "\n"
  message += "SUCCESS: no Hunger increase " if victory else "FAILURE: add 1 Hunger"
  message += "\n"

  log.exitMethod(name="assembleRouseCheckMessage",die=die)
  return message