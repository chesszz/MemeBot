from discord.ext import commands

class DebugCommands():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self):
        """Used to test if the bot is awake."""
        await self.bot.say("pong")

    @commands.command()
    async def pong(self):
        """Alternative command to test if the bot is awake."""
        await self.bot.say("ping")