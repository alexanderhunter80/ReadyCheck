import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("readycheck")

from discord import Message
from collections.abc import MutableMapping
import uuid
from datetime import datetime

class ReadyCheck(MutableMapping):
    def __init__(self, data=()):
        self.mapping = {}
        self.mapping["id"] = uuid.uuid4()
        self.mapping["input"] = None
        self.mapping["mention"] = None
        self.mapping["message"] = None
        self.mapping["target"] = None
        self.mapping["author"] = None
        self.mapping["guild"] = None
        self.mapping["channel"] = None
        self.mapping["authorLastKnownName"] = None
        self.mapping["guildLastKnownName"] = None
        self.mapping["channelLastKnownName"] = None
        self.mapping["uniqueReactors"] = True
        self.mapping["createdAt"] = datetime.utcnow()
        self.mapping["updatedAt"] = datetime.utcnow()
        self.update(data)

    def __getitem__(self, key):
        return self.mapping[key]

    def __delitem__(self, key):
        del self.mapping[key]

    def __setitem__(self, key, value):
        self.mapping[key] = value
        
    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return f'{type(self).__name__}({self.mapping})'

    def build(self, message, target, mention, uniqueReactors):
        self.mapping["input"] = message.content
        self.mapping["target"] = target
        self.mapping["mention"] = mention
        self.mapping["author"] = message.author.id
        self.mapping["guild"] = message.guild.id
        self.mapping["channel"] = message.channel.id
        self.mapping["authorLastKnownName"] = message.author.name
        self.mapping["guildLastKnownName"] = message.guild.name
        self.mapping["channelLastKnownName"] = message.channel.name
        self.mapping["uniqueReactors"] = uniqueReactors
        self.mapping["updatedAt"] = datetime.utcnow()
        logger.debug("Built "+glimpse(self))
        return self

def glimpse(rc):
    return f'ReadyCheck: {rc["authorLastKnownName"]} in {rc["guildLastKnownName"]} / {rc["channelLastKnownName"]}'