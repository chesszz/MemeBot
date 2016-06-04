import discord
from discord.ext import commands

import DebugCommands
import MemeFunctions
import RandomFunctions

import os
import sys
import time
import json
import re

with open("credentials.json", "r") as cred:
    credentials = json.load(cred)

bot = commands.Bot(command_prefix='!', pm_help=True, 
    description="Hi! I am MemeBot created by Chezz and developed using discord.py.")
bot.add_cog(DebugCommands.DebugCommands(bot))
bot.add_cog(MemeFunctions.MemeFunctions(bot, credentials))
bot.add_cog(RandomFunctions.RandomFunctions(bot))

global say_hi 
say_hi = True

curr_dir = os.getcwd()
log_file = os.path.join(curr_dir, time.strftime("logs\\%Y-%m-%d-%H%M.txt"))
# Create the file
with open(log_file, "w") as f:
    pass

########################################################################################
########################################################################################

@bot.event
async def on_message(message):

    ch = message.channel
    msg = message.content.lower()
    
    # It will say hi to the channel when it first logs in, then prevents it from saying hi again
    global say_hi
    if say_hi and message.author.id == credentials["admin_ID"]:
        await bot.send_message(ch, "Hi! {0} has logged in at {1}".format(bot.user.name, 
                            time.strftime("%A, UTC %d %b %Y %H:%M:%S", time.gmtime())))
        say_hi = False

    # If the string contains "aquors" and is NOT preceded by a letter and is NOT followed by a letter 
    # (i.e. is not hidden inside a word), then we correct the person. The letter "s" is optional.
    if re.search(r"(?<![a-zA-Z])aquor(s?)(?![a-zA-Z])", msg) is not None:
        await bot.send_message(ch, "***AQOURS***")

    await bot.process_commands(message)

################################ CLEANING UP #################################

# Use !quit to tell it to quit. Only authorised users can call this command
# Optional arguments after !quit : Provide reasons
@bot.command(pass_context=True)
async def quit(ctx, reason : str = ""):
    """ To kill the bot. You can't use it. """
    if ctx.message.author.id != credentials["admin_ID"]:
        await bot.say("You don't have permission to use this!")
        return

    await bot.say("{0} has gone to sleep at {1}".format(bot.user.name, 
                            time.strftime("%A, GMT %d %b %Y %H:%M:%S", time.gmtime())))

    if reason == "":
        #reason = "To play with Zuikaku"           
        reason = "To update LL Wikia" 

    await bot.say("Reason for quitting: {0}".format(reason))
    
    print("Logged out at {0}".format(time.strftime("%A, %d %b %Y %H:%M:%S")))
    await bot.logout()

################################################################################

@bot.event
async def on_ready():
    print("Logged in at {0}".format(time.strftime("%A, %d %b %Y %H:%M:%S")))
    print("Logged in as {0} with user ID {1}".format(bot.user.name, bot.user.id))
    print("------")
    game = discord.Game(name="Cardfight Vanguard")
    await bot.change_status(game=game)

## MAIN STARTS HERE
with open(log_file, "a", 1) as f:
    sys.stdout = f
    sys.stderr = f
    bot.run(credentials["bot_token"])