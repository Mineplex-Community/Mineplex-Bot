import base64
import logging

import discord
from discord import Message, TextChannel, NotFound, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from resources.declarations import declarations
from utilities.miscellaneous import is_url


class LinkBypass(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @cog_ext.cog_slash(**declarations["moderation"]["redirect"])
    async def redirect(self, context: SlashContext, url: str):
        """
        Create a redirect for any URL

        :param context: Slash Context
        :param url: URL to redirect
        :return: None

        """
        if not is_url(url):
            return await context.send(f"<:{config.X_EMOJI} The provided string is not a valid URL and cannot be redirected.")

        base_64: str = bytes.decode(base64.b64encode(str.encode(url)))
        await context.send(f"<:{config.CHECK_EMOJI}> **Redirect:** https://www.mineplex.com/redirect/?to={base_64}")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Bypass link filtering when in certain channels

        :param message: Message sent
        :return: None

        """
        # Not a bypass channel or no embeds
        if int(message.channel.id) not in config.LINK_BYPASS_CHANNELS or not message.embeds:
            return

        embed_desc: str = message.embeds[0].description

        if "contained a non-whitelisted link" not in str(embed_desc):
            return

        try:
            channel_id: int = int(embed_desc.split("<#")[1].split(">")[0])
            user_id: str = embed_desc.split("<@")[1].split(">")[0]
            url: str = "https://" + embed_desc.split("(`")[1].split("`)")[0]
        except IndexError:
            return logging.warning("Failed to parse Channel ID or User ID or Filtered URL from filter message")

        # Get the channel
        try:
            channel: TextChannel = await self.bot.fetch_channel(channel_id)
            member: Member = await message.guild.fetch_member(user_id)
        except NotFound:
            return logging.warning("Failed to look up the parsed Channel or Member from filter message")

        await channel.send(
            content=f"<:{config.CHECK_EMOJI}> **Recovered Link:** {url}\n_ _",
            embed=discord.Embed(
                title="Full Message",
                description=message.embeds[0].fields[0].value,
                colour=config.EMBED_COLOUR_INVIS
            ).set_author(name=str(member), icon_url=member.avatar_url).set_thumbnail(url=channel.guild.icon_url)
        )


def setup(bot: MineplexBot):
    bot.add_cog(LinkBypass(bot))
