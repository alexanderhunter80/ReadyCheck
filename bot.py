# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description='Interactive ready checks via Discord reactions.'
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

bot.trackedMessageId = 0

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'ID: {bot.user.id}')

@bot.command()
async def ready(ctx, count: int):
    print(f'Ready check called for {count} reactions by {ctx.message.author.name}')
    
    messageText = f'{ctx.message.author.name} has called for a ready check!  We need {count} reactions to be ready.'
    
    await ctx.message.delete()

    sentMessage = await ctx.send(messageText)
    
    bot.trackedMessageId = sentMessage.id
    print(f'Tracking message {bot.trackedMessageId}')
    
    def check(reaction, user):
        print('Called check function')
        totalReactions = 0
        for rx in reaction.message.reactions:
            totalReactions += rx.count
            
        print(f'Standing at {totalReactions} of {count}')
        return count <= totalReactions
        
    try:
        await bot.wait_for('reaction_add', timeout=300.0, check=check)
    except asyncio.TimeoutError:
        print('Timed out!')
        await sentMessage.delete()
        await ctx.send('Ready check timed out!')
    else:
        await sentMessage.delete()
        await ctx.send('@everyone Ready!')
        
        
        
    return
    


# count reaction authors, not total of reactions (or pass optional flag)
# include reaction emoji in ready confirmation message






























bot.run(TOKEN)
