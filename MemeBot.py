import discord
import random
import os
import time
import pytz
import datetime
import requests
import bs4
import re
import json
from xml.etree import ElementTree

client = discord.Client()

with open("credentials.json", "r") as cred:
    credentials = json.load(cred)

MEMEPATH = r"D:\Qi\Fun\Anime\Reaction Gifs"
NSFWMEMEPATH = os.path.join(MEMEPATH, "NSFW")
FORMATS = ("png", "gif", "jpg")

global say_hi 
say_hi = True

# Generates meme list statically, check that the formats are restricted
# meme_list stores all the memes with extensions
# meme_name_dict stores the pairs of meme names : meme names with extensions so that the user doesn't have to input 
# Only need dict if we allow the user to specify the file that they want

meme_list = [meme for meme in os.listdir(MEMEPATH) if meme[-3:].lower() in FORMATS]
meme_name_dict = {meme.split(".")[0].lower() : meme for meme in meme_list}

nsfw_meme_list = [nsfw_meme for nsfw_meme in os.listdir(NSFWMEMEPATH) if nsfw_meme[-3:].lower() in FORMATS]
nsfw_meme_name_dict = {nsfw_meme.split(".")[0].lower() : nsfw_meme for nsfw_meme in nsfw_meme_list}

towel_meme_list = [towel_meme for towel_meme in meme_list if "towel" in towel_meme]

# For this one, we also strip out the "feelsgood" at the start, so feelsgoodeli.png --> eli
# User can just type !feelsgood eli
feelsgood_list = [feelsgood for feelsgood in meme_list if feelsgood.startswith("feelsgood")]
feelsgood_name_dict = {feelsgood.split(".")[0][9:].lower() : feelsgood for feelsgood in feelsgood_list}


# Takes all timezones and make a dict with the small letter version as the key
all_timezones_dict = {tz.lower() : tz for tz in pytz.all_timezones}

usage = ''' Hi! I am MemeBot created by Chezz and developed using discord.py.

***Commands:***
----------
!helpmeme / !meme help : You already did this.
!hello : Hello!
!ping : Will reply with "pong"
!time <timezone>: Gives the current time in that timezone. <timezone> can be either a number (-12 ~ 12) or a named timezone. Use "!time help" for more information.

!meme [meme_name] : Generates a random meme, with an option to specify a particular meme
!nsfwmeme [meme_name] : Generates a random NSFW meme, with an option to specify a particular meme
!listmemes: Prints a list of all memes possible
!listnsfwmemes : Prines a list of all NSFW memes possible
!towelmeme : Generates a random towel meme
!feelsgood [name]: Generates a random feelsgood meme, with an option to specify a particular member name, e.g. !feelsgood eli

!noobscout : Does an honor scout
!noobscout11 : Does a 10+1 honor scout

!choose <choice1>,<choice2>,<choice3>,... : Choose 1 item from the choices
!choose[n] <choice1>,<choice2>,<choice3>,... : Choose 1 item from the choices, but repeated n times (n<10)
!rank <item1>,<item2>,<item3>,... : Ranks the items among the list
!honk : THIS IS AGAINST THE RULES. YOU WILL GET BANNED.
!!brainpower: Note the 2 exclamation marks. BRAIN POWER~~
!tsun: Copies something from a certain someone's Instagram page
!shigure <searchterm>: Searches for a random anime on MAL and replaces a random word with Shigure
'''

# Macro to print stuff
async def printC(ch, msg):
    return await client.send_message(ch, msg)

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

async def return_named_meme(ch, msg, memelist, namedict, path, err_msg):
    msg_split = msg.split()

    # Gives a random meme if only the main command (e.g . "!meme") is given 
    if len(msg_split) == 1:
        filename = random.choice(memelist)
        await client.send_file(ch, os.path.join(path, filename))

    # Otherwise, if the user has requested a specific one
    # We will only take the first part of msg_split because there are only 2 parts, the command and the filename
    elif len(msg_split) == 2:
        filename = msg_split[1]

        # If the user has specified a full filename with extension, then we simply retrieve that file
        if "." in filename: 
            await client.send_file(ch, os.path.join(path, filename))
        # Otherwise, if the user only gave the name, then we use the dictionary to get the full filename with extension
        else: 
            await client.send_file(ch, os.path.join(path, namedict[filename]))

    # User entered >1 words in the meme name
    else:
        await printC(ch, err_msg) 


@client.event
async def on_message(message):

    ch = message.channel
    msg = message.content.lower()
    msg_or = message.content
    global say_hi

    # It will say hi to the channel when it first logs in, then prevents it from saying hi again
    # Prevents it from responding to itself
    if say_hi and message.author.id == credentials["admin_ID"]:
        await printC(ch, "Hi! MemeBot has logged in at {0}".format(time.strftime("%A, UTC %d %b %Y %H:%M:%S", time.gmtime())))
        say_hi = False


    ### CHOOSES FROM A LIST OF OPTIONS ###
    if msg.startswith("!choose"):
        # Splits based on the first space, we are concerned with the part after. 
        choose, space, after = msg_or.partition(" ")

        try:
            times = int(choose[7:])
            if times > 10:
                times = 10
        except ValueError:
            times = 1

        if after == "":
            await printC(ch, "Error! Input syntax '!choose <choice1>,<choice2>,<choice3>,...'")
        else:
            # Split the choices based on commas
            # When we output, choose 1 and call strip() on it to remove any spaces surrounding it
            choices = after.split(",")
            for _  in range(times):
                await printC(ch, "I chose {0}!".format(random.choice(choices).strip()))

    ### RANKS A LIST OF OPTIONS ###
    if msg.startswith("!rank"):
        # Splits based on the first space, we are concerned with the part after. 
        rank, space, after = msg_or.partition(" ")

        if after == "":
            await printC(ch, "Error! Input syntax '!rank <item1>,<item2>,<item3>,...'")
        else:
            # Split the items based on commas, and then shuffles it
            items = after.split(",")
            random.shuffle(items)

            # Builds the output string
            # Gives the ranking and then the item name stripped of whitespace

            out_str = ""
            for i, item in enumerate(items):
                out_str += "**{0}**. {1}\n".format(i + 1, item.strip())
            await printC(ch, out_str)


    elif msg == "!hello":
        await printC(ch, "Hello {0.mention} onii-sama!".format(message.author))

    # If message ends with \o\ and not sent by MemeBot, we reply the opposite
    elif msg[-3:] == "\\o\\" and message.author != client.user:
        await printC(ch, "/o/")

    elif msg[-3:] == "/o/" and message.author != client.user:
        await printC(ch, "\\o\\")

    # Outputs the current time in either GMT or an aribtrary time zone (can be multiple)
    elif msg.startswith("!time"):

        utc_now = datetime.datetime.utcnow()
        utc_obj = pytz.utc
        utc_now = utc_obj.localize(utc_now)

        if msg == "!time help":
            await printC(ch, "Please refer to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

        # Split the given parameters by spaces
        msg_split = msg.split()

        # Check if we have any parameters given
        # If not, just print the GMT time
        if len(msg_split) == 1:
            await printC(ch, "The time for Etc/GMT is {0}".format(utc_now.strftime("%A, %d %B %Y %I:%M:%S %p")))

        # If we do have timezones, we need to parse them.
        # 2 possible sorts of inputs, either GMT +X/-X numbers, or standard timezone names
        else:
            # Store the list of valid parameters
            # Each parameter will a 2 tuple, 1st entry is the name to print, 2nd entry is the actual timezone object
            timezones = []

            for i in msg_split[1:]:

                # Check if they are in standard timezones. 
                # If so, we just look it up in the dict and get the appropriately capitalised version 
                if i in all_timezones_dict:
                    timezones.append((all_timezones_dict[i],pytz.timezone(all_timezones_dict[i])))

                # If not, it must be an int, because it means GMT +X/-X format input
                else:
                    try:
                        int_i = int(i)
                    except ValueError:
                        print("{0} is not valid".format(i))
                        continue

                    # Workaround because somehow GMT+X makes the time go backward, not sure why
                    # So our printed string and the timezone object are opposite signs
                    tz_str = "Etc/GMT{0:+}".format(-int_i)
                    tz_str_output = "Etc/GMT{0:+}".format(int_i)
                    timezones.append((tz_str_output, pytz.timezone(tz_str)))

            # Print time for each of the timezones
            for tz in timezones:
                await printC(ch, "The time for {0} is {1}".format(tz[0], utc_now.astimezone(tz[1]).strftime("%A, %d %B %Y %I:%M:%S %p")))

        ### HELP MESSAGE ###
    elif msg in ("!helpmeme", "!meme help") or client.user in message.mentions:
        if not str(ch).startswith("Direct Message with"):
            await printC(ch, "{0.mention}, please check your direct message inbox for a list of instructions.".format(message.author))
        await client.send_message(message.author, usage)

    ### LIST OF POSSIBLE MEMES ###
    elif msg == "!listmemes":
        if not str(ch).startswith("Direct Message with"):
            await printC(ch, "{0.mention}, please check your direct message inbox for a list of memes.".format(message.author))
        await printC(message.author, "***The following comands can be used with !meme [meme_name] to show a specific meme.***")
        await printC(message.author, "-----------------------------------------------------------------------------------")
        await printC(message.author, "\n".join(sorted(meme_name_dict.keys())))
        await printC(message.author, "Additional information: You can @mention me or type '!meme help'/'!helpmeme' to get the full list of comamnds")

    ### LIST OF POSSIBLE NSFW MEMES ###
    elif msg == "!listnsfwmemes":
        if not str(ch).startswith("Direct Message with"):
            await printC(ch, "{0.mention}, please check your direct message inbox for a list of NSFW memes.".format(message.author))
        await printC(message.author, "***The following comands can be used with !nsfwmeme [meme_name] to show a specific NSFW meme.***")
        await printC(message.author, "-----------------------------------------------------------------------------------")
        await printC(message.author, "\n".join(sorted(nsfw_meme_name_dict.keys())))
        await printC(message.author, "Additional information: You can @mention me or type '!meme help'/'!helpmeme' to get the full list of comamnds")


    ### GENERATES A RANDOM MEME ###
    elif msg.startswith(("!meme","!maymay")):
        await return_named_meme(ch, msg, memelist=meme_list, namedict=meme_name_dict, path=MEMEPATH, 
                                err_msg="Error! Input syntax '!meme [meme_name]'")

        # msg_split = msg.split()

        # # Gives a random meme if only "!meme" is given 
        # if len(msg_split) == 1:
        #     filename = random.choice(meme_list)
        #     await client.send_file(ch, os.path.join(MEMEPATH, filename))

        # # Otherwise, if the user has requested a specific one
        # elif len(msg_split) == 2:
        #     filename = msg_split[1]
        #     # If the user has specified a full filename with extension, then we simply retrieve that file
        #     if "." in filename: 
        #         await client.send_file(ch, os.path.join(MEMEPATH, filename))
        #     # Otherwise, if the user only gave the name, then we use the dictionary to get the full filename with extension
        #     else: 
        #         await client.send_file(ch, os.path.join(MEMEPATH, meme_name_dict[filename]))
        # else:
        #     await printC(ch, "Error! Input syntax '!meme [meme_name]'")

    ### GENERATES A RANDOM NSFW MEME ###
    elif msg.startswith(("!nsfwmeme","!nsfwmaymay")):
        msg_split = msg.split()

        # Gives a random meme if only "!meme" is given 
        if len(msg_split) == 1:
            filename = random.choice(nsfw_meme_list)
            await client.send_file(ch, os.path.join(NSFWMEMEPATH, filename))

        # Otherwise, if the user has requested a specific one
        elif len(msg_split) == 2:
            filename = msg_split[1]
            # If the user has specified a full filename with extension, then we simply retrieve that file
            if "." in filename: 
                await client.send_file(ch, os.path.join(NSFWMEMEPATH, filename))
            # Otherwise, if the user only gave the name, then we use the dictionary to get the full filename with extension
            else: 
                await client.send_file(ch, os.path.join(NSFWMEMEPATH, nsfw_meme_name_dict[filename]))
        else:
            await printC(ch, "Error! Input syntax '!nsfwmeme [nsfw_meme_name]'")

    ### SENDS A RANDOM FEELSGOOD MEME ###
    elif msg == "!feelsgood":

        filename = random.choice(feelsgood_list)
        await client.send_file(ch, os.path.join(MEMEPATH, filename))

    ### GENERATES A RANDOM TOWEL MEME ###
    elif msg == "!towelmeme":
        meme = random.choice(towel_meme_list)
        await client.send_file(ch, os.path.join(MEMEPATH, meme))

    ### TELLS PEOPLE NOT TO HONK ###
    elif msg == "!honk":
        await client.send_file(ch, os.path.join(MEMEPATH, "dont_honk.jpg"))

    ### PINGS THE BOT ###
    elif msg == "!ping":
        await printC(ch, "pong")

    ### DOES A SINGLE HONOR SCOUT ###
    elif msg == "!noobscout":
        result = scout()
        await printC(ch, "{0.mention}, you drew an {1}!".format(message.author, result))

    ### DOES A 10+1 HONOR SCOUT ###
    elif msg == "!noobscout11":
        results = [scout() for _ in range(10)]
        if all([i == "R" for i in results]):
            results.append(scout2())
        else:
            results.append(scout())

        r_count = results.count("R")
        sr_count = results.count("SR")
        ur_count = results.count("UR")

        await printC(ch, "{0.mention}, you drew R: {1}, SR: {2}, UR: {3}!".format(message.author, r_count, sr_count, ur_count))
        if "UR" in results:
            await printC(ch, "{0.mention} got a UR!!".format(message.author))

    elif msg == "!!brainpower":
        await printC(ch, "おーおおおおおおおおああああえーあーあーいーあーうーじょお - おおおおおおおおおおおおああえーおーあーあーうーうーあーえ - えええーええーえええああああえーあーえーいーえーあーじょおーおおおーおおーおお - おおええええおーあーあああーああああ")

    elif msg == "!tsun":

        # Use requests to get the page, convert to HTML
        # Use BeautifulSoup to parse the HTML and pick out the script tags
        r = requests.get('https://www.instagram.com/tsuntsunlive/')
        html = r.content
        soup = bs4.BeautifulSoup(html, 'html.parser')
        tag_list = soup.find_all("script",type="text/javascript")

        # Find the longest script tag (super primitive and super breakable method....)
        tag_list = [str(tag) for tag in tag_list]
        tag_list = sorted(tag_list, key=len)
        data_tag = tag_list[-1]


        # Each 'caption' means a separate post
        # Chop out the first one because the first one is before the first post
        post_list = re.split('"caption":"', data_tag)[1:]
        post = random.choice(post_list)

        # Find the end of the caption by the start of the next field, "likes"
        caption = post[:re.search('","likes"', post).start()]

        # letters = [letter for letter in caption]

        # for i, letter in enumerate(letters):
        #     if letter == "\\":
        #         letters[i] = "\ud83d"
        #         letters[i+1] = ""
        #         letters[i+2] = ""
        #         letters[i+3] = ""
        #         letters[i+4] = ""
        #         letters[i+5] = ""    
        #         print (i)
        # print (letters)
        # caption = "".join(letters)

        # Remove mu's
        caption = re.sub(r"#\\u03bc's ", "", caption)
        # Remove all other unicode characters of the form "#\u[4 letters/numbers]" and possibly a space
        caption = re.sub(r"#?\\u[0-9a-f]{4} ?", "", caption)

        cap_split = caption.partition("#")
        caption = cap_split[0] + "😍😍😘😘😄😄😃😃😀😀😊😊☺☺😉😉😚😚😗😗😙😙😳😳😣😣😻😻😽😽💛💛💙💙💜💜💚💚❤❤💗💗💓💓💕💕💖💖💞💞💘💘💌💌💋💋" + "".join(cap_split[1:])

        # Find the start of image url by the "display_src" field 
        img_part = post[re.search('"display_src":"', post).end():]
        # Chop off at the "?"  part because after that is some authentication thing
        img = img_part[:re.search("\?", img_part).start()]
        # Remove backslashes
        img = re.sub(r"\\", "", img)

        await printC(ch, img)
        await printC(ch, caption)

    # Searches a random anime on MAL, replaces a random word with Shigure
    elif msg.startswith("!shigure"):
        cmd, space, search = msg.partition(" ")
        if search == "":
            await printC(ch, "Please enter a valid search term.")
            await printC(ch, "Usage: !shigure <any string to be searched on MAL>")

        else:
            base_url="http://myanimelist.net/api/anime/search.xml?q="
            # Takes the search terms, split by space and add "+" instead
            search_plus = "+".join(search.split(" "))

            # Searches on MAL, gets the response and parses the XML obtained
            req = requests.get(base_url + search_plus, auth=(credentials["MAL_user"], credentials["MAL_pass"]))
            tree = ElementTree.fromstring(req.content)

            # Repeat up to 3 times if the anime is 1 word long
            for trial in range(3):
                # Top level is by anime, so we choose a random anime
                anime_choice = random.randrange(len(tree))
                # The [1] refers to the 2nd entry in each anime tag, containing the title
                title = tree[anime_choice][1].text
                # Replace a random word with Shigure
                title_words = title.split(" ")
                # Use this title if it has >1 word title
                if len(title_words) > 1:
                    break

            switch_index = random.randrange(len(title_words))
            title_words[switch_index] = "Shigure"

            await printC(ch, " ".join(title_words))


    # Use !quit to tell it to quit. Only authorised users can call this command
    # Optional arguments after !quit : Provide reasons
    elif msg.startswith("!quit") and message.author.id == credentials["admin_ID"]:
        # Splits by spaces
        quit, space, reason = msg_or.partition(" ")
        await printC(ch, "MemeBot has gone to sleep at {0}".format(time.strftime("%A, GMT %d %b %Y %H:%M:%S", time.gmtime())))
        # If we provided a reason, make it into string by rejoining with spaces in between the args 
        # (that were split by spaces before)
        if reason == "":
            reason = "None"

        await printC(ch, "Reason for quitting: {0}".format(reason))
        await client.logout()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

client.run(credentials["discord_email"], credentials["discord_pass"])