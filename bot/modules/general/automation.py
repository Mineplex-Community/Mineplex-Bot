import random
from typing import List

import discord
from discord import ActivityType, Member, Role, Message
from discord.ext import commands, tasks

import config
from bot import MineplexBot


class Automation(commands.Cog):

    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

        # Parse Bot Statuses
        self.bot_statuses: List[str] = self.bot.yaml_config.get("bot-statuses", [])

        # Parse auto-replies
        auto_replies: List[str] = self.bot.yaml_config.get("auto-replies", [])
        self.auto_replies: dict = {}

        for reply in auto_replies:
            raw: List[str] = reply.split(";")
            self.auto_replies[raw[0].lower()] = '\n'.join(raw[1:])

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Start looped tasks on ready
        :return: None

        """
        if config.STATUS_CHANGE_ENABLED:
            self.change_status.start()

    @tasks.loop(seconds=max(config.STATUS_CHANGE_INTERVAL, 30), reconnect=True)
    async def change_status(self):
        """
        Change the status every X seconds
        :return: None
        """
        try:
            choice: str = random.choice(self.bot_statuses)
        except IndexError:
            choice: str = 'around'

        await self.bot.change_presence(
            activity=discord.Activity(name=choice, type=ActivityType.playing)
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        When someone joins the server

        :param member: Member
        :return: None

        """
        if int(member.guild.id) != config.HOME_GUILD_ID or not config.AUTO_ROLE_IDS:
            return

        roles: List[Role] = []
        for role_id in config.AUTO_ROLE_IDS:
            try:
                roles.append(member.guild.get_role(role_id))
            except:
                pass

        await member.add_roles(roles)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Auto-replies for specific config keys

        :param message: Message to send
        :return: None

        """

        # Ignore bots
        if message.author.bot:
            return

        # Parse message as keyword
        keyword: str = message.content.lower()

        if keyword in self.auto_replies.keys():
            await message.channel.send(self.auto_replies.get(keyword))


def setup(bot: MineplexBot):
    return bot.add_cog(Automation(bot))
