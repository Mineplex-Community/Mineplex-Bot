import os

import discord
import yaml
from discord.ext.commands import AutoShardedBot, Context, CommandNotFound
from discord_slash import SlashCommand

import config
from utilities.files import load_json_file, load_extensions


class MineplexBot(AutoShardedBot):

    def __init__(self, **options):
        super().__init__(config.LEGACY_PREFIX, **options)

        # Load custom items
        self.token_list: dict = load_json_file(config.TOKEN_PATH)
        self.token: str = self.token_list["bot"]
        self.slash: SlashCommand = SlashCommand(self, sync_commands=True)
        self.yaml_config: dict = yaml.safe_load(open(config.YAML_CONFIG_PATH, 'r', encoding='utf-8').read())

    @property
    def invite_link(self):
        return f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=3288853584&scope=bot%20applications.commands"


if __name__ == '__main__':
    try:
        os.chdir('bot')
    except FileNotFoundError:
        pass

    bot = MineplexBot(intents=discord.Intents.all())
    bot.remove_command('help')


    @bot.event
    async def on_command_error(context: Context, error):
        if isinstance(error, CommandNotFound):
            return

        if context.command.has_error_handler():
            return

        raise error


    load_extensions(bot)
    bot.run(bot.token)
