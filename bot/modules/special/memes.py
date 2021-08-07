from discord import Message
from discord.ext import commands

import config
from bot import MineplexBot


class Memes(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        When someone sends a message

        :param message: The message they sent
        :return: None

        """
        # Validate Message
        if (
                (int(message.channel.id) not in config.MEME_CHANNEL_IDS) or
                message.author.bot or
                (len(message.embeds) < 1 and len(message.attachments) < 1)
        ):
            return

        # Add Reactions
        await message.add_reaction(config.MEME_UPVOTE_EMOJI), await message.add_reaction(config.MEME_DOWN_VOTE_EMOJI)


def setup(bot: MineplexBot):
    bot.add_cog(Memes(bot))
