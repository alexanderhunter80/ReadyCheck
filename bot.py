# bot.py
import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("bot")

import os
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import asyncio
import contextlib
from pymongo import MongoClient
from readycheck import ReadyCheck

from ops import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description='Interactive ready checks via Discord reactions.'
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

bot.trackedMessageId = 0

mongoClient = MongoClient()
db = mongoClient.readycheck

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.debug(f'ID: {bot.user.id}')

# @bot.command()
# async def ready(ctx, count: int):
#     logger.info(f'Ready check called for {count} reactions by {ctx.message.author.name}')
    
#     messageText = f'{ctx.message.author.name} has called for a ready check!  We need {count} reactions to be ready.'

#     checks = db.checks
#     if checks.find_one({"id":ctx.message.id}) is None:
#         checks.insert_one({"id":ctx.message.id})
    
#     await ctx.message.delete()

#     sentMessage = await ctx.send(messageText)
    
#     bot.trackedMessageId = sentMessage.id
#     logger.debug(f'Tracking message {bot.trackedMessageId}')
    
#     def check(reaction, user):
#         logger.debug('Called check function')
#         totalReactions = 0
#         for rx in reaction.message.reactions:
#             totalReactions += rx.count
            
#         logger.debug(f'Standing at {totalReactions} of {count}')
#         return count <= totalReactions
        
#     try:
#         await bot.wait_for('reaction_add', timeout=300.0, check=check)
#     except asyncio.TimeoutError:
#         logger.warn('Timed out!')
#         await sentMessage.delete()
#         await ctx.send('Ready check timed out!')
#     else:
#         await sentMessage.delete()
#         await ctx.send('@everyone Ready!')
        
#     return

@bot.command()
async def ready(ctx, target: int, mention: str = None, uniqueReactors: bool = True):
    logger.info(f'Ready check called for {target} reactions by {ctx.message.author.name}')
    
    checks = db.checks
    checkForConflicts = findUniqueReadyCheck(checks, ctx.message)

    if checkForConflicts is None:
        logger.debug("No conflicts found, continuing")
        await createReadyCheck(ctx, target, mention, uniqueReactors, checks)
    else:
        logger.warning(f'Found conflicting item in database: {checkForConflicts["id"]}')
        logger.debug(f'Conflicting object: {checkForConflicts}')
        # TODO: clear command message and DM user about error

    return

@bot.command()
async def cancel(ctx):
    logger.info(f'Cancel called for {ctx.message.author.name}({ctx.message.author.id})')

    checks = db.checks
    checkToCancel = findUniqueReadyCheck(checks, ctx.message)

    if checkToCancel is not None:
        await removeReadyCheck(bot, checks, checkToCancel)
    else:
        logger.warning("No matching item found in database")
        # TODO: DM user that no check was found

    await ctx.message.delete()

    return

@bot.command()
async def clearAll(ctx):
    adminId = int(os.getenv('GLOBAL_ADMIN_ID'))

    logger.debug(f'Admin id {adminId}')
    logger.debug(f'Calling user id {ctx.message.author.id}')

    if ctx.message.author.id == adminId:
        logger.info(f"Admin {ctx.message.author.name} called to clear all ready checks")
        await clearAllReadyChecks(db.checks)
    else:
        logger.warning("Non-admin user called clearAll!")

    await ctx.message.delete()

    return
    
@bot.event
async def on_raw_reaction_add(payload):
    rc = findReadyCheckByMessageId(db.checks, payload.message_id)
    if rc is None:
        logger.debug("Message not found in database")
        return
    logger.debug("Message found, continuing")

    reactors = await countReactorsToMessage(bot, payload.channel_id, payload.message_id, rc["uniqueReactors"])
    logger.debug("Resolved await on countReactorsToMessage")

    target = int(rc["target"])
    logger.debug(f'Target int: {target}')

    if reactors >= target:
        logger.info(f'ReadyCheck {rc["id"]} is ready!')
        await fulfillReadyCheck(bot, db.checks, rc)
    else:
        logger.debug(f'ReadyCheck {rc["id"]} has registered {reactors} of {target} reactors')

    return


timeoutFrequency = int(os.getenv('TIMEOUT_TASK_FREQUENCY_IN_MINUTES'))
timeoutInMinutes = int(os.getenv('TIMEOUT_IN_MINUTES'))
logger.debug(f'Timeout task: {timeoutFrequency}')
logger.debug(f'Timeout: {timeoutInMinutes}')

@tasks.loop(minutes=timeoutFrequency)
async def timeoutChecks():
    with contextlib.suppress(Exception):
        logger.debug("Running timeout task...")

        await timeoutReadyChecks(bot, db.checks, timeoutInMinutes)

        logger.debug("Timeout task complete")
        return





###############################
# dev notes
###############################
# count reaction authors, not total of reactions (or pass optional flag)
# include reaction emoji in ready confirmation message
#
#
#
###############################

























timeoutChecks.start()
bot.run(TOKEN)
