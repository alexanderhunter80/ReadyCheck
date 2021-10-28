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

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description='Interactive ready checks via Discord reactions.'
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

bot.trackedMessageId = 0

client = MongoClient()
db = client.readycheck

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.debug(f'ID: {bot.user.id}')

@bot.command()
async def ready(ctx, count: int):
    logger.info(f'Ready check called for {count} reactions by {ctx.message.author.name}')
    
    messageText = f'{ctx.message.author.name} has called for a ready check!  We need {count} reactions to be ready.'

    checks = db.checks
    if checks.find_one({"id":ctx.message.id}) is None:
        checks.insert_one({"id":ctx.message.id})
    
    await ctx.message.delete()

    sentMessage = await ctx.send(messageText)
    
    bot.trackedMessageId = sentMessage.id
    logger.debug(f'Tracking message {bot.trackedMessageId}')
    
    def check(reaction, user):
        logger.debug('Called check function')
        totalReactions = 0
        for rx in reaction.message.reactions:
            totalReactions += rx.count
            
        logger.debug(f'Standing at {totalReactions} of {count}')
        return count <= totalReactions
        
    try:
        await bot.wait_for('reaction_add', timeout=300.0, check=check)
    except asyncio.TimeoutError:
        logger.warn('Timed out!')
        await sentMessage.delete()
        await ctx.send('Ready check timed out!')
    else:
        await sentMessage.delete()
        await ctx.send('@everyone Ready!')
        
    return

# @bot.command()
# async def ready(ctx, target: int, mention: str):
#     print(f'Ready check called for {count} reactions by {ctx.message.author.name}')

#     pass

# @bot.command()
# async def cancel(ctx):
#     # grab user-guild-channel combo and cancel any active readychecks that match (enforce one check per user per channel)
#     pass
    
# @bot.event()
# async def on_raw_reaction_add(reaction, user):
#     # check if reaction.message.id is in db, if so then check against reaction count to fulfill ready check
#     pass

# @tasks.loop(minutes=5)
# async def timeoutChecks():
#     with contextlib.suppress(Exception):
#         # remove timed out tasks from database
#         pass





###############################
# dev notes
###############################
# count reaction authors, not total of reactions (or pass optional flag)
# include reaction emoji in ready confirmation message
#
#
#
###############################

























# timeoutChecks.start()
bot.run(TOKEN)
