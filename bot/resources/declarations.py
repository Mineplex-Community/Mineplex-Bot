from discord_slash.model import SlashCommandPermissionType, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_permission, create_option

import config

declarations: dict = {
    "general": {
        "ping": {
            "name": "ping",
            "description": "Get the bot's current ping",
            "guild_ids": [config.HOME_GUILD_ID],
        },
        "pin": {
            "name": "pin",
            "description": "Pin a message by message ID",
            "guild_ids": [config.HOME_GUILD_ID],
            "permissions": {
                config.HOME_GUILD_ID: (
                        [create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.PIN_ROLES]
                )
            },
            "options": [
                create_option(
                    name="message_id",
                    description="The ID of the message to pin",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                )
            ]
        },
        "unpin": {
            "name": "unpin",
            "description": "Unpin a message by message ID",
            "guild_ids": [config.HOME_GUILD_ID],
            "permissions": {
                config.HOME_GUILD_ID: (
                        [create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.PIN_ROLES]
                )
            },
            "options": [
                create_option(
                    name="message_id",
                    description="The ID of the message to unpin",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                )
            ]
        },
        "invite": {
            "name": "invite",
            "description": "Create a custom, cat-lead friendly invite link to the Discord",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="tag",
                    description="The Discord tag of the invitee",
                    option_type=SlashCommandOptionType.STRING,
                    required=False
                ),
                create_option(
                    name="username",
                    description="The Minecraft username of the invitee",
                    option_type=SlashCommandOptionType.STRING,
                    required=False
                ),
                create_option(
                    name="hours",
                    description="The number of hours the invite should last",
                    option_type=SlashCommandOptionType.INTEGER,
                    required=False
                ),
                create_option(
                    name="uses",
                    description="The number of uses the invite should have",
                    option_type=SlashCommandOptionType.INTEGER,
                    required=False
                )
            ],
            "permissions": {
                config.HOME_GUILD_ID: (
                        [create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.INVITE_ROLES]
                )
            },
        }
    },
    "moderation": {
        "redirect": {
            "name": "redirect",
            "description": "Create a Mineplex redirect from a given URL",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="url",
                    description="The URL to create the redirect for ",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                )
            ]
        },
        "verify": {
            "name": "verify",
            "description": "Use the bot's built-in verification",
            "guild_ids": [config.HOME_GUILD_ID],
            "permissions": {
                config.HOME_GUILD_ID: [
                    create_permission(config.VERIFY_ROLE_ID, SlashCommandPermissionType.ROLE, True),
                    create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)
                ]
            }
        },
        "dblacklist": {
            "name": "dblacklist",
            "description": "Apply a blacklisted role to a given member",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="member",
                    description="The sniveling member to discussion blacklist",
                    option_type=SlashCommandOptionType.USER,
                    required=True
                )
            ],
            "permissions": {
                config.HOME_GUILD_ID: (
                        [create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.BLACKLIST_ROLES]
                )
            }
        },
        "role": {
            "tag": {
                "base": "role",
                "name": "tag",
                "description": "Tag a specific role through the bot (avoid giving the permission)",
                "guild_ids": [config.HOME_GUILD_ID],
                "options": [
                    create_option(
                        name="role",
                        description="Role to tag through the bot",
                        option_type=SlashCommandOptionType.ROLE,
                        required=True
                    )
                ]
            },
            "promote": {
                "base": "role",
                "name": "promote",
                "description": "Promote a user to a given role in the Discord",
                "guild_ids": [config.HOME_GUILD_ID],
                "options": [
                    create_option(
                        name="member",
                        description="The person to apply the role to",
                        option_type=SlashCommandOptionType.USER,
                        required=True
                    ),
                    create_option(
                        name="role",
                        description="Role to promote them to through the Bot",
                        option_type=SlashCommandOptionType.ROLE,
                        required=True
                    )
                ]
            },
            "demote": {
                "base": "role",
                "name": "demote",
                "description": "Demote a user from a given role in the Discord",
                "guild_ids": [config.HOME_GUILD_ID],
                "options": [
                    create_option(
                        name="member",
                        description="The person to take the role from",
                        option_type=SlashCommandOptionType.USER,
                        required=True
                    ),
                    create_option(
                        name="role",
                        description="Role to demote them from through the Bot",
                        option_type=SlashCommandOptionType.ROLE,
                        required=True
                    )
                ]
            },

        }

    },
    "special": {
        "recruitment": {
            "name": "recruitment",
            "description": "Recruit players to your clan or yourself to a clan",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="information",
                    description="Information to input into your recruitment post",
                    option_type=SlashCommandOptionType.STRING,
                    required=False
                )
            ]
        },
        "content": {
            "name": "content",
            "description": "Create a content submission",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="url",
                    description="The URL to create the redirect for ",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                )
            ]
        },
        "rank": {
            "name": "rank",
            "description": "Check your rank card or that of another member",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="user",
                    description="The person to check the rank card for",
                    option_type=SlashCommandOptionType.USER,
                    required=False
                )
            ],
            "permissions": {
                config.HOME_GUILD_ID: (
                        ([create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] if config.ACTIVITY_ALLOWED_ROLES else []) +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.ACTIVITY_ALLOWED_ROLES]
                )
            }
        },
        "leaderboard": {
            "name": "leaderboard",
            "description": "Check the leaderboard for this guild",
            "guild_ids": [config.HOME_GUILD_ID],
            "options": [
                create_option(
                    name="page",
                    description="The page number to check for ranking",
                    option_type=SlashCommandOptionType.INTEGER,
                    required=False
                )
            ],
            "permissions": {
                config.HOME_GUILD_ID: (
                        ([create_permission(config.HOME_GUILD_ID, SlashCommandPermissionType.ROLE, False)] if config.ACTIVITY_ALLOWED_ROLES else []) +
                        [create_permission(role_id, SlashCommandPermissionType.ROLE, True) for role_id in config.ACTIVITY_ALLOWED_ROLES]
                )
            }
        }
    }
}
