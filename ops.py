import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("ops")

from readycheck import ReadyCheck, glimpse
from datetime import *

def findUniqueReadyCheck(collection, message):
    # ReadyCheck items should always be limited to one per user per channel
    result = collection.find_one({            \
            "author":message.author.id,     \
            "guild":message.guild.id,       \
            "channel":message.channel.id    \
    })

    return result

def findReadyCheckByMessageId(collection, id):
    return collection.find_one({"message":id})

async def createReadyCheck(ctx, target, mention, uniqueReactors, collection):
    rc = ReadyCheck()
    rc.build(ctx.message, target, mention, uniqueReactors)            

    authorName = ctx.message.author.name
    mentionPrefix = "@everyone" if rc["mention"] is None else ("@"+rc["mention"])
    messageText = f'{mentionPrefix} {authorName} has called a ready check for {rc["target"]} players!  React to this message to signal that you are ready.'

    # TODO: properly get and send role mention

    await ctx.message.delete()
    sentMessage = await ctx.send(messageText)
    rc["message"] = sentMessage.id

    collection.insert_one(rc)
    logger.debug(f'Inserted {rc["id"]} into checks')  

    return  

async def clearAllReadyChecks(collection):
    # TODO: loop through and try to delete all associated messages

    result = collection.delete_many({})
    logging.warning(f'Deleted {result.deleted_count} items from database')
    
    return

async def countReactorsToMessage(bot, channelId, messageId, uniqueReactors):
    channel = await bot.fetch_channel(channelId)
    message = await channel.fetch_message(messageId)

    logger.debug(f'Message retrieved: {message.id}')

    if uniqueReactors is True:
        logger.debug("uniqueReactors is true, counting reactions per person")
        reactors = set()
        for r in message.reactions:
            logger.debug(f'Reaction: {r.emoji}')
            rlist = await r.users().flatten()
            for user in rlist:
                logger.debug(f'User: {user.name}')
                reactors.add(user.id)
        reactorsCount = len(reactors)
    elif uniqueReactors is False:
        logger.debug("uniqueReactors is false, counting total reactions")
        reactorsCount = 0
        for r in message.reactions:
            reactorsCount += r.count
    else:
        raise TypeError("uniqueReactors was not a boolean")

    logger.debug(f'Counted {reactorsCount} total reactors')

    return reactorsCount

async def fulfillReadyCheck(bot, collection, rc):
    channel = await bot.fetch_channel(rc["channel"])
    message = await channel.fetch_message(rc["message"])
    reactions = message.reactions

    messageText = f'@{rc["mention"]} Ready!'
    # TODO: properly get and send role mention

    sentMessage = await channel.send(messageText)

    # TODO: transfer reactions from old message to ready confirmation
    collection.delete_one({"_id":rc["_id"]})
    await message.delete()

    return

async def timeoutReadyChecks(bot, collection, timeoutInMinutes):
    readyChecks = collection.find()
    for rc in readyChecks:
        rcg = glimpse(rc)
        logger.debug(f'Item: {rcg}')
        createdAt = rc["createdAt"]
        timeout = createdAt + timedelta(minutes=timeoutInMinutes)
        if datetime.utcnow() > timeout:
            logger.info(f'Timeout: {rc["id"]} created by {rc["authorLastKnownName"]} in {rc["guildLastKnownName"]} / {rc["channelLastKnownName"]} at {createdAt.strftime("%Y-%m-%d %H:%M:%S")} UTC')
            await removeReadyCheck(bot, collection, rc)

    return

async def removeReadyCheck(bot, collection, rc):
    try:
        channel = await bot.fetch_channel(rc["channel"])
        message = await channel.fetch_message(rc["message"])
        await message.delete()
    except Exception as e:
        logger.error(e)

    collection.delete_one({"id":rc["id"]})

    rcg = glimpse(rc)
    logger.debug(f'Removed {rcg}')

    return
