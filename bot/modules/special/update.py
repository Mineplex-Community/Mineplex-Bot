import json
import logging
import traceback
from typing import List, Optional

from discord import Message
from discord.ext import commands
from discord.ext.commands import Context, BucketType, CommandOnCooldown

import config
from bot import MineplexBot

# Load Config
DB_PATH: str = './resources/data/update.json'
CONFIG: dict = json.loads(open(DB_PATH, 'r').read())

# Parse Config
keywords: List[str] = CONFIG.get('keywords', [])
direction: bool = CONFIG.get('direction', True)
max_count: int = CONFIG.get('max', 100)
min_count: int = CONFIG.get('min', 0)
cooldown: int = CONFIG.get('cooldown', 0)
message: str = CONFIG.get('message', "")
change: int = CONFIG.get('change', 1)
bound_message: str = CONFIG.get('bound_message', '')


class WhenWeUpdating(commands.Cog):

    def __init__(self, bot: MineplexBot):
        self.bot: MineplexBot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        When a message is detected, try to update the count

        :param message: The message object
        :return: Ignored

        """
        # Confirm we need to update the count
        if (
                not message.guild or
                message.author.bot or
                int(message.guild.id) != config.HOME_GUILD_ID or
                message.content.lower() not in keywords
        ):
            return

        message.content = f"{config.LEGACY_PREFIX}updateReply"
        await self.bot.process_commands(message)

    @commands.command(name='updateReply')
    @commands.cooldown(1, 30, BucketType.user)
    async def update_reply(self, context: Context):
        """
        Try to update the reply message

        :param context: Message content
        :return: None

        """
        # Get Count
        count: Optional[int] = self.__get_count()
        changed: bool = False

        if count is None:
            logging.error(traceback.format_exc())

        # Change count
        if (count < max_count and direction) or (count > min_count and not direction):
            count += (change * (-1 if not direction else 1))
            self.__set_count(count)
            changed = True

        reply: str = (
                message.replace("%name%", str(context.author)).replace("%count%", str(count)).replace("%pl%", '' if count == 1 else 's')
                + (" " + bound_message if changed else '')
        )

        await context.send(reply)

    @staticmethod
    def __get_count() -> Optional[int]:
        """
        Get the current count
        :return: Count or None

        """
        try:
            return json.loads(open(DB_PATH, "r").read())["count"]
        except:
            return None

    @staticmethod
    def __set_count(count: int) -> bool:
        """
        Update the current count
        :return: Whether it succeeded or not

        """
        try:
            current: dict = json.loads(open(DB_PATH, "r").read())
        except:
            return False

        current["count"] = count
        try:
            open(DB_PATH, "w").write(json.dumps(current, indent=4))
            return True
        except:
            return False

    @update_reply.error
    async def on_update_reply_error(self, context: Context, error: Exception):
        """
        If the update command fails

        :param context: Command Context
        :param error: Reason it failed
        :return: Ignored

        """
        # Cooldown
        if isinstance(error, CommandOnCooldown):
            await context.message.delete()

            try:
                await context.message.author.create_dm()
                return await context.message.author.send(f"<:{config.X_EMOJI}>`{error}.`")
            except:
                return


def setup(bot: MineplexBot):
    return bot.add_cog(WhenWeUpdating(bot))
