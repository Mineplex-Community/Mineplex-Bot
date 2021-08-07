import discord
from discord import Message, NotFound
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import config
from bot import MineplexBot
from config import EMBED_COLOUR_SUCCESS, CHECK_EMOJI
from resources.declarations import declarations


class Pinning(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @cog_ext.cog_slash(**declarations["general"]["pin"])
    async def pin(self, context: SlashContext, message_id: int):
        """
        Pin a message

        :param context: Slash context
        :param message_id: Message ID
        :return: None

        """
        message: Message = await context.channel.fetch_message(int(message_id))
        await message.pin(reason=f"User {context.author} unpinned through Bot")

        await context.send(
            embed=discord.Embed(
                description=f"<:{CHECK_EMOJI}> Successfully pinned message `{message_id}` in {message.channel.mention}.",
                color=EMBED_COLOUR_SUCCESS
            ).set_author(name=f"{context.author}", icon_url=context.author.avatar_url)
        )

    @cog_ext.cog_slash(**declarations["general"]["unpin"])
    async def unpin(self, context: SlashContext, message_id: int):
        """
        Unpin a message

        :param context: Slash Context
        :param message_id: Message ID
        :return: None

        """
        message: Message = await context.channel.fetch_message(message_id)
        await message.unpin(reason=f"User {context.author} unpinned through Bot")

        await context.send(
            embed=discord.Embed(
                description=f"<:{CHECK_EMOJI}> Successfully unpinned message `{message_id}` in {message.channel.mention}.",
                color=EMBED_COLOUR_SUCCESS
            ).set_author(name=f"{context.author}", icon_url=context.author.avatar_url)
        )

    @unpin.error
    @pin.error
    async def on_pinning_error(self, context: SlashContext, error: Exception):
        """
        On failed pin

        :param context: Slash Context
        :param error: Error raised
        :return: None

        """
        if isinstance(error, NotFound) or isinstance(error, ValueError):
            return await context.send(f"<:{config.X_EMOJI}> A message with the given ID does not exist in this channel.", hidden=True)

        await context.send(f"<:{config.X_EMOJI}> Unexpected error when pinning message, contact bot creator.", hidden=True)
        raise error


def setup(bot: MineplexBot):
    bot.add_cog(Pinning(bot))
