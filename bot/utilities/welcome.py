from io import BytesIO

import requests
from PIL import ImageFont, Image, ImageDraw
from discord import Member


def create_welcome(member: Member, resource_path: str) -> Image:
    pfp = str(member.avatar_url)
    discord_name = str(member.name)
    discord_name = discord_name[:12] if len(discord_name) > 15 else discord_name

    image_width, image_height = 800, 200
    header_font = ImageFont.truetype(resource_path + '/welcome_font.ttf', 35)

    img = Image.new('RGBA', (image_width, image_height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pfp_dimensions = round(image_height / 1.2)

    pfp = Image.open(BytesIO(requests.get(pfp).content))
    pfp.thumbnail((pfp_dimensions, pfp_dimensions))

    img.paste(pfp, (30, int(image_height / 2 - pfp_dimensions / 2)))  # Drawing the profile picture mask=pfp

    count: str = str(member.guild.member_count) + {1: 'st', 2: 'nd', 3: 'rd'}.get(member.guild.member_count, "th")

    formatted_text = f"Welcome, {discord_name} to\n{str(member.guild.name)}!\nYou are the {count} member. "
    draw.text((250, 38), formatted_text, font=header_font, fill='white')

    return img
