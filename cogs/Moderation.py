import re
import discord
import asyncio
from discord.ext import commands

time_regex = re.compile(r'(\d+)(d|h|m)', re.I)
time_dict = {"h": 3600, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(f'{k} is an invalid time-key! h/m/d are valid!')
            except ValueError:
                raise commands.BadArgument(f'{v} is not a number!')
        return time


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, time: TimeConverter = None, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        await member.add_roles(role, reason='Mute')
        await ctx.send(f'{member} has been muted | {reason}')
        await ctx.message.delete()
        if time:
            await asyncio.sleep(time)
            await member.remove_roles(role, reason='Lapse of mute')


def setup(client):
    client.add_cog(Moderation(client))
