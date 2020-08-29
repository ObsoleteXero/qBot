import discord
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.ExtensionError):
            await ctx.message.add_reaction('❌')
            await ctx.message.delete(delay=5)

        if isinstance(error, commands.NotOwner):
            await ctx.send('Only the bot owner can use that command.', delete_after=5)
            await ctx.message.delete(delay=5)
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the required permissions for this command.', delete_after=5)
            await ctx.message.delete(delay=5)

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send('Command failed; Insufficient Permissions.', delete_after=5)
            await ctx.message.delete(delay=5)

        log_channel = self.client.get_channel(731880960832045156)
        embed = discord.Embed(description=f'**User:** {ctx.author}\n**Command:** {ctx.message.content}\n**Error:** '
                                          f'```py\n{error}```')
        await log_channel.send(embed=embed)


def setup(client):
    client.add_cog(CommandErrorHandler(client))
