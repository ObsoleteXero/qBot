import discord
from scripts.guild_config import reaction_message_set
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
    async def enable_rr(self, ctx, message: discord.Message, *roles: discord.Role):
        if len(roles) != len(message.reactions):
            raise commands.BadArgument('Mismatch between number of roles and reactions.')
        msg_data = {}
        reactions = message.reactions
        for n, reaction in enumerate(reactions):
            msg_data[str(reaction.id)] = str(roles[n].id)
        await reaction_message_set(ctx.guild.id, message.id, msg_data)
        # await ctx.send('The following Reaction-Role pairs were registered:')
        await message.clear_reactions()
        for reaction in reactions:
            await message.add_reaction(reaction)


def setup(client):
    client.add_cog(Roles(client))
