import logging
from typing import Dict, List

import aiohttp
import discord
from discord import Role, Member, RawReactionActionEvent, Guild
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
from bot import MineplexBot
from resources.declarations import declarations


class RoleTagging(commands.Cog):
    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

        self.taggable: Dict[int, List[int]] = self.__parse_roles_config(self.bot.yaml_config.get('taggable-roles', {}))
        self.promotable: Dict[int, List[int]] = self.__parse_roles_config(self.bot.yaml_config.get('promote-demote-roles', {}))
        self.reaction_roles: Dict[str, Dict[str, str]] = self.__reaction_roles_config(self.bot.yaml_config.get('reaction-roles', {}))

    @staticmethod
    def __reaction_roles_config(reaction_roles: dict):
        """
        Parse the role config

        :param reaction_roles: Reaction role dict
        :return: None

        """
        configuration: Dict[str, Dict[str, str]] = dict()

        for entry in reaction_roles:
            # Try to split
            try:
                role_id, message_id, emote = entry.split(";")
            except ValueError:
                continue

            # Try to add
            try:
                configuration[message_id][emote] = role_id
            except KeyError:
                configuration[message_id] = {emote: role_id}

        return configuration

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        """
        When someone adds a reaction

        :param reaction: The reaction they added
        :return: None

        """
        await self.__parse_reaction_role(reaction, True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent):
        """
        When someone removes a reaction

        :param reaction: The reaction they removed
        :return: None

        """
        await self.__parse_reaction_role(reaction, False)

    async def __parse_reaction_role(self, reaction: RawReactionActionEvent, add_role: bool):
        """
        Parse reaction roles when uses add/remove reactions to specific messages

        :param reaction: Reaction they made
        :param add_role: The role to add (if it matches one of the saved ones)
        :return: None

        """
        # Get config if one exists for message
        try:
            reactions: Dict[str, str] = self.reaction_roles[str(reaction.message_id)]
        except KeyError:
            return

        # Try to get default
        try:
            role_id: int = int(reactions[str(reaction.emoji)])
        except KeyError:
            # Try to get custom
            try:
                role_id: int = int(reactions[str(reaction.emoji)[2:-1]])
            except KeyError:
                return
        except ValueError:
            return logging.warning("Failed to update role due to badly configured Role ID (string where int expected)")

        # Get the pertinent data
        guild: Guild = self.bot.get_guild(reaction.guild_id)
        role: Role = guild.get_role(role_id)
        member: Member = guild.get_member(reaction.user_id)

        # Add Role
        if add_role and role not in member.roles:
            await member.add_roles(role)

        # Remove Role
        elif not add_role and role in member.roles:
            await member.remove_roles(role)

    @staticmethod
    def __parse_roles_config(taggable_roles: dict):
        """
        Parse the config

        :param taggable_roles: Tag roles
        :return: None

        """
        configuration: Dict[int, List[int]] = {}

        for name, value in taggable_roles.items():
            try:
                configuration[value['id']] = value.get('allowed-roles', [])
            except:
                continue

        return configuration

    @cog_ext.cog_subcommand(**declarations["moderation"]["role"]["tag"])
    async def tag(self, context: SlashContext, role: Role):
        """
        Tag a role without receiving the permission on Discord

        :param context: Slash context
        :param role: Role to tag
        :return: None

        """

        # Get roles that can tag
        allowed_roles: List[str] = [str(r_id) for r_id in self.taggable.get(role.id, [])]

        # If they aren't taggable by this person
        if not allowed_roles or not any(str(r.id) in allowed_roles for r in context.author.roles):
            return await context.send(f"<:{config.X_EMOJI}> Sorry, but you cannot tag this role.", hidden=True)

        # Send the role tag
        await context.defer(hidden=False)
        await self.__delete_original_response(context)

        try:
            await context.channel.send(role.mention)
        except discord.errors.Forbidden:
            pass

    async def __delete_original_response(self, context: SlashContext):
        """
        Delete the original deferred reply after tagging

        :param context: SlashContext
        :return: None

        """
        endpoint = f"https://discord.com/api/v9/webhooks/{self.bot.user.id}/{context._token}/messages/@original"
        headers = {f"Authorization": f"Bot {self.bot.token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(url=endpoint, headers=headers) as response:
                return await response.read()

    @cog_ext.cog_subcommand(**declarations["moderation"]["role"]["promote"])
    async def promote(self, context: SlashContext, member: Member, role: Role):
        """
        Promote a user to a given role

        :param context: Slash context
        :param member: Member to promote
        :param role: Role to promote to
        :return: None

        """
        # Get roles that can tag
        allowed_roles: List[str] = [str(r_id) for r_id in self.promotable.get(role.id, [])]

        # If they aren't demotable by this person
        if not allowed_roles or not any(str(r.id) in allowed_roles for r in context.author.roles):
            return await context.send(f"<:{config.X_EMOJI}> Sorry, but you cannot promote to this role.", hidden=True)

        # Has it already
        if role in member.roles:
            return await context.send(f"<:{config.X_EMOJI}> `{member}` already has the `{role.name}` role already!")

        # Add it
        try:
            await member.add_roles(role)
        except discord.errors.Forbidden:
            return await context.send(f"<:{config.X_EMOJI}> The Bot does not have permission to give `{role.name}` to players.")

        await context.send(
            embed=discord.Embed(
                title=f"Promote - Action Complete! Promote Player to {role.name}",
                description=f"{member.mention} has just been promoted to {role.name}",
                colour=0xe7ca12
            ).set_footer(
                icon_url=context.guild.icon_url, text=f"This action was performed by {context.author.name} ({context.author.id})"
            )
        )

    @cog_ext.cog_subcommand(**declarations["moderation"]["role"]["demote"])
    async def demote(self, context: SlashContext, member: Member, role: Role):
        """
        Demote a user from a given role

        :param context: Slash context
        :param member: Person to demote
        :param role: Role todemote from
        :return: None

        """
        # Get roles that can tag
        allowed_roles: List[str] = [str(r_id) for r_id in self.promotable.get(role.id, [])]

        # If they aren't demotable by this person
        if not allowed_roles or not any(str(r.id) in allowed_roles for r in context.author.roles):
            return await context.send(f"<:{config.X_EMOJI}> Sorry, but you cannot demote from this role.", hidden=True)

        # Doesn't have yet
        if role not in member.roles:
            return await context.send(f"<:{config.X_EMOJI}> `{member}` does not have the `{role.name}` role currently!")

        # Remove it
        try:
            await member.remove_roles(role)
        except discord.errors.Forbidden:
            return await context.send(f"<:{config.X_EMOJI}> The Bot does not have permission to take `{role.name}` from players.")

        await context.send(
            embed=discord.Embed(
                title=f"Demote - Action Complete! Demote Player from {role.name}",
                description=f"{member.mention} has just been demoted from {role.name}",
                colour=0xe7ca12
            ).set_footer(
                icon_url=context.guild.icon_url, text=f"This action was performed by {context.author.name} ({context.author.id})"
            )
        )


def setup(bot: MineplexBot):
    bot.add_cog(RoleTagging(bot))
