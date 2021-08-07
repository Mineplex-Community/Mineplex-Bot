import discord
from discord import Message, TextChannel, Reaction, Embed, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from config import *
from resources.declarations import declarations
from utilities.miscellaneous import is_url


class DiscussionBlacklist(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @cog_ext.cog_slash(**declarations["special"]["content"])
    async def content(self, context: SlashContext, url: str):
        """
        Content submission command

        :param context: Slash context
        :param url: URL of the video
        :return: None

        """
        if not is_url(url):
            return await context.send(f"<:{config.X_EMOJI}> Please send a valid YouTube video URL.")

        # Pending Channel
        channel: TextChannel = self.bot.get_channel(config.CONTENT_CHANNEL_ID)
        message: Message = await channel.send(
            embed=discord.Embed(
                description=f"<{SEARCHING_EMOJI}> `Pending Submission`\n_ _", color=EMBED_COLOUR_STRD
            ).set_author(
                name=f"{context.author} ({context.author.id})", icon_url=context.author.avatar_url
            ).add_field(
                name="**Link URL**", value=f"{url}"
            )
        )
        await message.add_reaction(CHECK_EMOJI)
        await message.add_reaction(X_EMOJI)

        # Success Message
        await context.send(
            embed=discord.Embed(
                description=f"<:{CHECK_EMOJI}> Your content submission was successfully sent.", color=EMBED_COLOUR_SUCCESS
            ).set_author(name=f"{context.author.name}#{context.author.discriminator}", icon_url=context.author.avatar_url)
        )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, member: Member):
        """
        When someone adds a reaction

        :param reaction: Reaction added to the message
        :param member: User that added the message
        :return: None

        """
        channel: TextChannel = self.bot.get_channel(config.CONTENT_SEND_CHANNEL_ID)

        message: Message = reaction.message
        x_stringified: str = f"<:{config.X_EMOJI}>"
        check_stringified: str = f"<:{config.CHECK_EMOJI}>"

        # Not the right reaction
        if str(reaction) not in [check_stringified, x_stringified] or member.bot:
            return

        # No permissions? Remove their reaction and yeet it
        if not any(role.id in config.CONTENT_PROCESS_ROLES for role in member.roles):
            return await message.remove_reaction(reaction, member)

        # Not one of our embeds
        if (
                not message.embeds or
                len(message.embeds[0].fields) < 1 or
                message.embeds[0].fields[0].name != "**Link URL**"
        ):
            return

        embed: Embed = message.embeds[0]
        embed_dict: dict = embed.to_dict()

        if 'Pending Submission' not in embed.description:
            return

        if str(reaction) == check_stringified:
            embed_dict["color"] = config.EMBED_COLOUR_SUCCESS
            embed_dict['description'] = f"<:{CHECK_EMOJI}> `Accepted Submission`\n_ _"

        else:
            embed_dict["color"] = config.EMBED_COLOUR_ERROR
            embed_dict['description'] = f"<:{X_EMOJI}> `Rejected Submission`\n_ _"

        embed: Embed = Embed.from_dict(embed_dict)
        embed.add_field(
            name="Processed By",
            value=member.mention,
            inline=False
        )

        # Process everything all at once ;)
        await message.edit(embed=embed), await message.clear_reactions(), await channel.send(embed.fields[0].value)


def setup(bot: MineplexBot):
    bot.add_cog(DiscussionBlacklist(bot))
