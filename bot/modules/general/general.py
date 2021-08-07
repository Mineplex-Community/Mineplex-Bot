import asyncio
import os
import platform

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from resources.declarations import declarations


class General(commands.Cog):

    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Actions to perform on bot ready
        :return: None

        """
        await self.__initial_messages()

    async def __initial_messages(self):
        """
        Messages to send on bot ready
        :return: None

        """
        print("-------------------")
        print(f"Logged in as {self.bot.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("Go for launch!")
        print("-------------------")

    @cog_ext.cog_slash(**declarations["general"]["ping"])
    async def ping(self, context: SlashContext):
        """
        Get the bot's latency

        :param context: Slash Context
        :return: None

        """
        message = await context.send(f"<{config.SEARCHING_EMOJI}> **Bot's Ping** :mag_right: `Loading...`")
        await asyncio.sleep(1)
        await message.edit(content=f"<:{config.ONLINE_EMOJI}> **Bot's Ping** :mag_right: `{round(self.bot.latency * 1000)} ms`")


def setup(bot: MineplexBot):
    return bot.add_cog(General(bot))
