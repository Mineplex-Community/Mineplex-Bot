import discord
from discord import TextChannel, DMChannel, Invite, Member, Webhook, RequestsWebhookAdapter
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from config import *
from resources.declarations import declarations


class CreateInvite(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @cog_ext.cog_slash(**declarations["general"]["invite"])
    async def invite(self, context: SlashContext, tag: Optional[str] = None, username: Optional[str] = None, hours: Optional[int] = 1, uses: Optional[int] = 1):
        """
        Create an invite link with a set of information

        :param context: Slash Command Context
        :param tag: Discord Tag
        :param username: Username being invited
        :param hours: Hours for the invite to last
        :param uses: Number of uses for the invite
        :return: None

        """
        # Parse Values
        seconds: int = max(hours, 1) * 3600
        uses: int = max(uses, 1)

        # Create Invite        
        invite_channel: TextChannel = self.bot.get_channel(config.VERIFY_CHANNEL_ID)
        invite_object: Invite = await invite_channel.create_invite(reason=f"{context.author} Requested a user invitation", max_uses=uses, max_age=seconds)

        try:
            # Send the DM message with the invite
            dm_channel: DMChannel = await context.author.create_dm()
            await dm_channel.send(f":wave: Your Invite Link is {invite_object.url}")

            # Send the success message
            await context.send(
                embed=discord.Embed(
                    title=":sunglasses: Success! Check your DMs",
                    description=f"Created a {uses}-use, {hours} hour invite link and DM'd to you. This action has been logged in <#{config.INVITE_LOG_CHANNEL_ID}>",
                    color=EMBED_COLOUR_SUCCESS
                )
            )

            # Log the creation
            await self.__log_invite_creation(config.INVITE_LOG_CHANNEL_ID, context.author, invite_object, uses, hours)

            # Send the listing message
            if username or tag is not None:
                await self.__send_cat_lead_message(self.bot.token_list["invite_webhook"], context.author, invite_object, tag, username, uses)


        except:
            await context.send(
                embed=discord.Embed(
                    title=":x: Failed to send DM!",
                    description="Failed to send DM. Check that your DM's are enabled and try again.",
                    color=EMBED_COLOUR_ERROR
                )
            )
            return await invite_object.delete(reason=f"Failed to send to {context.author} privately, deleting.")

    @staticmethod
    async def __send_cat_lead_message(webhook_url: str, author: Member, _: Invite, tag: Optional[str], username: Optional[str], __: int):
        """
        Log the creation of the invite in the cat lead #discord-invites channel (makes our lives easier)
        
        :param webhook_url: Channel for the listing webhook
        :param author: Creator of invite
        :param tag: Discord Tag of invitee
        :param username: Minecraft username of invitee
        :return: None
        """
        webhook: Webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
        webhook.send(username=str(author), avatar_url=author.avatar_url, content=(
                "`" +
                (f"{tag} " if tag is not None else '').replace("`", "") +
                (f"({username})" if username is not None else '').replace("`", "") +
                "`"
        ))

    async def __log_invite_creation(self, log_channel: int, author: Member, invite: Invite, uses: int, hours: int):
        """
        Log an invite in the logs channel

        :param log_channel: Channel to log it in
        :param author: Person that made it
        :param invite: The invite they made
        :return: None

        """
        log_channel: TextChannel = self.bot.get_channel(log_channel)
        await log_channel.send(
            embed=discord.Embed(
                title="Bot Invite Created",
                description=f"{author.mention} created a {uses}-use {hours}-hour invite.",
                color=EMBED_COLOUR_STRD
            ).add_field(name="Invite Link:", value=invite.url)
        )


def setup(bot):
    bot.add_cog(CreateInvite(bot))
