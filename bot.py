import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='You'))
    print(f'Bot online. Logged in as {client.user}')


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} loaded')
    await ctx.message.delete(delay=5)


@load.error
async def load_error(ctx, error):
    await ctx.message.add_reaction('❌')
    await ctx.message.delete(delay=5)


@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} unloaded')
    await ctx.message.delete(delay=5)


@unload.error
async def unload_error(ctx, error):
    await ctx.message.add_reaction('❌')
    await ctx.message.delete(delay=5)


@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')
    await ctx.message.add_reaction('✅')
    print(f'{extension} reloaded')
    await ctx.message.delete(delay=5)


@reload.error
async def reload_error(ctx, error):
    await ctx.message.add_reaction('❌')
    await ctx.message.delete(delay=5)


for file in os.listdir('./cogs'):
    if file.endswith('.py'):
        client.load_extension(f'cogs.{file[:-3]}')
        print(f'{file[:-3]} Loaded')

client.run(token)
