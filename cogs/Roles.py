import discord
import asyncio
import scripts.guild_config as gc
from copy import copy
from discord.ext import commands, tasks


class Roles(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.role_queue = []
        self.add_roles.start()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not await gc.reaction_messages_status(payload.guild_id):
            return
        emoji_roles = await gc.reaction_message_list(payload.guild_id, payload.message_id)
        if not emoji_roles:
            return
        guild = self.client.get_guild(payload.guild_id)
        react_user = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        if react_user.bot:
            return
        roletoassign = guild.get_role(int(emoji_roles[f'{payload.emoji.id}']))
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
        reactions = [reac.emoji for reac in message.reactions]
        desc = 'The following reaction-role pairs were registered with the message.\n\n'
        for n, reaction in enumerate(reactions):
            msg_data[str(reaction.id)] = str(roles[n].id)
            desc += f'{reaction} : {roles[n].mention}\n'
        await gc.reaction_message_set(ctx.guild.id, message.id, msg_data)
        embed = discord.Embed(title='Reaction Roles', description=desc, color=0x6dcded)
        await ctx.send(embed=embed)
        await ctx.message.delete()
        await asyncio.wait_for(message.clear_reactions(), 5)
        for reaction in reactions:
            await message.add_reaction(reaction)

    @commands.command()
    async def disable_rr(self, ctx, message: discord.Message):
        if await gc.reaction_message_remove(ctx.guild.id, message.id):
            await ctx.send('Reaction-Roles disabled for the message.', delete_after=5)
        else:
            await ctx.send('Reaction-Roles not found for the given message.', delete_after=5)
        await ctx.message.delete()


def setup(client):
    client.add_cog(Roles(client))
