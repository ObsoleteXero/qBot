import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='You | .help'))
    print(f'Bot online. Logged in as {client.user}')

client.run(token)
