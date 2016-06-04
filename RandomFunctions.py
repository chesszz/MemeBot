from discord.ext import commands
import random

# Does a scout with 1% UR, 9% SR, 90% R
def scout():
    num = random.random()
    if num < 0.01:
        return "UR"
    elif num < 0.1:
        return "SR"
    else:
        return "R"

def scout2():
    num = random.random()
    if num < 0.1:
        return "UR"
    else:
        return "SR"

class RandomFunctions():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def hello(self, ctx):
        """Hello!"""
        await self.bot.say("Hello {0.mention} onii-sama!".format(ctx.message.author))

    @commands.command()
    async def choose(self, *inputs : str):
        """<choice1>,[choice2],[choice3],... : Choose 1 item from the choices."""
        inputs = " ".join(inputs)
        choices = inputs.split(",")
        # Remove empty items.
        choices = list(filter(lambda x: x != "", choices))
        
        if len(choices) == 0:
            await self.bot.say("Error! Input syntax '!choose <choice1>,<choice2>,<choice3>,...'")
            return

        await self.bot.say("I chose **{0}**!".format(random.choice(choices).strip()))

    @commands.command()
    async def rank(self, *inputs : str):
        """<item1>,[item2],[item3],... : Ranks the items among the list."""
        inputs = " ".join(inputs)
        items = inputs.split(",")
        # Remove empty items.
        items = list(filter(lambda x: x != "", items))

        random.shuffle(items)
        
        if len(items) == 0:
            await self.bot.say("Error! Input syntax '!rank <item1>,<item2>,<item3>,...'")
            return

        # Builds the output string
        # Gives the ranking and then the item name stripped of whitespace
        out_str = ""
        for i, item in enumerate(items):
            out_str += "**{0}**. {1}\n".format(i + 1, item.strip())
        await self.bot.say(out_str)

    @commands.command(pass_context=True)
    async def noobscout(self, ctx):
        """ Does a single honour scout."""
        result = scout()
        await self.bot.say("{0.mention}, you drew an {1}!".format(ctx.message.author, result))

    @commands.command(pass_context=True)
    async def noobscout11(self, ctx):
        """ Does a 10+1 honour scout. """
        results = [scout() for _ in range(10)]
        if all([i == "R" for i in results]):
            results.append(scout2())
        else:
            results.append(scout())

        r_count = results.count("R")
        sr_count = results.count("SR")
        ur_count = results.count("UR")

        await self.bot.say("{0.mention}, you drew R: {1}, SR: {2}, UR: {3}!".format(ctx.message.author, r_count, sr_count, ur_count))
        if "UR" in results:
            await self.bot.say("{0.mention} got a UR!!".format(ctx.message.author))