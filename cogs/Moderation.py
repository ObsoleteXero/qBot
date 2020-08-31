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
        if ctx.author == member:
            await ctx.message.add_reaction('🤔')
            return
        if member.guild_permissions.manage_roles and member.top_role.position > role.position:
            await ctx.send('User cannot be muted', delete_after=5)
            await ctx.message.delete(delay=5)
            raise commands.CommandError('User cannot be muted.')
        await member.add_roles(role, reason='Mute')
        await ctx.send(f'{member} has been muted | {reason}')
        await member.send(f'You have been muted from {ctx.guild.name} for {reason}')
        await ctx.message.delete()
        if time:
            await asyncio.sleep(time)
            await member.remove_roles(role, reason='Lapse of mute')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, time: TimeConverter = None, *, reason=None):
        if ctx.author.top_role.position < member.top_role.position:
            await ctx.send('Cannot ban user', delete_after=5)
            await ctx.message.delete(delay=5)
            raise commands.CommandError('Cannot ban user.')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.top_role.position < member.top_role.position:
            pass
        await member.send(f'You have been kicked from {ctx.guild.name} for {reason}')
        await ctx.send(f'{member} has been kicked from the server | {reason}')
        await ctx.message.delete()


def setup(client):
    client.add_cog(Moderation(client))
