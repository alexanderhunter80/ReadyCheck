doInfo = True
doDebug = False
doTrace = False

def printFancy(kwargs):
  print()
  print("-----")
  for i,j in kwargs.items():
    print(f"--{i}={j}")
  print("-----")
  print()
  return

def info(**kwargs):
  if not doInfo:
    return
  printFancy(kwargs=kwargs)
  return

def printInfo(msg):
  if not doInfo:
    return  
  print(msg)
  return  

def debug(**kwargs):
  if not doDebug:
    return
  printFancy(kwargs=kwargs)
  return

def printDebug(msg):
  if not doDebug:
    return  
  print(msg)
  return

def enterMethod(**kwargs):
  if not doTrace:
    return
  print()
  print("-----")
  print("--Entering method")
  for i,j in kwargs.items():
    print(f"--{i}={j}")
  print("-----")
  print()
  return

def exitMethod(**kwargs):
  if not doTrace:
    return
  print()
  print("-----")
  print("--Exiting method")
  for i,j in kwargs.items():
    print(f"--{i}={j}")
  print("-----")
  print()
  return