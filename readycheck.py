import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("readycheck")

from discord import Message
import jsonpickle
import uuid
from datetime import datetime

class ReadyCheck(object):
    def __init__(self):
        id = uuid.uuid4()
        input = None
        mention = None
        message = None
        target = None
        author = None
        guild = None
        createdAt = datetime.utcnow()
        updatedAt = datetime.utcnow()

    def build(self, message, target, mention):
        self.input = message.content
        self.target = target
        self.mention = "@"+mention
        self.author = message.author.id
        self.guild = message.guild.id
        self.updatedAt = datetime.utcnow()

    def toJson(self):
        logger.debug('Transforming to JSON:')
        logger.debug(self)
        result = jsonpickle.encode(self)
        logger.debug(result)
        return result

    def fromJson(self, json):
        logger.debug('Rebuilding from JSON:')
        logger.debug(json)
        unpickled = jsonpickle.decode(json)
        self = unpickled
        logger.debug(self)
        return self
