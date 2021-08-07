import logging
from typing import Optional

import aiohttp
from discord import VoiceChannel
from discord.ext import commands, tasks

import config
from bot import MineplexBot


class PlayerCounter(commands.Cog):

    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

        # API Endpoints
        self.java: str = "https://api.mcsrvstat.us/2/mineplex.com"
        self.bedrock: str = "https://api.bedrockinfo.com/v1/status?server=mco.mineplex.com&port=19132"

        # Channels
        self.member_channel: Optional[VoiceChannel] = None
        self.player_channel: Optional[VoiceChannel] = None

    @staticmethod
    async def __request(url: str) -> Optional[dict]:
        """
        Make an async request and return JSON or None

        :param url: URL to request
        :return: Result

        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as result:
                    return await result.json()
        except:
            return {}

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start the tasks on ready
        :return: None

        """
        if config.PLAYER_COUNT_CHANNEL:
            self.player_channel = self.bot.get_channel(config.PLAYER_COUNT_CHANNEL)
            self.player_counter.start()

        if config.MEMBER_COUNT_CHANNEL:
            self.member_channel = self.bot.get_channel(config.MEMBER_COUNT_CHANNEL)
            self.member_counter.start()

    @tasks.loop(seconds=config.COUNT_CHANNEL_INTERVAL, reconnect=True)
    async def member_counter(self):
        """
        Edit a channel with the # of players on the Mineplex combined bedrock + java server
        :return: None

        """
        # Retrieve Statistics
        java: Optional[dict] = await self.__request(self.java) if config.PLAYER_COUNT_INCLUDE_JAVA else {"players": {"online": 0}}
        bedrock: Optional[dict] = await self.__request(self.bedrock) if config.PLAYER_COUNT_INCLUDE_BEDROCK else {"Players": 0}

        # Parse Statistics
        try:
            java_count: int = int(java["players"]["online"])
            bedrock_count: int = int(bedrock["Players"])
        except KeyError:
            return logging.warning(f"Failed to parse java or bedrock count from [Java, Bedrock] => [{str(java)}, {str(bedrock)}]")

        # Edit Channel Name
        await self.player_channel.edit(
            name=config.PLAYER_COUNT_STRING.replace("%count%", '{:,}'.format(java_count + bedrock_count))
        )

    @tasks.loop(seconds=config.COUNT_CHANNEL_INTERVAL, reconnect=True)
    async def player_counter(self):
        """
        Edit a channel with the Discord Member Count
        :return:

        """
        # Edit Channel Name
        await self.member_channel.edit(
            name=config.MEMBER_COUNT_STRING.replace("%count%", '{:,}'.format(self.member_channel.guild.member_count))
        )


def setup(bot: MineplexBot):
    bot.add_cog(PlayerCounter(bot))
