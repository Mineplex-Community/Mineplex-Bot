import discord
from discord import Role, User, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from resources.declarations import declarations


class DiscussionBlacklist(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @cog_ext.cog_slash(**declarations["moderation"]["dblacklist"])
    async def dblacklist(self, context: SlashContext, member: User):
        """
        Blacklist a user (add the blacklist role to them)

        :param context: Slash context
        :param member: Person to blacklist
        :return: None

        """
        role: Role = context.guild.get_role(config.BLACKLIST_ROLE_ID)
        member: Member = await context.guild.fetch_member(member.id)

        # If they are already blacklisted
        if role in member.roles:
            await member.remove_roles(role)
            await context.send(
                embed=discord.Embed(
                    description=f"<:{config.CHECK_EMOJI}> {member.mention} has been `unblacklisted` successfully.",
                    color=config.EMBED_COLOUR_SUCCESS
                ).set_author(name=str(context.author), icon_url=context.author.avatar_url)
            )

        # If they are not blacklisted
        else:
            await member.add_roles(role)
            await context.send(
                embed=discord.Embed(
                    description=f"<:{config.CHECK_EMOJI}> {member.mention} has been `blacklisted` successfully.",
                    color=config.EMBED_COLOUR_SUCCESS
                ).set_author(name=str(context.author), icon_url=context.author.avatar_url)
            )


def setup(bot: MineplexBot):
    bot.add_cog(DiscussionBlacklist(bot))
