from discord import Message, Member
from discord.ext import commands

import config
from bot import MineplexBot


class Filter(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot
        self.filter = [word for word in open(config.FILTER_PATH).read().split("\n") if word]

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        When someone sends a message

        :param message: The message they sent
        :return: None

        """
        # Channels that bypass the filter
        if int(message.channel.id) in config.FILTER_BYPASS_CHANNELS:
            return

        # Roles that bypass the filter
        if isinstance(message.author, Member) and any(role.id in config.FILTER_BYPASS_ROLES for role in message.author.roles):
            return

        # Run the filter
        for word in self.filter:
            if word in (message.content.replace(" ", "").replace("!", "i").replace("3", "e").replace("4", "a")):
                return await message.delete()


def setup(bot: MineplexBot):
    bot.add_cog(Filter(bot))
