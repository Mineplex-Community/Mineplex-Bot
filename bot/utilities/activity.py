from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config


def reformat_number(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def create_card(user, achieved_xp, needed_xp, rank, level, resource_path):
    status = str(user.status)
    name = user.name
    discriminator = user.discriminator
    pfp_url = str(user.avatar_url_as(format="png"))

    # DIMENSIONS
    image_width, image_height = 800, 200
    pfp_dimensions = round(image_height / 1.4)
    status_img_dimensions = round(pfp_dimensions / 4)

    # Fonts
    header_font = ImageFont.truetype(resource_path + '/card_font.ttf', 32)
    large_font = ImageFont.truetype(resource_path + '/card_font.ttf', 45)
    small_font = ImageFont.truetype(resource_path + '/card_font.ttf', 22)

    def mask_circle_transparent(pil_img, blur_radius, offset=0, border_thickness=10):
        blur_radius = 0
        offset = blur_radius * 2 + offset
        mask = Image.new("L", pil_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = pil_img.copy()
        result.putalpha(mask)

        z = Image.new('RGBA', (450, 450))
        draw = ImageDraw.Draw(z)
        draw.ellipse((0, 0, result.size[0] + border_thickness, result.size[1] + border_thickness), fill=(30, 37, 47), outline=(30, 37, 47))

        z.paste(result, (border_thickness // 2, border_thickness // 2), result)

        return z

    # Setting Up the Image
    img = Image.new('RGBA', (image_width, image_height), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    pfp = Image.open(BytesIO(requests.get(pfp_url).content))

    pfp.thumbnail((pfp_dimensions, pfp_dimensions))
    pfp = mask_circle_transparent(pfp, 3)

    pfp_border = Image.open(resource_path + '/hollow_circle.png')
    pfp_border.thumbnail((600, 600))

    # Drawing Profile Picture & Border
    pfp_offset = ((image_height // 2) - pfp_dimensions // 2)
    img.paste(pfp, (pfp_offset - 9, pfp_offset - 4))  # Drawing the profile picture mask=pfp

    # Drawing Status
    status_location = (pfp_offset + pfp_dimensions - status_img_dimensions, pfp_offset + pfp_dimensions - status_img_dimensions + 10)

    status_border = Image.open(resource_path + "/filled_circle.png")
    status_border.thumbnail(((round(status_img_dimensions * 1.2)), round(status_img_dimensions * 1.2)))
    img.paste(status_border, (round(status_location[0] * 0.97), round(status_location[1] * 0.97)), mask=status_border)

    if status == 'online':
        status_img = Image.open(resource_path + "/online.png")
        status_img.thumbnail((status_img_dimensions, status_img_dimensions))

    if status == 'idle':
        status_img = Image.open(resource_path + "/idle.png")
        status_img.thumbnail((status_img_dimensions, status_img_dimensions))

    if status == 'dnd':
        status_img = Image.open(resource_path + "/dnd.png")
        status_img.thumbnail((status_img_dimensions, status_img_dimensions))

    if status == 'offline':
        status_img = Image.open(resource_path + "/offline.png")
        status_img.thumbnail((status_img_dimensions, status_img_dimensions))

    img.paste(status_img, status_location, mask=status_img)

    achieved_xp = max(1, achieved_xp)
    needed_xp = max(1, needed_xp)

    # Drawing the progress bar
    progress_bar_width, progress_bar_height = round((image_width / 1.45)), round((image_height / 6))
    progress_bar_location = ((round(image_width - image_width / 1.38)), (round(image_height - image_height / 3.4)))

    draw.rectangle(((progress_bar_location[0], progress_bar_location[1]), (progress_bar_width + progress_bar_location[0], progress_bar_height + progress_bar_location[1])), fill=config.ACTIVITY_CARD_PROGRESS)
    draw.rectangle(((progress_bar_location[0], progress_bar_location[1]), (round(progress_bar_location[0] + ((achieved_xp / needed_xp) * progress_bar_width))), progress_bar_height + progress_bar_location[1]),
                   fill=config.ACTIVITY_CARD_PRIMARY)

    # Drawing the Discord Name & Discriminator
    if len(name) > 15:
        discord_name = name[:15]
    else:
        discord_name = name
    discord_discriminator = f"#{discriminator}"

    discord_name_length = header_font.getsize(discord_name)[0]

    draw.text((progress_bar_location[0] + 15, progress_bar_location[1] - 45), discord_name, font=header_font, fill=config.ACTIVITY_CARD_SECONDARY)
    draw.text((progress_bar_location[0] + 25 + discord_name_length, progress_bar_location[1] - 35), discord_discriminator, font=small_font, fill=config.ACTIVITY_CARD_TERTIARY)

    # Drawing the User's XP
    achieved_xp_formatted = reformat_number(achieved_xp)
    achieved_xp_length = small_font.getsize(achieved_xp_formatted)[0]

    needed_xp_formatted = f"/ {reformat_number(needed_xp)} XP"
    needed_xp_length = small_font.getsize(needed_xp_formatted)[0]
    needed_xp_location = (progress_bar_width + progress_bar_location[0] - needed_xp_length, progress_bar_location[1] - 35)

    draw.text(needed_xp_location, needed_xp_formatted, font=small_font, fill=config.ACTIVITY_CARD_TERTIARY)
    draw.text((needed_xp_location[0] - achieved_xp_length - 9, needed_xp_location[1]), achieved_xp_formatted, font=small_font, fill=config.ACTIVITY_CARD_SECONDARY)

    # Drawing the User's Level
    level_length = large_font.getsize(str(level))[0]
    level_location = (progress_bar_width + progress_bar_location[0] - level_length, 8)

    level_label_location = (level_location[0] - small_font.getsize("LEVEL")[0] - 10, 28)

    draw.text(level_label_location, "LEVEL", font=small_font, fill=config.ACTIVITY_CARD_PRIMARY)
    draw.text(level_location, str(level), font=large_font, fill=config.ACTIVITY_CARD_PRIMARY)

    # Drawing the User's Rank
    if rank is not None:
        rank_formatted = f"#{rank}"
        rank_formatted_length = large_font.getsize(rank_formatted)[0]
        rank_formatted_location = (level_label_location[0] - rank_formatted_length - 10, level_location[1])
        draw.text(rank_formatted_location, rank_formatted, font=large_font, fill=config.ACTIVITY_CARD_SECONDARY)

        rank_label_location = (rank_formatted_location[0] - small_font.getsize("RANK")[0] - 10, level_label_location[1])
        draw.text(rank_label_location, "RANK", font=small_font, fill=config.ACTIVITY_CARD_SECONDARY)

    backing_width = round(image_width * 1.05)
    backing_height = round(image_height * 1.3)

    background: Image = Image.open(BytesIO(requests.get(config.ACTIVITY_CARD_BACKGROUND_URL).content))
    background = background.resize((backing_width, backing_height))

    backing_img = Image.new('RGBA', (backing_width, backing_height), color=(255, 255, 255, 255))
    backing_img.paste(background, (0, 0))

    backing_img.paste(img, (20, 28), img)

    return backing_img
