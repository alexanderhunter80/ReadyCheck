import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("readychecktest")

from readycheck import ReadyCheck

rdy = ReadyCheck()

rdy.input = "input message"
rdy.mention = "Hades"
rdy.message = 1
rdy.target = 3
rdy.author = 1
rdy.guild = 1

jsonObject = rdy.toJson()

rdy2 = ReadyCheck()

rdy2.fromJson(jsonObject)