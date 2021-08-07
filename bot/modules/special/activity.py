import asyncio
import datetime
import gc
import io
import math
import random
import sqlite3
from math import ceil
from typing import Any

import discord
from discord import TextChannel, Role, Member, Guild
from discord.ext import commands
from discord_slash import cog_ext

import config
from bot import MineplexBot
from config import *
from resources.declarations import declarations
from utilities.activity import create_card

cooldown_users: set = set()

"""
IMPORTANT NOTE:

To the person who has stumbled across this file and is reading it. This is one the last remaining parts of my
second-ever Discord Bot. It is for that reason that I don't claim the negative energy from the atrocities 
committed below this comment. I didn't want to spend time re-coding this, so I just modified it to work
with the new bot framework rather than re-creating it from scratch. Good luck and enjoy.

"""


class Activity(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        connection = sqlite3.connect(config.ACTIVITY_DB_PATH)
        try:
            connection.cursor().execute("CREATE TABLE users (id INTEGER, messages INTEGER, xp INTEGER, level INTEGER)"), connection.commit()
        except:
            pass
        connection.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Run calculations on every message"""

        # Not valid
        if (
                not message.guild or
                int(message.guild.id) != config.HOME_GUILD_ID or
                message.channel.id in config.ACTIVITY_BLACKLISTED_CHANNEL_IDS
                or message.author.bot
        ):
            return

            # Open Connection
        connect = sqlite3.connect(config.ACTIVITY_DB_PATH)
        cursor = connect.cursor()

        # Get the user's information from the database
        cursor.execute(f"SELECT * FROM users WHERE id='{message.author.id}'")
        user_info = cursor.fetchone()

        # If there is no user with that ID in the database
        if user_info is None:
            cursor.execute(f"INSERT INTO users VALUES (:id, :messages, :xp, :level)", {'id': message.author.id, 'messages': 1, 'xp': 32, 'level': 0})
            connect.commit()
        else:
            # Constructing Class
            user_object = LevelUser(connect, cursor, message.author.id, user_info[1], user_info[2], user_info[3])
            old_level = user_object.level

            user_object.increment_messages()  # Updating Messages

            if message.author.id in cooldown_users:
                user_object.connect.commit()
                connect.close()
                return

            user_object.increment_xp()  # Updating XP
            current_level = user_object.level_at_xp()  # Updating Level
            user_object.connect.commit()
            connect.close()

            # Level Up Message
            if int(old_level) != int(current_level):
                if config.ACTIVITY_LEVEL_UP_MESSAGE and any(role.id in config.ACTIVITY_ALLOWED_ROLES for role in message.author.roles):
                    send_channel: TextChannel = self.bot.get_channel(config.ACTIVITY_LEVEL_UP_CHANNEL_ID) if config.ACTIVITY_LEVEL_UP_CHANNEL_ID else message.channel
                    await send_channel.send(f"Congrats <@{message.author.id}> on level {current_level}! Keep up the good work!")

            # Level Up Role
            if int(current_level) in config.ACTIVITY_LEVEL_ROLE_IDS:
                role: Role = message.guild.get_role(config.ACTIVITY_LEVEL_ROLE_IDS.get(int(current_level)))
                await message.author.add_roles(role)

                if config.ACTIVITY_REMOVE_LOWER_ROLES:
                    for r in message.author.roles:
                        for role_id in config.ACTIVITY_LEVEL_ROLE_IDS.values():
                            if r.id == role_id:
                                if r.id != role.id:
                                    await message.author.remove_roles(r)

            if config.ACTIVITY_XP_GAIN_COOLDOWN:
                # Add to cooldown if not on cooldown
                cooldown_users.add(message.author.id)
                await asyncio.sleep(config.ACTIVITY_XP_GAIN_COOLDOWN)
                cooldown_users.remove(message.author.id)

    @cog_ext.cog_slash(**declarations["special"]["leaderboard"])
    async def leaderboard(self, context, page: int = 1):
        results_per_page = 10

        # Connect to the Database
        connect = sqlite3.connect(config.ACTIVITY_DB_PATH)
        cursor = connect.cursor()

        # Retrieve Leaderboard Top 10
        cursor.execute("SELECT * FROM users ORDER BY xp DESC;")
        raw_data = cursor.fetchall()
        raw_data = await self.__filter_leaderboard(context.guild, raw_data, config.ACTIVITY_ALLOWED_ROLES)

        # Terminate the connection
        connect.close()

        # Collect info from raw data
        raw_length = len(raw_data)  # Number of results
        raw_pages = ceil(raw_length / results_per_page)  # X Pages

        # If the page number in the command is valid
        try: page = int(page)
        except ValueError:
            await context.send(embed=discord.Embed(title=f'Invalid Page Number `({page} of {raw_pages})`', colour=EMBED_COLOUR_ERROR))
            return
        if not (0 < page <= raw_pages):
            await context.send(embed=discord.Embed(title=f'Invalid Page Number `({page} of {raw_pages})`', colour=EMBED_COLOUR_ERROR))
            return

        # Get the data at the page index
        data_index = (page - 1) * results_per_page
        selected_data = raw_data[data_index:data_index + results_per_page]

        leaderboard_users = ""
        leaderboard_levels_xp = ""
        leaderboard_messages = ""

        levels_length = []
        for item in selected_data: levels_length.append(len('{:,}'.format(item[3])))

        xp_length = []
        for item in selected_data: xp_length.append(len('{:,}'.format(item[2])))

        messages_length = []
        for item in selected_data: messages_length.append(int(len(str('{:,}'.format(item[1])))))

        for idx, item in enumerate(selected_data):
            val: int = idx + data_index + 1
            val: int = {1: "🥇", 2: "🥈", 3: "🥉"}.get(val, f"`{val}.`")

            __uuid = item[0]
            __level = '{:,}'.format(item[3])
            __xp = '{:,}'.format(item[2])
            __messages = '{:,}'.format(item[1])

            leaderboard_users += f"{val} <@{__uuid}>\n"

            leaderboard_levels_xp += f"`Lvl. {__level}{' ' * (max(levels_length) - len(__level))} | XP {__xp}{' ' * (max(xp_length) - len(__xp))}`\n"
            leaderboard_messages += f"`{__messages}{' ' * (max(messages_length) - len(__messages))}`\n"

        embed_desc = f"<:{CHECK_EMOJI}> Select additional pages with `!leaderboard [page]`" if page == 1 else ""

        await context.send(
            embed=discord.Embed(
                title=f"🏆 Activity Leaderboard - Page {page}/{raw_pages}",
                color=EMBED_COLOUR_STRD,
                description=embed_desc
            ).add_field(
                name="Member",
                value=leaderboard_users
            ).add_field(
                name="Levels & XP",
                value=leaderboard_levels_xp
            ).add_field(
                name="Messages",
                value=leaderboard_messages
            ).set_footer(
                icon_url=self.bot.user.avatar_url,
                text=f'{context.guild.name} • Retrieved {datetime.datetime.utcnow().strftime("%D | %I:%M %p (UTC)")}'
            )
        )

    @staticmethod
    async def __filter_leaderboard(guild: Guild, dataset: Any, role_ids: List[int]):
        # If we aren't filtering, return old
        if not config.ACTIVITY_ALLOWED_ROLES:
            return dataset

        new_set: List[Tuple[int, int, int, int]] = []

        for entry in dataset:
            try:
                roles: list = guild.get_member(entry[0]).roles
            except:
                continue

            if any(int(role.id) in role_ids for role in roles):
                new_set.append(entry)

        return new_set

    @cog_ext.cog_slash(**declarations["special"]["rank"])
    async def rank(self, context, user: Optional[Member] = None):
        if user is None:
            # Get User's Info
            user = context.author

        user_id = user.id

        # Open Connection
        connect = sqlite3.connect(config.ACTIVITY_DB_PATH)
        cursor = connect.cursor()

        # Get the user's information from the database
        cursor.execute(f"SELECT * FROM users WHERE id='{user_id}'")
        user_info = cursor.fetchone()

        # If there is no user with that ID in the database
        if user_info is None:
            cursor.execute(f"INSERT INTO users VALUES (:id, :messages, :xp, :level)", {'id': user_id, 'messages': 1, 'xp': 0, 'level': 0})
            connect.commit()
            await context.send(f"<:{X_EMOJI}> Could not display a rank card due to lack of stats. Created account! Try again.")
            return
        else:
            # Retrieve Leaderboard
            cursor.execute("SELECT * FROM users ORDER BY xp DESC;")
            xp_lb = cursor.fetchall()
            xp_lb = await self.__filter_leaderboard(context.guild, xp_lb, config.ACTIVITY_ALLOWED_ROLES)

        user_object = LevelUser(connect, cursor, user_id, user_info[1], user_info[2], user_info[3])

        needed_xp = int(user_object.xp_to_next_level() - user_object.xp_from_level(user_object.level_from_xp(user_object.xp)))
        achieved_xp = int(user_object.xp - user_object.xp_from_level(user_object.level))
        level = user_object.level

        # Close connection and remove value
        del user_object
        connect.close()

        rank = None
        # Taking LB Values
        for idx, item in enumerate(xp_lb):
            if item[0] == user_id:
                rank = idx + 1
                break

        image = create_card(user, achieved_xp, needed_xp, rank, level, config.ACTIVITY_RESOURCE_PATH)
        gc.collect()

        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await context.send(file=discord.File(fp=image_binary, filename='image.png'))


class LevelUser:
    def __init__(self, _connect, _cursor, uuid, messages, xp, level):
        self.connect = _connect
        self.cursor = _cursor
        self.uuid = uuid
        self.messages = messages
        self.xp = xp
        self.level = level

    def __str__(self):
        return f"XP = {self.xp} | Level = {self.level} | Messages = {self.messages}"

    def increment_xp(self):
        """Take the current XP and add a random amount from MIN-MAX in config.py"""
        self.xp += random.randint(config.ACTIVITY_MIN_XP_GAIN, config.ACTIVITY_MAX_XP_GAIN)
        self.cursor.execute(f"UPDATE users SET xp={self.xp} WHERE id='{self.uuid}'")

    def increment_messages(self):
        """Increment a user's current messages by 1"""
        self.messages += 1
        self.cursor.execute(f"UPDATE users SET messages={self.messages} WHERE id='{self.uuid}'")

    @staticmethod
    def xp_from_level(level):
        return sum([5 * (l ** 2) + (50 * l) + 100 for l in range(0, level)])

    @staticmethod
    def level_from_xp(xp):
        required_level = 0
        while True:
            supposed_xp = LevelUser.xp_from_level(required_level)
            if supposed_xp >= xp:
                return required_level - 1
            required_level += 1

    def level_at_xp(self):
        """Update the level based on the current XP"""

        self.level = int(math.floor(max(self.level_from_xp(self.xp), 0)))
        self.cursor.execute(f"UPDATE users SET level={self.level} WHERE id='{self.uuid}'")

        return self.level

    def xp_to_next_level(self):
        """Get the XP from the current Level to the next level"""
        return int(math.floor(self.xp_from_level(self.level + 1)))


def setup(bot: MineplexBot):
    bot.add_cog(Activity(bot))
