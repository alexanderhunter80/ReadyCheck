import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("ops")

from readycheck import ReadyCheck

def findUniqueReadyCheck(collection, message):
    # ReadyCheck items should always be limited to one per user per channel
    return collection.find_one({            \
            "author":message.author.id,     \
            "guild":message.guild.id,       \
            "channel":message.channel.id    \
    })

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
    
async def cancelReadyCheck(bot, collection, checkToCancel):
    collection.delete_one({"_id":checkToCancel["_id"]})
    logger.info("Deleted one item from database")

    channel = await bot.fetch_channel(checkToCancel["channel"])
    message = await channel.fetch_message(checkToCancel["message"])
    await message.delete()    

    return

async def clearAllReadyChecks(collection):
    # TODO: loop through and try to delete all associated messages

    result = collection.delete_many({})
    logging.warn(f'Deleted {result.deleted_count} items from database')
    
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