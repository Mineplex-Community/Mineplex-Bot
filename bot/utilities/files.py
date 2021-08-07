import json
import os
from typing import List, Union

from discord.ext.commands import AutoShardedBot, Bot


def file_type_search(directory: str, extension: str) -> List[str]:
    working_files: List[str] = []

    # Everything in each directory and subdirectory
    for current_path, directories, files in os.walk(directory):
        for file in files:
            if not file.endswith(extension):
                continue

            working_files.append(
                current_path.replace("\\", "/") + "/" + file
            )

    return working_files


def load_extensions(bot: Union[Bot, AutoShardedBot]):
    cogs: List[str] = [
        cog.replace("./", "").replace("/", ".").replace(".py", "")
        for cog in
        file_type_search('./modules', '.py')
    ]

    # Try to load each cog
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f"[COG] Loaded bot extension", f"/{cog.replace('.', '/')}.py")
        except Exception as ex:
            raise ex
            print(f"Failed to load extension", cog, f"{type(ex).__name__}: {ex}")


def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.loads(file.read())
