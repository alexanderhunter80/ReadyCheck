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
from bson.binary import UuidRepresentation

from ops import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')

bot = commands.Bot(                                                                                                             \
    command_prefix=COMMAND_PREFIX,                                                                                              \
    help_command=None,                                                                                                          \
    description='Interactive ready checks via Discord reactions.',                                                              \
    intents=discord.Intents.default(),                                                                                          \
    allowed_mentions=discord.AllowedMentions(users=True, everyone=True, roles=True, replied_user=True)                          \
)

print(UuidRepresentation.STANDARD)
mongoClient = MongoClient(uuidRepresentation='standard')
db = mongoClient.readycheck

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.debug(f'ID: {bot.user.id}')

###############################
# Commands
###############################

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

    await ctx.message.delete()

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

@bot.command()
async def help(ctx):
    logger.info(f'{ctx.message.author.name} called for help')

    await sendHelpMessage(ctx)

    return

@bot.command()
async def weather(ctx, season: str = None):
    logger.info(f'{ctx.message.author.name} requested weather for season {season}')
    
    await sendWeatherMessage(ctx,season)

    return
    
###############################
# Event listeners
###############################

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

###############################
# Tasks
###############################

timeoutFrequency = int(os.getenv('TIMEOUT_TASK_FREQUENCY_IN_MINUTES'))
timeoutInMinutes = int(os.getenv('TIMEOUT_IN_MINUTES'))
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
# handle ?ready with no arguments - single reactor? default number? refuse and dm user?
# handle ?ready with bad arguments - refuse and dm user?
# include reaction emoji in ready confirmation message
# IAM for users - who can create ready checks?  who can mention certain roles?
# DM users on errors / warnings / weird stuff
# ?help command sends DM with command reference
# ?version command sends DM with version / release / author info
# is role mention finding case sensitive?
###############################

























timeoutChecks.start()
bot.run(TOKEN)