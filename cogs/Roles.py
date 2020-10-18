import discord
from scripts.guild_config import reaction_roles_add, reaction_roles_remove
from copy import copy
from discord.ext import commands, tasks

role_react_messages = []
emoji_roles = {}


class Roles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.role_queue = []
        self.add_roles.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id not in role_react_messages:
            return
        guild = self.client.get_guild(payload.guild_id)
        react_user = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        roletoassign = discord.utils.get(guild.roles, name=emoji_roles[f'{payload.emoji.name}'])
        react_channel = guild.get_channel(payload.channel_id)
        react_message = await react_channel.fetch_message(payload.message_id)
        await react_message.remove_reaction(payload.emoji, react_user)
        if roletoassign in react_user.roles:
            return
        else:
            self.role_queue.append((react_user, roletoassign))

    @tasks.loop(seconds=1)
    async def add_roles(self):
        if not self.role_queue:
            return
        working_copy = copy(self.role_queue)
        for user, role in working_copy:
            await user.add_roles(role)
            self.role_queue.remove((user, role))

    @commands.command()
    async def add_rr(self, ctx, reaction: discord.PartialEmoji, role: discord.Role):
        response = await reaction_roles_add(ctx.guild.id, reaction.id, role.id)
        if response:
            await ctx.send('Rection-Role pair added.', delete_after=5)
        else:
            await ctx.send('Rection-Role already exists.', delete_after=5)

    @commands.command()
    async def remove_rr(self, ctx, reaction: discord.PartialEmoji):
        response = await reaction_roles_remove(ctx.guild.id, reaction.id)
        if response:
            await ctx.send('Rection-Role pair removed.', delete_after=5)
        else:
            await ctx.send('Rection-Role pair does not exist.', delete_after=5)


def setup(client):
    client.add_cog(Roles(client))
