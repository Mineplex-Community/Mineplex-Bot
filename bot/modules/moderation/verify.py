import asyncio
from typing import Optional

import discord
from discord import TextChannel, Member
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from resources.declarations import declarations


class BackupVerification(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot
        self.channel: Optional[TextChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Get the text channel to prep for channel use
        :return:

        """
        self.channel: TextChannel = self.bot.get_channel(config.VERIFY_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """
        When the bot switches between online & offline

        :param before:
        :param after:
        :return:

        """

        # If not ready yet
        if not self.channel:
            return

        # Fetch the member
        mineplex: Member = self.channel.guild.get_member(config.VERIFY_MAIN_BOT_ID)

        # If it's our bot
        if after.id == int(mineplex.id) and int(after.guild.id) == int(self.channel.guild.id):
            # Online -> Offline
            if after.status == discord.Status.offline and before.status != discord.Status.offline:
                await self.channel.send(
                    embed=discord.Embed(
                        title=f"The silly ({mineplex.name}) Bot just went offline. This bot has taken over verification functions temporarily as of now.",
                        color=config.EMBED_COLOUR_ERROR
                    )
                )

            # Offline -> Online
            if before.status == discord.Status.offline and after.status != discord.Status.offline:
                await self.channel.send(
                    embed=discord.Embed(
                        title=f"The slacker ({mineplex.name}) Bot is now back online. Verification disabled.",
                        color=config.EMBED_COLOUR_SUCCESS
                    )
                )

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        When someone joins the server

        :param member: Person that joined
        :return: None

        """

        # If not ready yet
        if not self.channel:
            return

        mineplex: Member = self.channel.guild.get_member(config.VERIFY_MAIN_BOT_ID)

        # Confirm correct circumstances
        if not int(member.guild.id) == int(self.channel.guild.id) or mineplex.status != discord.Status.offline:
            return

        # Add verify role
        await member.add_roles(member.guild.get_role(config.VERIFY_ROLE_ID))

        welcome_embed = discord.Embed(
            title=f":wave: Welcome to the {member.guild.name} Discord!",
            description=f"Hey <@{member.id}>, and welcome to the {member.guild.name} Discord!\n\n"
                        f"Please **read over** the information provided in the visible channels. "
                        f"When you are done, type `!agree`, `!verify`, or `!join` to verify.\n\n"
                        f"Hope you enjoy your stay!\n\n"
                        f"**~ Being better than the Mineplex bot EST 2020**",
            color=config.VERIFY_EMBED_COLOR
        )

        await self.channel.send(content=f"Welcome <@{member.id}>!", embed=welcome_embed)

    @cog_ext.cog_slash(**declarations["moderation"]["verify"])
    async def verify(self, context: SlashContext):
        """
        When a member wants to verify

        :param context: Slash context
        :return: None

        """

        # If not ready yet
        if not self.channel:
            return

        mineplex: Member = self.channel.guild.get_member(config.VERIFY_MAIN_BOT_ID)

        # Mineplex Bot online
        if mineplex.status == discord.Status.offline:
            return await context.send(f"<:{config.X_EMOJI}> The Mineplex bot is online! Please use the `!agree <code>` command instead.")

        # Incorrect channel
        if context.channel.id != config.VERIFY_CHANNEL_ID:
            return await context.send(f"<:{config.X_EMOJI}> This is the incorrect channel for verification!")

        # Send message
        await context.send(
            embed=discord.Embed(
                title="Confirmation: You did it! :sunglasses:",
                description=(
                    f"<@{context.author.id}>, you have successfully **verified!**\n\n"
                    f"You will have access to our Discord momentarily. "
                    f"Click one of the channels to start chatting, and remember: **Memes are key to your survival.**\n\n"
                    f"Hope you enjoy your stay!"
                ),
                color=config.VERIFY_EMBED_COLOR
            )
        )

        # Sleep, then give roles
        await asyncio.sleep(3)
        await context.author.remove_roles(context.guild.get_role(config.VERIFY_ROLE_ID))
        await context.author.add_roles(context.guild.get_role(config.VERIFY_PLAYER_ROLE_ID))


def setup(bot: MineplexBot):
    bot.add_cog(BackupVerification(bot))
