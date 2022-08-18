import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("ops")

import os
from dotenv import load_dotenv
from readycheck import ReadyCheck, glimpse
from datetime import datetime, timedelta
import weather as wt
import vampire
import pprint

###############################
# Database methods
###############################

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

###############################
# Command methods
###############################

async def createReadyCheck(ctx, target, mention, uniqueReactors, collection):
    rc = ReadyCheck()
    rc.build(ctx.message, target, mention, uniqueReactors)            

    authorName = ctx.message.author.name

    messageText = f'{authorName} has called a ready check for {rc["target"]} players!  React to this message to signal that you are ready.'

    mentionInMessage = getRoleMentionByName(ctx.message.guild, rc["mention"])

    if mentionInMessage is not None:
        messageText = mentionInMessage+" "+messageText

    sentMessage = await ctx.send(messageText)
    rc["message"] = sentMessage.id

    collection.insert_one(rc)
    logger.debug(f'Inserted {rc["id"]} into checks')  

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

async def clearAllReadyChecks(collection):
    # TODO: loop through and try to delete all associated messages

    result = collection.delete_many({})
    logging.warning(f'Deleted {result.deleted_count} items from database')
    
    return


async def sendHelpMessage(ctx):
    timeoutInMinutes = int(os.getenv('TIMEOUT_IN_MINUTES'))
    commandPrefix = os.getenv('COMMAND_PREFIX')

    msgLines = []

    msgLines.append("```ReadyCheck helps you make sure that your whole group is ready to continue.")
    msgLines.append("Here is a list of ?commands and their [arguments].  Required [arguments] are marked with an *asterisk.")
    msgLines.append("The following commands are available:")
    msgLines.append("\n")
    msgLines.append(f"{commandPrefix}ready [*target] [rolemention] [uniqueReactors]")
    msgLines.append("   Creates a ready check.  Once enough people react to this ready check message, the group will be notified that everyone is ready.")
    msgLines.append("   [*target] (required) - The number of users needed to finish the ready check.")
    msgLines.append("   [rolemention] - The name of a server role (without the @prefix) that will be mentioned when the ready check is started or completed.  Defaults to everyone.")
    msgLines.append("   [uniqueReactors] - If this is false, the ready check will count the raw number of reactions to the message instead of how many users have reacted.  Defaults to true.")
    msgLines.append(f"   Please note that you can only create one reaction per person per channel.  Unfulfilled reactions will time out after {timeoutInMinutes} minutes and be removed.")
    msgLines.append("\n")
    msgLines.append(f"{commandPrefix}cancel")
    msgLines.append("   Cancels an active ready check made by you in this channel.")
    msgLines.append("\n")
    msgLines.append(f"{commandPrefix}help")
    msgLines.append("   Sends you this message.")
    msgLines.append("```")

    helpMessage = "\n".join(msgLines)

    helpUser = ctx.message.author
    channel = await helpUser.create_dm()
    await channel.send(helpMessage)

    return

async def sendWeatherMessage(ctx, season):
    if season is not None:
        msg = wt.generate(season)
    else:
        msg = "Please specify a season."

    await ctx.send(msg)

    return

async def rollVampireDice(ctx, dice: int, hunger: int, difficulty: int):
    if not vampire.validateDice(dice, hunger, difficulty):
        # error message
        await ctx.send("rollVampireDice: generic error message")
        return
    
    diceRolled = vampire.rollDice(dice, hunger)

    results = vampire.assembleResultsDict(diceRolled)

    msg = vampire.assembleRollMessage(results, difficulty)

    await ctx.send(msg)

    return

async def rollVampireRouseCheck(ctx):
    die = vampire.rollSingleDie(False)

    msg = vampire.assembleRouseCheckMessage(die)

    await ctx.send(msg)

    return

###############################
# Event methods
###############################    

async def fulfillReadyCheck(bot, collection, rc):
    channel = await bot.fetch_channel(rc["channel"])
    message = await channel.fetch_message(rc["message"])
    reactions = message.reactions

    messageText = 'Ready!'
    mentionInMessage = getRoleMentionByName(channel.guild, rc["mention"])
    if mentionInMessage is not None:
        messageText = mentionInMessage+" "+messageText

    sentMessage = await channel.send(messageText)

    # TODO: transfer reactions from old message to ready confirmation
    collection.delete_one({"_id":rc["_id"]})
    await message.delete()

    return

###############################
# Task methods
###############################

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

###############################
# Helper methods
###############################

def getRoleMentionByName(guild, name = None):
    roleMention = None
    if name is None:
        roleMention = "@everyone"
    else:
        roles = guild.roles
        for role in roles:
            if role.name == name:
                roleMention = role.mention
                break        

    # TODO: this catches incorrect role names or names of default roles and makes them ping @everyone instead, could be handled better        
    if roleMention is None:  
        roleMention = "@everyone"

    logger.debug(f'Role: {roleMention}')

    return roleMention

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