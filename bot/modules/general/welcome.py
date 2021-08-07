from io import BytesIO

import discord
from PIL.Image import Image
from discord import Member, TextChannel
from discord.ext import commands

import config
from bot import MineplexBot
from config import *
from utilities.welcome import create_welcome


class Welcome(commands.Cog):
    RESOURCE_PATH: str = "./resources/cards/welcome"

    def __init__(self, bot):
        self.bot: MineplexBot = bot
        self.channel: Optional[TextChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Update Cog cache on ready
        :return: None

        """
        self.channel: TextChannel = self.bot.get_channel(config.WELCOME_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        When someone joins the server

        :param member: The person that joined
        :return: None

        """

        # If not in the correct guild
        if int(member.guild.id) != HOME_GUILD_ID:
            return

        # Save the image
        image: Image = create_welcome(member, self.RESOURCE_PATH)

        buffer = BytesIO()
        image.save(buffer, "png")
        buffer.seek(0)

        await self.channel.send(file=discord.File(fp=buffer, filename="welcome.png"))


def setup(bot: MineplexBot):
    bot.add_cog(Welcome(bot))
