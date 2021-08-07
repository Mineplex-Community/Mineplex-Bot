import json
from datetime import datetime
from random import choice, randint

import discord
from discord.ext import commands, tasks
from discord_slash import SlashContext, cog_ext

from config import EMBED_COLOUR_ERROR, EMBED_COLOUR_SUCCESS, EMBED_COLOUR_STRD, X_EMOJI, CHECK_EMOJI
from resources.declarations import declarations

CONFIG: dict = json.loads(open('./resources/data/recruitment.json').read())
RECRUITMENT_CHANNEL = CONFIG["recruitment_channel"]
COMMAND_CHANNELS = CONFIG["command_channels"]
RANDOM_NAMES = CONFIG["names"]
RANDOM_CLANS = CONFIG["clans"]
RANDOM_EMOJIS = CONFIG["emojis"]

creating_post: list = []

"""
IMPORTANT NOTE:

To the person who has stumbled across this file and is reading it. This is one the last remaining parts of my
second-ever Discord Bot. It is for that reason that I don't claim the negative energy from the atrocities 
committed below this comment. I didn't want to spend time re-coding this, so I just modified it to work
with the new bot framework rather than re-creating it from scratch. Good luck and enjoy.

"""


def tm_find_time():
    time = datetime.utcfromtimestamp(datetime.now().timestamp())
    return time.strftime('%D | %I:%M %p (UTC)')


def checklist(check_list, context, check_type):
    for idx, val in enumerate(check_list):
        if val[0] == context.author.id:
            if check_type:
                return True
            elif not check_type:
                return idx
        else:
            pass


def remove_spaces(message):
    for idx, val in enumerate(message):
        if val == " ":
            pass
        else:
            return idx


def create_requirements_list(message):
    message += ","
    formatted_requirements = []
    current_iteration = ""
    current_requirement = 0

    for char in message:
        if char != ",":
            current_iteration += char
        else:
            if not current_iteration.isspace() and current_iteration != "":
                current_requirement += 1
                start_index = remove_spaces(current_iteration)
                formatted_requirements.append(f"{current_requirement}. {current_iteration[start_index:].capitalize()}")
                current_iteration = ""

    if current_requirement < 3:
        return None

    if current_requirement > 10:
        return None

    else:
        return "\n".join(formatted_requirements)


def display_instructions(self, step_number, instruction, usage, example):
    instruction_embed = discord.Embed(
        title=f"Step {step_number}: {instruction}",
        description=f"**Usage:** `{usage}`\n**Example:** `{example}`\n\n**Note:** Cancel setup at any time with `!recruitment cancel`",
        color=EMBED_COLOUR_STRD
    )
    instruction_embed.set_thumbnail(url=self.bot.user.avatar_url)
    return instruction_embed


def display_instructions_error(self, instruction, usage, example):
    error_instruction_embed = discord.Embed(
        title=f"Incorrect Usage: {instruction}",
        description=f"\n**Usage:** `{usage}`\n**Example:** `{example}`",
        color=EMBED_COLOUR_ERROR
    )
    error_instruction_embed.set_thumbnail(url=self.bot.user.avatar_url)
    return error_instruction_embed


class RecruitmentPost(commands.Cog, name="recruitment"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.cache_clear.start()

    @tasks.loop(hours=24)
    async def cache_clear(self):
        try:
            last = creating_post[-1]
            creating_post.clear()
            creating_post.append(last)
        except IndexError:
            pass

    @cog_ext.cog_slash(**declarations["special"]["recruitment"])
    async def recruitment(self, context: SlashContext, information: str = ""):
        if context.channel.id in COMMAND_CHANNELS:  # Checking if in a command channel

            if not checklist(creating_post, context, True):
                creating_post.append([context.author.id, None, None, None, None, None, None, None, None])
                """
                0: Author ID
                1: Type (clan/player)
                8: Confirmation
                """

                """ TYPE 1
                
                2: IGN
                3: Clan
                4: Clans Server (1-9)
                5: Description
                6: Requirements
                7: Extra Information
                
                """

                # OR

                """ TYPE 2
                
                2: IGN
                3: Ideal Clans Server
                4: What type of clan are you looking for?
                5: Describe yourself...
                6: What are your qualifications/experience?
                7: Extra Information
                
                """
                await context.send(
                    embed=display_instructions(self, 1,
                                               "What kind of post do you want to make?",
                                               "!recruitment <clan/player>",
                                               f"!recruitment {choice(['clan', 'player'])}"))

            else:
                user_index = checklist(creating_post, context, False)

                if information == "cancel":
                    creating_post.remove(creating_post[user_index])

                    embed = discord.Embed(
                        description=f"<:{CHECK_EMOJI}> <@{context.author.id}> Cancelled the recruitment post.",
                        color=EMBED_COLOUR_SUCCESS
                    )
                    embed.set_author(name=f"{context.author.name}#{context.author.discriminator}",
                                     icon_url=context.author.avatar_url)

                    await context.send(embed=embed)

                else:
                    if creating_post[user_index][1] is None:
                        """PROMPT #1
                
                        What type is the post? Clan or Player?"""

                        creating_post[user_index][1] = information.lower()  # Remove spaces, make lowercase

                        if creating_post[user_index][1] == "clan":
                            await context.send(
                                content=f"<:{CHECK_EMOJI}>",
                                embed=display_instructions(self, 2,
                                                           "What is your IGN (3-16 chars)?",
                                                           "!recruitment <IGN>",
                                                           f"!recruitment {choice(RANDOM_NAMES)}"))

                        elif creating_post[user_index][1] == "player":
                            await context.send(
                                content=f"<:{CHECK_EMOJI}>",
                                embed=display_instructions(self, 2,
                                                           "What is your IGN (3-16 chars)?",
                                                           "!recruitment <IGN>",
                                                           f"!recruitment {choice(RANDOM_NAMES)}"))
                        else:
                            await context.send(
                                content=f"<:{X_EMOJI}>",
                                embed=display_instructions_error(
                                    self,
                                    "What kind of post do you want to make?",
                                    "!recruitment <clan/player>",
                                    f"!recruitment {choice(['clan', 'player'])}"))
                            creating_post[user_index][1] = None

                    else:
                        # PATH SPLITS HERE (CLAN VS PLAYER)

                        # If Clan Recruitment Post
                        if creating_post[user_index][1] == "clan":
                            """
    
                            -----------------------------------
                            CLAN RECRUITMENT POST BEGINS HERE
                            -----------------------------------
    
                            """
                            construct_post = False

                            # Setting the IGN
                            if creating_post[user_index][2] is None:
                                """CLAN PROMPT #1
                                
                                What is your IGN?"""
                                creating_post[user_index][2] = information  # Remove spaces
                                name_length = len(creating_post[user_index][2])

                                if not 3 <= name_length <= 16:
                                    # Invalid length, player name must be 3-16 characters.
                                    creating_post[user_index][2] = None

                                if creating_post[user_index][2] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What is your IGN (3-16 chars)?",
                                                                         "!recruitment <IGN>",
                                                                         f"!recruitment {choice(RANDOM_NAMES)}"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 3,
                                                                   "What is your Clan Name (3-10 chars)?",
                                                                   "!recruitment <clan name>",
                                                                   "!recruitment IfOnly"))

                            # Setting the Clan Name
                            elif creating_post[user_index][3] is None:
                                """CLAN PROMPT #2
        
                                What is the clan name?"""
                                creating_post[user_index][3] = information  # Remove spaces
                                clan_name_length = len(creating_post[user_index][3])

                                if not 3 <= clan_name_length <= 10:
                                    creating_post[user_index][3] = None

                                if creating_post[user_index][3] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What is your Clan Name (3-10 chars)?",
                                                                         "!recruitment <clan name>",
                                                                         "!recruitment IfOnly"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 4,
                                                                   "What is your Clans Server (1-9)?",
                                                                   "!recruitment <server number>",
                                                                   f"!recruitment {randint(1, 9)}"))


                            # Setting the Clans Server
                            elif creating_post[user_index][4] is None:
                                """CLAN PROMPT #3
                                
                                What is the clans server?"""
                                creating_post[user_index][4] = information  # Remove spaces

                                if creating_post[user_index][4].isnumeric():  # Checking if the input was a number

                                    if 1 <= int(creating_post[user_index][4]) <= 9:  # Checking if clans server is valid
                                        creating_post[user_index][4] = f"Clans-{creating_post[user_index][4]}"

                                    else:
                                        # Must be between 1 & 9
                                        creating_post[user_index][4] = None

                                elif creating_post[user_index][4].lower() == "tbd":
                                    creating_post[user_index][4] = f"To be decided"

                                elif creating_post[user_index][4].lower() == "skip" or creating_post[user_index][4].lower() == "n/a":
                                    creating_post[user_index][4] = f"N/A"

                                else:
                                    # Must be numeric
                                    creating_post[user_index][4] = None

                                if creating_post[user_index][4] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What is your Clans Server (1-9)?",
                                                                         "!recruitment <server number | TBD | skip OR n/a>",
                                                                         f"!recruitment {randint(1, 9)}"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 5,
                                                                   "Briefly describe your clan, who you are, etc.\n(100-850 chars)",
                                                                   "!recruitment <paragraph - can be multiple lines>",
                                                                   "!recruitment This is my clan description."))

                            # Clan Description
                            elif creating_post[user_index][5] is None:
                                """CLAN PROMPT #4
        
                                Briefly describe your clan, who you are, etc."""
                                creating_post[user_index][5] = information  # Remove spaces

                                # Limit to 850 Characters
                                if len(creating_post[user_index][5]) >= 850:
                                    # Too long, must a maximum of 850 characters"
                                    creating_post[user_index][5] = None
                                if len(creating_post[user_index][5]) <= 100:
                                    # Too short, must be at least 50 characters
                                    creating_post[user_index][5] = None

                                if creating_post[user_index][5] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "Briefly describe your clan, who you are, etc. (100-850 chars)",
                                                                         "!recruitment <paragraph - can be multiple lines>",
                                                                         "!recruitment This is my clan description."))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 6,
                                                                   "What are your clan requirements (3-10 items)?",
                                                                   "!recruitment <requirement1>, <requirement2>, etc...",
                                                                   "!recruitment Be good, Don't throw, Act nice"))

                            # Clan Requirements
                            elif creating_post[user_index][6] is None:
                                """CLAN PROMPT #5
        
                                List your Clan's Requirements with each one separated by a comma."""

                                creating_post[user_index][6] = information  # Remove Spaces
                                creating_post[user_index][6] = create_requirements_list(creating_post[user_index][6])  # Parse

                                if creating_post[user_index][6] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What are your clan requirements (3-10 items)?",
                                                                         "!recruitment <requirement1>, <requirement2>, etc...",
                                                                         "!recruitment Be good, Don't throw, Act nice"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 7,
                                                                   "Is there any other information you want to include (30-500 chars)?",
                                                                   "!recruitment <paragraph | OR skip | OR N/A>",
                                                                   "!recruitment This is my extra information."))

                            elif creating_post[user_index][7] is None:
                                """CLAN PROMPT #6
        
                                Any extra information"""
                                creating_post[user_index][7] = information

                                if creating_post[user_index][7].lower() == "skip" or creating_post[user_index][7].lower() == "n/a":
                                    # Posting message
                                    creating_post[user_index][7] = False  # Post without the extra info section
                                elif creating_post[user_index][7] == "":
                                    # Invalid
                                    creating_post[user_index][7] = None
                                elif len(creating_post[user_index][7]) >= 500:
                                    # Too long, must a maximum of 850 characters
                                    creating_post[user_index][7] = None
                                elif len(creating_post[user_index][7]) <= 30:
                                    # Too short, must be at least 30 characters
                                    creating_post[user_index][7] = None
                                else:
                                    # Pass through
                                    pass

                                if creating_post[user_index][7] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "Is there any other information you want to include (30-500 chars)?",
                                                                         "!recruitment <paragraph | OR skip | OR N/A>",
                                                                         "!recruitment This is my extra information."))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 8,
                                                                   "Are you sure you want to post this? It's not too late to turn back.",
                                                                   "!recruitment <confirm | cancel>",
                                                                   "!recruitment confirm"))


                            elif creating_post[user_index][8] is None:
                                """CLAN PROMPT #7
                                
                                Do you want to post the message? Confirm with !recruitment confirm or cancel with !recruitment cancel"""

                                creating_post[user_index][8] = information

                                if creating_post[user_index][8].lower() == "confirm":
                                    construct_post = True

                                else:
                                    construct_post = False
                                    creating_post[user_index][8] = None
                                    await context.send(
                                        embed=display_instructions_error(self,
                                                                         "Are you sure you want to post this? It's not too late to turn back.",
                                                                         "!recruitment <confirm | cancel>",
                                                                         "!recruitment confirm"))

                            # Posting the message

                            if construct_post:
                                if not creating_post[user_index][7]:
                                    extra_info = ""
                                else:
                                    extra_info = f"**Extra Information**\n{creating_post[user_index][7]}\n\n"

                                formatted_embed = "" \
                                                  + f"**IGN**\n{creating_post[user_index][2]}\n\n" \
                                                  + f"**Clan Name**\n{creating_post[user_index][3]}\n\n" \
                                                  + f"**Server**\n{creating_post[user_index][4]}\n\n" \
                                                  + f"**Briefly describe your clan, who you are, etc.**\n{creating_post[user_index][5]}\n\n" \
                                                  + f"**Clan Requirements**\n{creating_post[user_index][6]}\n\n" \
                                                  + f"{extra_info}" \
                                                  + f"**How to Contact**\nInterested? DM <@{creating_post[user_index][0]}> for information."

                                emoji_choice = choice(RANDOM_EMOJIS)

                                n = creating_post[user_index][3]
                                c = n[0].capitalize() + n[1:]

                                embed = discord.Embed(
                                    title=f"{emoji_choice} {c}'s Recruitment Post (Clan Post) {emoji_choice}",
                                    description=formatted_embed,
                                    color=0x5fd3e3
                                )
                                embed.set_author(name="Message by Clans Insights Bot:", icon_url="https://i.imgur.com/6NeKLZq.png")
                                embed.set_footer(text=f"Player Submitted Post • {tm_find_time()}", icon_url=self.bot.user.avatar_url)

                                send_channel = self.bot.get_channel(RECRUITMENT_CHANNEL)
                                await send_channel.send(embed=embed)

                                embed = discord.Embed(
                                    description=f"<:{CHECK_EMOJI}> Successfully posted `clan` recruitment message in <#{send_channel.id}>.",
                                    color=EMBED_COLOUR_SUCCESS
                                )
                                embed.set_author(name=f"{context.author.name}#{context.author.discriminator}",
                                                 icon_url=context.author.avatar_url)

                                await context.send(embed=embed)

                                creating_post.remove(creating_post[user_index])

                        elif creating_post[user_index][1] == "player":
                            """
    
                            -----------------------------------
                            PLAYER RECRUITMENT POST BEGINS HERE
                            -----------------------------------
    
                            """

                            construct_post = False

                            # User's IGN
                            if creating_post[user_index][2] is None:
                                """PLAYER PROMPT #1

                                What is your IGN?"""

                                creating_post[user_index][2] = information  # Remove spaces
                                name_length = len(creating_post[user_index][2])

                                if not 3 <= name_length <= 16:
                                    # Invalid length, player name must be 3-16 characters.
                                    creating_post[user_index][2] = None

                                if creating_post[user_index][2] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What is your IGN (3-16 chars)?",
                                                                         "!recruitment <IGN>",
                                                                         f"!recruitment {choice(RANDOM_NAMES)}"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 3,
                                                                   "What is your ideal Clans Server (1-9)?",
                                                                   "!recruitment <server number | skip OR N/A>",
                                                                   f"!recruitment {randint(1, 9)}"))

                            # Preferred Clans Server
                            elif creating_post[user_index][3] is None:
                                """PLAYER PROMPT #2

                                What is your preferred Clans Server server?"""
                                creating_post[user_index][3] = information  # Remove spaces

                                if creating_post[user_index][3].isnumeric():  # Checking if the input was a number

                                    if 1 <= int(creating_post[user_index][3]) <= 9:  # Checking if clans server is valid
                                        creating_post[user_index][3] = f"Clans-{creating_post[user_index][3]}"

                                    else:
                                        # Must be between 1 & 9
                                        creating_post[user_index][3] = None

                                elif creating_post[user_index][3].lower() == "skip" or creating_post[user_index][3].lower() == "n/a":
                                    creating_post[user_index][3] = "N/A"

                                else:
                                    # Must be numeric
                                    creating_post[user_index][3] = None

                                if creating_post[user_index][3] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What is your ideal Clans Server (1-9)?",
                                                                         "!recruitment <server number | skip OR N/A>",
                                                                         f"!recruitment {randint(1, 9)}"))

                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 4,
                                                                   "What type of clan are you looking for?\n(25-350 chars)",
                                                                   "!recruitment <paragraph - can be multiple lines>",
                                                                   "!recruitment I'm looking for a nice group of..."))

                            # What type of clan are you looking for?
                            elif creating_post[user_index][4] is None:
                                """PLAYER PROMPT #3

                                What type of clan are you looking for?"""

                                creating_post[user_index][4] = information  # Remove spaces

                                # Limit to 25-350 Characters
                                if len(creating_post[user_index][4]) >= 350:
                                    # Too long, must a maximum of 350 characters"
                                    creating_post[user_index][4] = None
                                if len(creating_post[user_index][4]) <= 25:
                                    # Too short, must be at least 25 characters
                                    creating_post[user_index][4] = None

                                if creating_post[user_index][4] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What type of clan are you looking for?\n(25-300 chars)",
                                                                         "!recruitment <paragraph - can be multiple lines>",
                                                                         "!recruitment I'm looking for a nice group of..."))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 5,
                                                                   "Describe yourself, who you are, etc.\n(50-500 chars)",
                                                                   "!recruitment <paragraph - can be multiple lines>",
                                                                   "!recruitment I'm a hard working Mineman (mostly)"))

                            # Describe Yourself
                            elif creating_post[user_index][5] is None:
                                """PLAYER PROMPT #4

                                Describe yourself..."""

                                creating_post[user_index][5] = information  # Remove spaces

                                # Limit to 25-350 Characters
                                if len(creating_post[user_index][5]) >= 350:
                                    # Too long, must a maximum of 350 characters"
                                    creating_post[user_index][5] = None
                                if len(creating_post[user_index][5]) <= 25:
                                    # Too short, must be at least 25 characters
                                    creating_post[user_index][5] = None

                                if creating_post[user_index][5] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "Describe yourself, who you are, etc.\n(50-500 chars)",
                                                                         "!recruitment <paragraph - can be multiple lines>",
                                                                         "!recruitment I'm a hard working Mineman (mostly)"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 6,
                                                                   "What are your qualifications/experience (3-10 items)?",
                                                                   "!recruitment <qualification1>, <experience1>, etc...",
                                                                   "!recruitment Played since Alpha, pos. KDR, nice"))

                            # Qualifications/Experience
                            elif creating_post[user_index][6] is None:
                                """PLAYER PROMPT #5
    
                                What are your qualifications/experience in the Clans field?"""

                                creating_post[user_index][6] = information  # Remove Spaces
                                creating_post[user_index][6] = create_requirements_list(
                                    creating_post[user_index][6])  # Parse

                                if creating_post[user_index][6] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "What are your qualifications/experience (3-10 items)?",
                                                                         "!recruitment <qualification1>, <experience1>, etc...",
                                                                         "!recruitment Played since Alpha, positive KDR, nice"))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 7,
                                                                   "Is there any other information you want to include (30-500 chars)?",
                                                                   "!recruitment <paragraph | OR skip | OR N/A>",
                                                                   "!recruitment This is my extra information."))

                            elif creating_post[user_index][7] is None:
                                """PLAYER PROMPT #6

                                Any extra information"""
                                creating_post[user_index][7] = information

                                if creating_post[user_index][7].lower() == "skip" or creating_post[user_index][7].lower() == "n/a":
                                    # Posting message
                                    creating_post[user_index][7] = False  # Post without the extra info section
                                elif creating_post[user_index][7] == "":
                                    # Invalid
                                    creating_post[user_index][7] = None
                                elif len(creating_post[user_index][7]) >= 500:
                                    # Too long, must a maximum of 850 characters
                                    creating_post[user_index][7] = None
                                elif len(creating_post[user_index][7]) <= 30:
                                    # Too short, must be at least 30 characters
                                    creating_post[user_index][7] = None
                                else:
                                    # Pass through
                                    pass

                                if creating_post[user_index][7] is None:
                                    await context.send(
                                        content=f"<:{X_EMOJI}>",
                                        embed=display_instructions_error(self,
                                                                         "Is there any other information you want to include (30-500 chars)?",
                                                                         "!recruitment <paragraph | OR skip | OR N/A>",
                                                                         "!recruitment This is my extra information."))
                                else:
                                    await context.send(
                                        content=f"<:{CHECK_EMOJI}>",
                                        embed=display_instructions(self, 8,
                                                                   "Are you sure you want to post this? It's not too late to turn back.",
                                                                   "!recruitment <confirm | cancel>",
                                                                   "!recruitment confirm"))


                            elif creating_post[user_index][8] is None:
                                """PLAYER PROMPT #7

                                Do you want to post the message? Confirm with !recruitment confirm or cancel with !recruitment cancel"""

                                creating_post[user_index][8] = information

                                if creating_post[user_index][8].lower() == "confirm":
                                    construct_post = True

                                else:
                                    construct_post = False
                                    creating_post[user_index][8] = None
                                    await context.send(
                                        embed=display_instructions_error(self,
                                                                         "Are you sure you want to post this? It's not too late to turn back.",
                                                                         "!recruitment <confirm | cancel>",
                                                                         "!recruitment confirm"))

                            if construct_post:
                                if not creating_post[user_index][7]:
                                    extra_info = ""
                                else:
                                    extra_info = f"**Extra Information**\n{creating_post[user_index][7]}\n\n"

                                formatted_embed = "" \
                                                  + f"**IGN**\n{creating_post[user_index][2]}\n\n" \
                                                  + f"**Preferred Clans Server**\n{creating_post[user_index][3]}\n\n" \
                                                  + f"**What type of clan are you looking for?**\n{creating_post[user_index][4]}\n\n" \
                                                  + f"**Briefly describe yourself, who you are, etc.**\n{creating_post[user_index][5]}\n\n" \
                                                  + f"**What are your qualifications/experience?**\n{creating_post[user_index][6]}\n\n" \
                                                  + f"{extra_info}" \
                                                  + f"**How to Contact**\nInterested? DM <@{creating_post[user_index][0]}> for information."

                                emoji_choice = choice(RANDOM_EMOJIS)

                                n = creating_post[user_index][2]
                                c = n[0].capitalize() + n[1:]

                                embed = discord.Embed(
                                    title=f"{emoji_choice} {c}'s Recruitment Post (Player Post) {emoji_choice}",
                                    description=formatted_embed,
                                    color=0x5fd3e3
                                )
                                embed.set_author(name="Message by Clans Insights Bot:", icon_url="https://i.imgur.com/6NeKLZq.png")
                                embed.set_footer(text=f"Player Submitted Post • {tm_find_time()}", icon_url=self.bot.user.avatar_url)
                                embed.set_thumbnail(url=self.bot.user.avatar_url)

                                send_channel = self.bot.get_channel(RECRUITMENT_CHANNEL)
                                await send_channel.send(embed=embed)

                                embed = discord.Embed(
                                    description=f"<:{CHECK_EMOJI}> Successfully posted `player` recruitment message in <#{send_channel.id}>.",
                                    color=EMBED_COLOUR_SUCCESS
                                )
                                embed.set_author(name=f"{context.author.name}#{context.author.discriminator}",
                                                 icon_url=context.author.avatar_url)

                                await context.send(embed=embed)

                                creating_post.remove(creating_post[user_index])
        else:
            await context.message.add_reaction(X_EMOJI)


def setup(bot):
    bot.add_cog(RecruitmentPost(bot))
