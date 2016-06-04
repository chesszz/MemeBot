from discord.ext import commands
import os
import time
import random
import requests
import bs4
import codecs
import re
from xml.etree import ElementTree

MEMEPATH = r"D:\Qi\Fun\Anime\Reaction Gifs"
NSFWMEMEPATH = os.path.join(MEMEPATH, "NSFW")
FORMATS = ("png", "gif", "jpg")
inform_msg = "{0.mention}, please check your direct message inbox."

def generate_memelists(path):
    # Generates meme list statically, check that the formats are restricted
    # meme_list stores all the memes with extensions
    # meme_name_dict stores the pairs of meme names : meme names with extensions so that the user doesn't have to input 
    # Only need dict if we allow the user to specify the file that they want

    meme_list = [meme for meme in os.listdir(path) if meme[-3:].lower() in FORMATS]

    meme_name_dict = {meme.split(".")[0].lower() : meme for meme in meme_list}

    # Stores the filename and the time modified 
    meme_list_mod = [[filename, time.time() -  os.stat(os.path.join(path, meme_name_dict[filename])).st_mtime] for filename in meme_name_dict]
    # Splits into 2 lists, old and new. The cutoff is 3 days from now.
    # New memes have the :new: tag added
    meme_list_old = [file for file in meme_list_mod if file[1] > 3600*24*3]
    meme_list_new = [[(file[0] + " :new:"), file[1]] for file in meme_list_mod if file[1] <= 3600*24*3]

    # Sort old memes by name, new memes by time
    # Combine the list together
    meme_list_old.sort(key=lambda x: x[0])
    meme_list_new.sort(key=lambda x: x[1])
    meme_list_mix = [file[0] for file in meme_list_new] + [file[0] for file in meme_list_old]

    return meme_list, meme_name_dict, meme_list_mix

async def return_named_meme(meme_name, memelist, namedict, path, err_msg):

    # Gives a random meme if only the main command (e.g . "!meme") is given 
    if meme_name == "":
        filename = random.choice(memelist)
        return os.path.join(path, filename)
        # await client.send_file(ch, fp=os.path.join(path, filename))

    # Otherwise, if the user has requested a specific one...
    elif meme_name in namedict:
        return os.path.join(path, namedict[meme_name])
    # Not found.
    else:
        return None

        # # If the user has specified a full filename with extension, then we simply retrieve that file
        # if "." in filename: 
        #     await client.send_file(ch, fp=os.path.join(path, filename))
        # # Otherwise, if the user only gave the name, then we use the dictionary to get the full filename with extension
        # else: 
        #     await client.send_file(ch, fp=os.path.join(path, namedict[filename]))

########################################################################################
########################################################################################

meme_list, meme_name_dict, meme_list_mix = generate_memelists(MEMEPATH)
nsfw_meme_list, nsfw_meme_name_dict, nsfw_meme_list_mix = generate_memelists(NSFWMEMEPATH)
towel_meme_list = [towel_meme for towel_meme in meme_list if "towel" in towel_meme]

# For this one, we also strip out the "feelsgood" at the start, so feelsgoodeli.png --> eli
# User can just type !feelsgood eli
feelsgood_list = [feelsgood for feelsgood in meme_list if feelsgood.startswith("feelsgood")]
feelsgood_name_dict = {feelsgood.split(".")[0][9:].lower() : feelsgood for feelsgood in feelsgood_list}

################################ CORE MEME FUNCTIONALITY #################################

class MemeFunctions():
    def __init__(self, bot, credentials):
        self.bot = bot
        self.credentials = credentials

    ### GENERATES AND SENDS A RANDOM MEME ###
    async def send_meme(self, meme_name, memelist, namedict, path, err_msg):
        meme = await return_named_meme(meme_name, memelist, namedict, path, err_msg)

        if meme is None:
            await self.bot.say("Meme \"{0}\" not found.".format(meme_name))
        else:
            await self.bot.upload(meme)

    # Sends a given memelist to a certain user. Needed because of the 2000-character message limit.
    # memelist is a list of names.
    # user is a User object, usually obtained from message.author
    async def send_memelist(self, user, memelist):
        memelist_str_length = len(str(memelist))    # Length of all the strings in the list
        memelist_length = len(memelist)             # Number of entries in the list

        pieces = memelist_str_length // 2000 + 1    # Split into blocks of 2000 characters
        piece_length = memelist_length // pieces    # Use this number and split the indices accordingly

        for num in range(pieces):
            # Last piece may not have a nice round number and so will slice till end of string
            # Other pieces slice based on the piece length
            if num == (pieces - 1):
                await self.bot.send_message(user, "\n".join(memelist[num * piece_length:]))
            else:
                await self.bot.send_message(user, "\n".join(memelist[num * piece_length:(num + 1) * piece_length]))


    ### LIST OF POSSIBLE MEMES ###
    @commands.command(pass_context=True)
    async def listmemes(self, ctx):
        """Prints a list of all memes."""
        # If not in PM already, tells the user to look at his PM box
        if not ctx.message.channel.is_private:
            await self.bot.say(inform_msg.format(ctx.message.author))
            await self.bot.say("*New feature! !listmemes now identifies the memes that have been added within the last 3 days!*")
        await self.bot.send_message(ctx.message.author, "***The following comands can be used with !meme [meme_name] to show a specific meme.***")
        await self.bot.send_message(ctx.message.author, "-----------------------------------------------------------------------------------")
        await self.send_memelist(ctx.message.author, meme_list_mix)
        await self.bot.send_message(ctx.message.author, "Additional information: You can @mention me or type '!meme help'/'!helpmeme' to get the full list of comamnds")

    ### LIST OF POSSIBLE NSFW MEMES ###
    @commands.command(pass_context=True)
    async def listnsfwmemes(self, ctx):
        """Prints a list of NSFW memes."""
        # If not in PM already, tells the user to look at his PM box
        if not ctx.message.channel.is_private:
            await bot.say(inform_msg.format(ctx.message.author))
        await self.bot.send_message(ctx.message.author, "***The following comands can be used with !nsfwmeme [meme_name] to show a specific NSFW meme.***")
        await self.bot.send_message(ctx.message.author, "-----------------------------------------------------------------------------------")
        await self.send_memelist(ctx.message.author, nsfw_meme_list_mix)
        await self.bot.send_message(ctx.message.author, "Additional information: You can @mention me or type '!meme help'/'!helpmeme' to get the full list of comamnds")

    @commands.command()
    async def meme(self, meme_name : str = ""):
        """[meme_name]: Sends the specified meme, or a random one if unspecified."""
        await self.send_meme(meme_name, meme_list, meme_name_dict, MEMEPATH, "Error! Input syntax '!meme [meme_name]'")

    @commands.command()
    async def meem(self, meme_name : str = ""):
        """Same as meme."""
        await self.send_meme(meme_name, meme_list, meme_name_dict, MEMEPATH, "Error! Input syntax '!meme [meme_name]'")

    @commands.command()
    async def maymay(self, meme_name : str = ""):
        """Same as meme."""
        await self.send_meme(meme_name, meme_list, meme_name_dict, MEMEPATH, "Error! Input syntax '!meme [meme_name]'")

    @commands.command()
    async def nsfwmeme(self, meme_name : str = ""):
        """[meme_name]: Sends the specified NSFW meme, or a random one if unspecified."""
        await self.send_meme(meme_name, nsfw_meme_list, nsfw_meme_name_dict, NSFWMEMEPATH, "Error! Input syntax '!nsfwmeme [nsfw_meme_name]'")

    @commands.command()
    async def feelsgood(self, meme_name : str = ""):
        """[meme_name]: Sends the specified feelsgoodmeme, or a random one if unspecified."""
        await self.send_meme(meme_name, feelsgood_list, feelsgood_name_dict, MEMEPATH, "Error! Input syntax '!feelsgood [member_name]'")

    @commands.command()
    async def towelmeme(self, meme_name : str = ""):
        """Sends a random towel meme."""
        meme = random.choice(towel_meme_list)
        await self.bot.upload(os.path.join(MEMEPATH, meme))

    @commands.command()
    async def honk(self):
        """Used to be a sin."""
        await self.bot.upload(os.path.join(MEMEPATH, "dont_honk.jpg"))

    @commands.command(name="!brainpower")
    async def brainpower(self):
        """Note the extra "!". Brain Power chorus lyrics."""
        await self.bot.say("おーおおおおおおおおああああえーあーあーいーあーうーじょお - おおおおおおおおおおおおああえーおーあーあーうーうーあーえ - えええーええーえええああああえーあーえーいーえーあーじょおーおおおーおおーおお - おおええええおーあーあああーああああ")

    # Format !tsun [index] to retrive the index'th post ont the instagram page.
    # If index is not specified, we take any random post.
    @commands.command()
    async def tsun(self, index : int = None):
        """[index]: Copies something from a certain someone's Instagram page. If index is specified, we take the index-th post on the page. Otherwise, we take a random post."""
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
        post_list = re.split('"caption": "', data_tag)[1:]

        # If we have a valid index, we take that post (minus 1 since the list is 0-indexed)
        # Else, pick a random one.
        if index is None:
            post = random.choice(post_list)
        else:
            try:
                if index <= 0:
                    raise IndexError
                post = post_list[index - 1]

            except IndexError:
                await self.bot.say("Index {0} was out of range. Choosing a random post instead.".format(index))
                post = random.choice(post_list)

        # Find the end of the caption by the start of the next field, "likes"
        caption = post[:re.search('", "likes"', post).start()]
        # Fix all unicode characters of the form "\u[4 letters/numbers]"
        # http://stackoverflow.com/questions/11944978/call-functions-from-re-sub
        caption = re.sub(r"(\\u[0-9a-f]{4})", lambda match: codecs.decode(match.group(1), "unicode_escape"), caption)
        # Fix \n chars
        caption = re.sub(r"\\n", "\n", caption)

        # Find the start of image url by the "display_src" field 
        img_part = post[re.search('"display_src": "', post).end():]
        # Chop off at the "?"  part because after that is some authentication thing
        img = img_part[:re.search("\?", img_part).start()]
        # Remove backslashes
        img = re.sub(r"\\", "", img)

        await self.bot.say(img)
        await self.bot.say(caption)
        
    @commands.command()
    async def shigure(self, search : str = ""):
        """<searchterm>: Searches for a random anime on MAL and replaces a random word with Shigure."""
        if search == "":
            await self.bot.say("Please enter a valid search term.")
            await self.bot.say("Usage: !shigure <any string to be searched on MAL>")
            return

        base_url="http://myanimelist.net/api/anime/search.xml?q="
        # Takes the search terms, split by space and add "+" instead
        search_plus = "+".join(search.split(" "))

        # Searches on MAL, gets the response and parses the XML obtained
        req = requests.get(base_url + search_plus, auth=(self.credentials["MAL_user"], self.credentials["MAL_pass"]))

        try:
            tree = ElementTree.fromstring(req.content)
        except ElementTree.ParseError:
            await self.bot.say("Input {0} yielded no search results.".format(search))
            return

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

        await self.bot.say(" ".join(title_words))

    @commands.command()
    async def roasted(self):
        """To burn Insti."""
        await self.bot.upload(os.path.join(MEMEPATH, "shigure_burn.png"))
        await self.bot.say(":fire: :fire:")